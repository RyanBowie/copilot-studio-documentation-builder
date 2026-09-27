import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
import struct
import zlib


MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "validate_release.py"
SPEC = importlib.util.spec_from_file_location("release", MODULE_PATH)
release = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(release)


class ReleaseTests(unittest.TestCase):
    def assert_modified_public_copy_rejected(self, mutate, message):
        root = MODULE_PATH.parent.parent
        manifest = json.loads((root / "release-manifest.json").read_text())
        spec = next(asset for asset in manifest["assets"] if asset.get("kind") == "public-release-copy")
        with zipfile.ZipFile(root / spec["path"]) as original:
            parts = {name: original.read(name) for name in original.namelist()}
        mutate(parts, spec)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / Path(spec["path"]).name
            with zipfile.ZipFile(path, "w") as archive:
                for name, data in parts.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(release.ReleaseError, message):
                release.check_office(path, spec)

    @staticmethod
    def replace_label_record(parts, spec, mutate):
        tree = ET.fromstring(parts[release.LABEL_PART])
        mutate(tree)
        parts[release.LABEL_PART] = ET.tostring(tree)
        spec["publicSensitivityLabel"]["sha256"] = release.digest(parts[release.LABEL_PART])

    def test_private_markers_fail_without_echoing_values(self):
        values = [
            "demo" + "@" + "example.test",
            "C:" + "\\Users\\" + "example\\private.txt",
            "https://" + "demo.sharepoint.com/private",
            "ws:" + "//127.0.0.1:1234",
            "?" + "sig" + "=" + "not-a-real-signature",
            "Bearer " + "not-a-real-credential",
            "00000000" + "-1111-2222-3333-" + "444444444444",
        ]
        for value in values:
            with self.subTest(value_type=values.index(value)):
                with self.assertRaises(release.ReleaseError) as context:
                    release.scan_text(value, "fixture")
                self.assertNotIn(value, str(context.exception))

    def test_safe_public_text(self):
        release.scan_text("Cost UNKNOWN. https://learn.microsoft.com/microsoft-copilot-studio/", "fixture")

    def test_path_traversal_and_absolute_paths_fail(self):
        for value in ("../secret", "/secret", "docs/../secret", "C:/secret", "docs\\secret", "./docs/index.html"):
            with self.assertRaises(release.ReleaseError):
                release.safe_path(value)

    def test_missing_fragment_and_artifact_escape_fail(self):
        pages = {"docs/index.html": release.Page('<h1 id="overview">Title</h1>')}
        allowed = {"docs/index.html", "README.md"}
        release.resolve_link("docs/index.html", "#overview", allowed, pages)
        for link in ("#missing", "../README.md", "/index.html", "missing.html", "javascript:alert(1)"):
            with self.assertRaises(release.ReleaseError):
                release.resolve_link("docs/index.html", link, allowed, pages)

    def test_duplicate_ids_and_missing_alt_fail(self):
        for html in ('<p id="a"></p><p id="a"></p>', '<img src="x.png">'):
            with self.assertRaises(release.ReleaseError):
                release.Page(html)

    def test_office_field_ids_are_not_tenant_ids(self):
        value = "00000000" + "-1111-2222-3333-" + "444444444444"
        field = ET.fromstring(f'<a:fld xmlns:a="{release.DRAW_NS}" id="{value}"/>')
        release.check_office_identifiers(field, "fixture")
        with self.assertRaises(release.ReleaseError):
            release.check_office_identifiers(ET.fromstring(f'<owner id="{value}"/>'), "fixture")

    def test_all_office_parts_are_inspected_for_labels(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "labelled.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")
                archive.writestr("_rels/.rels", "<Relationships/>")
                archive.writestr("ppt/presentation.xml", "<presentation/>")
                archive.writestr("docMetadata/LabelInfo.xml", '<labelList><label enabled="1"/></labelList>')
            with self.assertRaisesRegex(release.ReleaseError, "metadata"):
                release.check_office(path, {"slides": 0})

    def test_external_relationship_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "external.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")
                archive.writestr("ppt/presentation.xml", "<presentation/>")
                archive.writestr("_rels/.rels", f'<Relationships xmlns="{release.REL_NS}"><Relationship Id="rId1" Target="https://example.test/" TargetMode="External"/></Relationships>')
            with self.assertRaisesRegex(release.ReleaseError, "external relationship"):
                release.check_office(path, {"slides": 0})

    def test_public_label_exception_rejects_other_asset_kinds(self):
        self.assert_modified_public_copy_rejected(
            lambda parts, spec: spec.update(kind="authored-template"), "restricted to two reviewed copies")

    def test_public_label_exception_rejects_other_filenames(self):
        self.assert_modified_public_copy_rejected(
            lambda parts, spec: spec.update(path="docs/downloads/Unreviewed-PUBLIC.pptx"),
            "restricted to two reviewed copies")

    def test_public_label_record_must_match_exact_hash(self):
        self.assert_modified_public_copy_rejected(
            lambda parts, spec: parts.update({release.LABEL_PART: parts[release.LABEL_PART] + b" "}),
            "metadata checksum")

    def test_public_label_rejects_rehashed_history_and_attributes(self):
        for change, message in (
            (lambda tree: ET.SubElement(tree, f"{{{release.LABEL_NS}}}label"), "label history"),
            (lambda tree: tree[0].set("contentBits", "8"), "attributes changed"),
            (lambda tree: tree[0].set("owner", "unreviewed"), "attributes changed"),
        ):
            with self.subTest(message=message):
                self.assert_modified_public_copy_rejected(
                    lambda parts, spec: self.replace_label_record(parts, spec, change), message)

    def test_public_label_rejects_rehashed_policy_identifier(self):
        value = "{" + "00000000" + "-1111-2222-3333-" + "444444444444" + "}"
        self.assert_modified_public_copy_rejected(
            lambda parts, spec: self.replace_label_record(parts, spec, lambda tree: tree[0].set("id", value)),
            "unreviewed Public policy identifier")

    def test_public_label_does_not_allow_identifiers_elsewhere(self):
        def mutate(parts, spec):
            tree = ET.fromstring(parts["ppt/slides/slide1.xml"])
            tree.set("owner", "00000000" + "-1111-2222-3333-" + "444444444444")
            parts["ppt/slides/slide1.xml"] = ET.tostring(tree)
        self.assert_modified_public_copy_rejected(mutate, "identifier outside reviewed Office format fields")

    def test_public_copy_rejects_personal_authorship(self):
        def mutate(parts, spec):
            tree = ET.fromstring(parts["docProps/core.xml"])
            tree.find("{http://purl.org/dc/elements/1.1/}creator").text = "Unreviewed author"
            parts["docProps/core.xml"] = ET.tostring(tree)
        self.assert_modified_public_copy_rejected(mutate, "unreviewed personal metadata")

    def test_public_copy_rejects_other_metadata_parts(self):
        self.assert_modified_public_copy_rejected(
            lambda parts, spec: parts.update({"docMetadata/Other.xml": b"<metadata/>"}),
            "unreviewed metadata")

    def test_public_label_reference_cannot_be_missing(self):
        def mutate(parts, spec):
            tree = ET.fromstring(parts["_rels/.rels"])
            for child in list(tree):
                if child.get("Type") == release.LABEL_REL:
                    tree.remove(child)
            parts["_rels/.rels"] = ET.tostring(tree)
        self.assert_modified_public_copy_rejected(mutate, "classification relationship")

    def test_active_content_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "active.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", "<Types/>")
                archive.writestr("_rels/.rels", "<Relationships/>")
                archive.writestr("ppt/presentation.xml", "<presentation/>")
                archive.writestr("ppt/vbaProject.bin", b"not executable")
            with self.assertRaisesRegex(release.ReleaseError, "active-content"):
                release.check_office(path, {"slides": 0})

    def test_unreviewed_unused_override_is_blocked(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dangling.pptx"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("[Content_Types].xml", '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"><Override PartName="/absent.xml"/></Types>')
                archive.writestr("_rels/.rels", "<Relationships/>")
                archive.writestr("ppt/presentation.xml", "<presentation/>")
            with self.assertRaisesRegex(release.ReleaseError, "unreviewed dangling"):
                release.check_office(path, {"slides": 0})

    def test_png_metadata_and_crc_are_checked(self):
        def chunk(kind, body):
            return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
        png += chunk(b"tEXt", b"unreviewed metadata")
        with self.assertRaisesRegex(release.ReleaseError, "metadata chunk"):
            release.check_png(png, "fixture")
        with self.assertRaisesRegex(release.ReleaseError, "CRC"):
            release.check_png(png[:-1] + bytes([png[-1] ^ 1]), "fixture")

    def test_reviewed_png_software_does_not_allow_other_text(self):
        def chunk(kind, body):
            return struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body) & 0xFFFFFFFF)
        for body in (b"Software\x00Figma", b"Software\x00Figma plus unreviewed text", b"Author\x00Figma"):
            png = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0))
            png += chunk(b"tEXt", body) + chunk(b"IDAT", zlib.compress(b"\x00\x00\x00\x00")) + chunk(b"IEND", b"")
            with self.subTest(body=body):
                if body == b"Software\x00Figma":
                    release.check_png(png, "fixture", reviewed_software="Figma")
                    with self.assertRaisesRegex(release.ReleaseError, "metadata chunk"):
                        release.check_png(png, "fixture")
                else:
                    with self.assertRaisesRegex(release.ReleaseError, "metadata chunk"):
                        release.check_png(png, "fixture", reviewed_software="Figma")

    def test_stage_refuses_nonempty_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / ".pages-artifact"
            target.mkdir()
            (target / "unreviewed.txt").write_text("do not merge")
            with self.assertRaisesRegex(release.ReleaseError, "new or empty"):
                release.stage(root, target, [])
            self.assertTrue((target / "unreviewed.txt").exists())

    def test_prepared_release(self):
        site_files = release.validate()
        self.assertIn("docs/index.html", site_files)
        self.assertTrue(all(name.startswith("docs/") for name in site_files))


if __name__ == "__main__":
    unittest.main()
