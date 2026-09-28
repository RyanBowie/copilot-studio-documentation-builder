import importlib.util
from html import unescape
import json
from pathlib import Path
import re
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

    def test_reference_palette_overrides_both_foundation_themes(self):
        html = (MODULE_PATH.parent.parent / "docs" / "index.html").read_text(encoding="utf-8")
        rules = re.findall(r'(:root|html\[data-theme="dark"\])\s*\{([^}]+)\}', html)
        self.assertEqual([selector for selector, _ in rules], [":root", 'html[data-theme="dark"]'] * 2)
        for (_, rule), expected in zip(rules[2:], [
            {"bg": "#f2f2f8", "surface": "#ffffff", "text": "#102631", "text-muted": "#52637a",
             "accent": "#7653ae", "accent-hover": "#58378b", "link": "#066bc7",
             "chart-blue": "#0877dd", "chart-purple": "#7653ae", "chart-magenta": "#b535c3"},
            {"bg": "#171717", "surface": "#1f1f1f", "text": "#f2f2f2", "text-muted": "#bdbdbd",
             "accent": "#c3a0ef", "accent-hover": "#debeff", "link": "#80baff",
             "chart-blue": "#69aeff", "chart-purple": "#bc98ed", "chart-magenta": "#ed8fea"},
        ]):
            values = dict(re.findall(r"--cp-([\w-]+):\s*([^;]+);", rule))
            for name, value in expected.items():
                self.assertEqual(values[name], value)
            self.assertEqual(values["shadow"], "0 0 2px rgba(0, 0, 0, 0.12), 0 1px 2px rgba(0, 0, 0, 0.14)")

    def test_default_dark_override_precedes_rendering(self):
        html = (MODULE_PATH.parent.parent / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="en" data-theme="dark">', html)
        scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
        self.assertEqual(len(scripts), 2)
        self.assertIn('window.matchMedia("(prefers-color-scheme: dark)")', scripts[0])
        self.assertIn('explicit === "light" ? "light" : "dark"', scripts[1])
        self.assertLess(html.index(scripts[1]), html.index("<style>"))

    def test_reviewed_public_content_and_transcript_pins(self):
        docs = MODULE_PATH.parent.parent / "docs"
        html = (docs / "index.html").read_text(encoding="utf-8")
        body = re.search(r"<body>.*</body>", html, re.S).group()
        self.assertEqual(release.digest(body.encode()), "a6e66aafd60f107e669a0beca68c48ee0a18f2ddec5dbcbc88a709b0a5135914")
        transcripts = {
            "cats-and-dogs-transcript.txt": "135cd23aa6093fd8beab3a98851efc1253e374a895d7f671c0d5195fe752ed10",
            "original-word-conversations.txt": "633d135e4e78977b5fa93c2266cd1015e7e2d003b4cce0e75b980cb74c192abb",
            "original-powerpoint-conversations.txt": "a611980eca847fa2b40a4e270a530d3b98d70b2bfdb779229915c49ce8dde7ee",
        }
        for name, expected in transcripts.items():
            self.assertEqual(release.digest((docs / "downloads" / name).read_text(encoding="utf-8").encode()), expected)

    def test_harness_focused_titles(self):
        html = (MODULE_PATH.parent.parent / "docs" / "index.html").read_text(encoding="utf-8")
        headings = re.findall(r"<h1\b[^>]*>(.*?)</h1>", html, re.S)
        self.assertEqual(len(headings), 1)
        heading = " ".join(unescape(re.sub(r"<[^>]+>", " ", headings[0])).split())
        self.assertEqual(heading, "Template-aligned documents in Copilot Studio\u2019s Standard and GitHub Copilot harnesses")
        self.assertIn("<br>", headings[0])
        self.assertIn("<span>", headings[0])
        title = unescape(re.search(r"<title>(.*?)</title>", html, re.S).group(1))
        self.assertEqual(title, "Standard and GitHub Copilot harnesses | Copilot Studio")

    def test_prepared_word_boundary_and_maker_guidance(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        boundary = re.search(r'<div id="word-template-boundary".*?</div>', html, re.S).group()
        self.assertIn("Can I use my own Word template?", boundary)
        self.assertNotIn("<details", boundary)
        self.assertNotIn(" hidden", boundary)
        self.assertIn("not a one-step", boundary)
        self.assertIn("upload any DOCX and follow its layout", boundary)
        card = re.search(r'<article id="standard-word".*?</article>', html, re.S).group()
        self.assertIn("previously prepared Word layout", card)
        self.assertIn("onboarded by a maker first", card)
        implementation = re.search(r'<article id="prepared-word".*?</article>', html, re.S).group()
        sources = [
            implementation,
            (root / "README.md").read_text(encoding="utf-8"),
            (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8"),
        ]
        for source in sources:
            text = " ".join(unescape(re.sub(r"<[^>]+>", " ", source)).split())
            for phrase in ("uniquely named", "repeating sections", "drafting schema",
                           "population mappings", "template/version", "required fields and rows",
                           "Populate a Microsoft Word template", "setup/engineering work"):
                self.assertIn(phrase, text)
            self.assertIn("https://learn.microsoft.com/en-us/connectors/wordonlinebusiness/", source)
        self.assertIn("not a product-wide restriction", boundary)
        self.assertIn("Separate ad-hoc-template experiment:", html)
        self.assertIn("incomplete 3-page/3-table document", html)

    def test_cost_section_removed_without_erasing_operational_evidence(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        page = release.Page(html)
        self.assertNotIn("cost", page.ids)
        self.assertNotIn("cost-title", page.ids)
        self.assertTrue(all("#cost" not in link for link in page.links))
        for source in (html, readme):
            for removed in ("826.67", "credits /", "billing-credit-overview", "analytics-overview",
                            "Cost &amp; limits", "| Cost |", 'aria-labelledby="cost-title"'):
                self.assertNotIn(removed, source)
        for retained in ("all nine ran after the stop", "Not compliant sequential metering",
                         "32 instructional paragraphs remain", "five template instructions remain",
                         "nesting depth 9 exceeds", "Human review is part of the workflow.",
                         "Target import: not started. Target runtime: not verified."):
            self.assertIn(retained, html)
        self.assertIn("deployment, costs and document generation", html)

    def test_prepared_word_screenshots_match_the_two_verified_sources(self):
        root = MODULE_PATH.parent.parent
        manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
        previews = [asset for asset in manifest["assets"] if asset["kind"] == "word-page-preview"]
        template_hash = "00486f3d164344c68f6b5a3f100c18c77e9c7c80f701cfa7e0d54ca3078c339c"
        output_hash = "30426cf84a301fd35de6c145f505c8f0544f3fbdff49f039ad709efe7cb8d1e0"
        expected = {
            "prepared-word-template-page-01.png": (template_hash, 1, 6),
            "prepared-word-template-page-02.png": (template_hash, 2, 6),
            "prepared-word-output-page-01.png": (output_hash, 1, 10),
            "prepared-word-output-page-03.png": (output_hash, 3, 10),
        }
        self.assertEqual({Path(asset["path"]).name for asset in previews}, set(expected))
        for asset in previews:
            self.assertEqual((asset["sourceSha256"], asset["sourcePage"], asset["nativePageCount"]),
                             expected[Path(asset["path"]).name])
            self.assertEqual((asset["width"], asset["height"]), (1600, 2263))
            self.assertEqual(release.digest((root / asset["path"]).read_bytes()), asset["sha256"])
        evidence = manifest["preparedWordPreview"]
        self.assertEqual(evidence["historicalDate"], "2026-09-24")
        self.assertEqual(evidence["historicalOutput"]["sha256"], output_hash)
        self.assertEqual(evidence["historicalOutput"]["pages"], 10)
        self.assertEqual(evidence["historicalOutput"]["tables"], 6)
        self.assertEqual([(pair["templatePage"], pair["outputPage"]) for pair in evidence["pagePairs"]],
                         [(1, 1), (2, 3)])
        self.assertIn("Private", evidence["historicalOutput"]["binaryAvailability"])
        self.assertFalse(any(asset["sha256"] == output_hash for asset in manifest["assets"]))
        self.assertEqual(len(manifest["assets"]), 14)
        self.assertEqual(len(manifest["sourceFiles"]) + len(manifest["assets"]), 28)

    def test_word_previews_are_visible_clickable_and_qualified(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        preview = re.search(r'<section id="prepared-word-preview".*?</section>', html, re.S).group()
        self.assertNotIn("<details", preview)
        self.assertNotIn(" hidden", preview)
        self.assertEqual(preview.count("<figure>"), 4)
        images = re.findall(r'<a href="([^"]+)"><img [^>]*src="([^"]+)"[^>]*></a>', preview)
        self.assertEqual(len(images), 4)
        for full_size, image in images:
            self.assertEqual(full_size, image)
            self.assertTrue(image.startswith("assets/prepared-word-") and image.endswith(".png"))
        card = re.search(r'<article id="standard-word".*?</article>', html, re.S).group()
        self.assertIn('href="#prepared-word-preview"', card)
        for phrase in ("template page 2 and output page 3", "10 native pages and 6 tables",
                       "two authorised drafting calls", "one separately confirmed document creation",
                       "Fresh native Word renders of the unchanged historical files",
                       "page numbering recalculated by Word", "output DOCX and intermediate PDFs remain private",
                       "Representative pages, not complete quality proof", "inferred queue/topic",
                       "REQ-01 through REQ-04", "separate 3-page/3-table ad-hoc"):
            self.assertIn(phrase, preview)
        self.assertIn("#prepared-word-preview", (root / "README.md").read_text(encoding="utf-8"))
        self.assertIn("#prepared-word-preview",
                      (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8"))

    @staticmethod
    def native_solution():
        root = MODULE_PATH.parent.parent
        manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
        spec = next(asset for asset in manifest["assets"] if asset["kind"] == "native-solution-export")
        return root / spec["path"], spec

    def test_native_solution_exact_archive_and_decoded_schemas(self):
        path, spec = self.native_solution()
        release.check_native_solution(path, spec)
        self.assertEqual(spec["bytes"], 185544)
        self.assertEqual(spec["members"], 92)
        self.assertEqual(spec["components"], {"bots": 2, "botComponents": 39, "flows": 5,
                         "models": 3, "configurations": 6, "connectionReferences": 3, "environmentVariables": 0})
        self.assertEqual([item["bytes"] for item in spec["decodedSpecifications"]], [793, 1660, 3545])
        self.assertEqual(spec["targetImportStatus"], "NOT_STARTED")
        self.assertEqual(spec["targetRuntimeStatus"], "NOT_VERIFIED")

    def test_native_solution_exception_is_not_a_generic_zip_allowance(self):
        path, spec = self.native_solution()
        for key, value in (("kind", "authored-template"), ("path", "docs/downloads/unreviewed.zip")):
            altered = dict(spec, **{key: value})
            with self.assertRaisesRegex(release.ReleaseError, "restricted to the reviewed export"):
                release.check_native_solution(path, altered)

    def test_native_solution_rejects_changed_bytes_even_with_new_manifest_hash(self):
        path, spec = self.native_solution()
        altered = path.read_bytes() + b"unreviewed"
        with tempfile.TemporaryDirectory() as directory:
            copy = Path(directory) / path.name
            copy.write_bytes(altered)
            spec.update(sha256=release.digest(altered), bytes=len(altered))
            with self.assertRaisesRegex(release.ReleaseError, "exact approved native ZIP"):
                release.check_native_solution(copy, spec)

    def test_native_solution_rejects_changed_review_pins(self):
        path, spec = self.native_solution()
        for key, value in (("memberInventorySha256", "0" * 64),
                           ("reviewedMetadataSha256", "0" * 64),
                           ("decodedSpecifications", []), ("components", {})):
            with self.subTest(pin=key), self.assertRaises(release.ReleaseError):
                release.check_native_solution(path, dict(spec, **{key: value}))

    def test_native_solution_download_and_setup_boundaries(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        card = re.search(r'<article id="native-solution".*?</article>', html, re.S).group()
        self.assertIn(f'href="{release.NATIVE_SOLUTION_PATH.removeprefix("docs/")}" download', card)
        self.assertEqual(len(re.findall(r"<a\b[^>]*\bdownload(?:\s|>)", html)), 10)
        for phrase in ("Target import: not started", "Target runtime: not verified",
                       "98,985-byte template", "not compatible", "No environment variables"):
            self.assertIn(phrase, card)
        guide = (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8")
        for phrase in ("### 1. Native import", "### 2. Connector binding", "### 3. Source-resource retargeting",
                       "### 4. Required template assets", "### 5. Prompt readiness",
                       "### 6. Activation, agent publishing and acceptance", "PublishWorkflows=false",
                       "12,629-byte", "14,564-byte", "zero environment variables",
                       "7c5858479154c2c5d20a2e8c636faddd252c90fbcd97acd209fa13880e21916b"):
            self.assertIn(phrase, guide)
        self.assertNotIn("No tenant-bound topics, connections, solution ZIPs or deployable flows", html)


if __name__ == "__main__":
    unittest.main()
