import importlib.util
from html import unescape
from html.parser import HTMLParser
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
        self.assertEqual([selector for selector, _ in rules[:2]], [":root", 'html[data-theme="dark"]'])
        for (_, rule), expected in zip(rules[:2], [
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
        self.assertEqual(html.count("/* design-layer:start */"), 1)
        self.assertEqual(html.count("/* design-layer:end */"), 1)
        design = re.search(r"/\* design-layer:start \*/(.*?)/\* design-layer:end \*/", html, re.S).group(1)
        self.assertNotRegex(design, r"#[0-9a-fA-F]{3,8}\b|(?:rgb|hsl)a?\(")
    def test_default_dark_override_precedes_rendering(self):
        html = (MODULE_PATH.parent.parent / "docs" / "index.html").read_text(encoding="utf-8")
        self.assertIn('<html lang="en-GB" data-theme="dark">', html)
        self.assertIn('<meta name="color-scheme" content="dark light">', html)
        scripts = re.findall(r"<script>(.*?)</script>", html, re.S)
        self.assertGreaterEqual(len(scripts), 2)
        self.assertIn('param === "light" ? "light" : "dark"', scripts[0])
        self.assertLess(html.index(scripts[0]), html.index("<style>"))
        self.assertIn('root.classList.add("js")', scripts[1])
    def test_reviewed_public_content_and_transcript_pins(self):
        docs = MODULE_PATH.parent.parent / "docs"
        html = (docs / "index.html").read_text(encoding="utf-8")
        body = re.search(r"<body>.*</body>", html, re.S).group()
        self.assertEqual(release.digest(body.encode()), "b1ceba3d46c5702097de432cd669c2b65e26f05e7cd3845c91a0872446bd32a1")
        transcripts = {
            "cats-and-dogs-transcript.txt": ("caa360d3af8dc9151106168311ec18cdf38d881c5d1afbf51ca98dd3c9aefb59",
                3837, "46c34b985475171d5ee464fc0ae0eb96bead9ca43a33b3ff719caca87351aed8"),
            "original-word-conversations.txt": ("2f44dc283a1dd81eaea5c3f832e9c85e0cdcb0b7ca0b7c8d112c261901a0bee3",
                2766, "2ce17280cc62a5bd98a860eab2be46e96ccb43a460f0dc314e91096d6187e1a9"),
            "original-powerpoint-conversations.txt": ("72681ed174b6c2a57d790df18ccbebc45f0900a2b83105d3591e5474832f42f7",
                5299, "90f3b0c9695df71510c66af86839127adb983d7c664396fd8753c5299fe8392f"),
        }
        for name, (expected, prefix_bytes, prefix_hash) in transcripts.items():
            text = (docs / "downloads" / name).read_text(encoding="utf-8")
            self.assertEqual(release.digest(text.encode()), expected)
            marker = "PUBLICATION BOUNDARY / NOT AN AGENT MESSAGE"
            self.assertEqual(text.count(marker), 1)
            prefix = text.split(marker)[0].encode()
            self.assertEqual(len(prefix), prefix_bytes)
            self.assertEqual(release.digest(prefix), prefix_hash)
    def test_public_narrative_keeps_compatibility_without_policy_discussion(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        class BodyText(HTMLParser):
            def __init__(self):
                super().__init__()
                self.parts = []
            def handle_data(self, data):
                self.parts.append(data)
            def handle_starttag(self, tag, attrs):
                if tag == "img":
                    self.parts.append(dict(attrs).get("alt", ""))
        page = BodyText()
        page.feed(re.search(r"<body>.*</body>", html, re.S).group())
        prose = [" ".join(page.parts)]
        for name in ("README.md", "docs/downloads/reuse-guide.md",
                     "docs/downloads/cats-and-dogs-transcript.txt",
                     "docs/downloads/original-word-conversations.txt",
                     "docs/downloads/original-powerpoint-conversations.txt"):
            prose.append((root / name).read_text(encoding="utf-8"))
        def descriptions(value):
            if isinstance(value, dict):
                for key, child in value.items():
                    if key != "publicSensitivityLabel":
                        yield from descriptions(child)
            elif isinstance(value, list):
                for child in value:
                    yield from descriptions(child)
            elif isinstance(value, str):
                yield value
        manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
        prose.extend(descriptions(manifest))
        forbidden = (r"(?i)\b(?:sensitivity|encrypt(?:ed|ion)?|revocation|downgrade|"
                     r"re-?labell?(?:ed|ing)?|KeepIRM|GetLabel|EncryptedPackage|rights-protected)\b|"
                     r"\b(?:label|classification)[- /]+(?:hash|metadata|record|history|policy|identifiers?)\b|"
                     r"\b(?:General|Public)\s+(?:policy|label)\b|method=Privileged|"
                     r"Contoso Internal|Northwind Internal|Internal/Confidential")
        for text in prose:
            self.assertNotRegex(text, forbidden)
            self.assertNotRegex(text.replace("queue/topic classifications", ""), r"(?i)\bclassif\w*")
        for text in prose[:3]:
            self.assertIn("7c5858479154c2c5d20a2e8c636faddd252c90fbcd97acd209fa13880e21916b", text)
            self.assertIn("98,985-byte", text)
            self.assertIn("not compatible", text)
            self.assertIn("integrity/contract", text)
            self.assertIn("byte-identical benchmark originals", text)
        self.assertIn("General source landing pages", prose[0])
        self.assertIn("inferred queue/topic classifications", prose[0])
        self.assertIn('aria-labelledby="deployment-setup-title"', html)
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
                         "Imported with warnings; target configuration pending; runtime not verified."):
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
        self.assertEqual(len(manifest["assets"]), 17)
        self.assertEqual(len(manifest["sourceFiles"]) + len(manifest["assets"]), 33)
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
        self.assertEqual(spec["targetImportStatus"], "SUCCEEDED_WITH_WARNINGS")
        self.assertEqual(spec["targetConfigurationStatus"], "PENDING")
        self.assertEqual(spec["targetRuntimeStatus"], "NOT_VERIFIED")
        observation = spec["targetImportObservation"]
        self.assertEqual(observation["attempts"], 2)
        self.assertEqual(observation["stagingStatus"], "PASSED")
        self.assertEqual(observation["missingDependencies"], 0)
        self.assertEqual(observation["installedCounts"], {"bots": 2, "botComponents": 39,
                         "flows": 5, "models": 3, "configurations": 6, "connectionReferences": 3,
                         "flowAssociations": 9, "directConnectorAssociations": 1, "solutionMembership": 62})
        self.assertIs(observation["allFlowsInactive"], True)
        self.assertEqual(observation["savedPromptPayloadsMatchExport"], 3)
        self.assertEqual(observation["importLogCounts"], {"success": 18, "warning": 5, "failure": 0})
        self.assertIn("not additive component counts", observation["verificationBasis"])
        self.assertIs(observation["blindRetries"], False)
        self.assertIs(observation["runtimeVerified"], False)
        self.assertEqual(len(spec["targetImportHistory"]), 1)
        first_attempt = spec["targetImportHistory"][0]
        self.assertEqual(first_attempt["status"], "FAILED")
        self.assertEqual(first_attempt["attempts"], 1)
        self.assertEqual(first_attempt["errorCode"], "BadGatewayConnection")
        self.assertIn("no installed solution", first_attempt["summary"])
        self.assertIn("not all external resources", first_attempt["readbackScope"])
        for flag in ("publishWorkflows", "overwriteUnmanagedCustomizations", "retryPerformed", "runtimeExecuted"):
            self.assertIs(first_attempt[flag], False)
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
        self.assertEqual(len(re.findall(r"<a\b[^>]*\bdownload(?:\s|>)", html)), 21)
        for name in ("TechnicalDocumentationBuilderDeployed_unmanaged_20260928T105706Z.zip", "Technical-Design-Tables-v0.2.docx", "Short-Briefing-5-Slides.pptx", "Short-Briefing-With-Images-5-Slides.pptx", "Cats-and-Dogs-Creation05-PUBLIC.pptx", "Cats-and-Dogs-Revision06-PUBLIC.pptx", "reuse-guide.md", "cats-and-dogs-transcript.txt", "original-word-conversations.txt", "original-powerpoint-conversations.txt", "synthetic-context.txt"):
            self.assertIn(f'href="downloads/{name}"', html)
        for phrase in ("Imported with warnings; target configuration pending; runtime not verified.",
                       "98,985-byte template", "not compatible", "No environment variables"):
            self.assertIn(phrase, card)
        guide = (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8")
        readme = (root / "README.md").read_text(encoding="utf-8")
        for source in (card, guide, readme):
            with self.subTest(source=source[:40]):
                source = " ".join(source.split())
                self.assertIn("controlled second import attempt", source.lower())
                self.assertIn("staging passed with no missing dependencies", source.lower())
                self.assertIn("all five flows were Off at verification".lower(), source.lower())
                self.assertIn("18 success, 5 warning and 0 failure", source)
                self.assertIn("log results, not component counts", source)
                self.assertIn("First attempt / historical failure:", source)
                self.assertIn("BadGatewayConnection", source)
                self.assertIn("agent-to-flow association service", source)
                self.assertIn("import-log successes did not prove installed components", source)
                self.assertIn("after that attempt found no installed solution", source)
                self.assertIn("Two controlled import attempts in total, not blind retries", source)
                self.assertNotIn("rolled back", source)
                self.assertNotIn("Target import: failed", source)
                self.assertNotIn("NOT STARTED", source)
                self.assertNotIn("not started", source)
        for phrase in ("### Native import boundary", "### 1. Choose destination and bind connections",
                       "### 2. Provision templates and output storage", "### 3. Retarget imported flow settings and save",
                       "### 4. Check readiness and activate only intended flows",
                       "### 5. Configure authentication, publish both agents and distribute", "PublishWorkflows=false",
                       "12,629-byte", "14,564-byte", "zero environment variables",
                       "7c5858479154c2c5d20a2e8c636faddd252c90fbcd97acd209fa13880e21916b"):
            self.assertIn(phrase, guide)
        self.assertNotIn("No tenant-bound topics, connections, solution ZIPs or deployable flows", html)
    def test_cross_tenant_setup_is_visible_and_separate_from_runtime_evidence(self):
        root = MODULE_PATH.parent.parent
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        setup = re.search(r'<aside id="deployment-setup".*?</aside>', html, re.S).group()
        self.assertEqual(len(re.findall(r"<li>", setup)), 5)
        self.assertNotIn("<details", setup)
        self.assertIn('href="#deployment-setup"', html)
        self.assertIn('aria-labelledby="deployment-setup-title"', setup)
        for phrase in ("Connected", "tdb_DraftingPrompt", "tdb_WordRenderer", "tdb_OneDriveDrafts",
                       "same destination identity", "direct Word action", "My files",
                       "Technical Documentation Builder", "Templates", "Generated Drafts",
                       "Technical-Design-Tables-v0.2.docx", "Copilot-session-7c585847.pptx",
                       "SharePoint is not a drop-in", "three Predict organization fields",
                       "OneDrive prerequisite", "not a separate model-driven app or custom app registration",
                       "template read access and output write access", "without resaving",
                       "ETags/file-version pins", "template/hash/integrity/contract guards",
                       "zero environment variables", "legacy Word v0.1 disabled",
                       "end-user authentication", "Docs Compare - Standard", "publish both",
                       "Make agent available in Microsoft 365 Copilot", "own account first",
                       "admin approval", "NOT_VERIFIED", "Evidence remains separate"):
            self.assertIn(phrase, setup)
        self.assertIn("#deployment-setup", (root / "README.md").read_text(encoding="utf-8"))
        guide = (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8")
        steps = guide.split("## Cross-tenant deployment setup", 1)[1].split(
            "### Runtime evidence is separate, not a setup step", 1)[0]
        self.assertEqual(re.findall(r"^### (\d)\.", steps, re.M), ["1", "2", "3", "4", "5"])
        for phrase in ("Import copies connection references, not live authenticated connections",
                       "### Prerequisite: your own OneDrive for Business",
                       "Adopters must set up their own OneDrive arrangement",
                       "not a separate model-driven app or a custom app registration",
                       "Import does not provision OneDrive, create folders, copy templates or transfer",
                       "Every adopter must bind all three", "direct Word action",
                       "does\n**not** automatically configure", "Create or reuse **Connected**",
                       "Solution import does not create these folders or copy/upload the templates",
                       "Matching folder names alone is insufficient",
                       "SharePoint is not a drop-in", "Save", "zero environment variables",
                       "leave the Long\nroute disabled", "Keep legacy Word v0.1 disabled",
                       "Settings > Security > Authentication", "publish both agents",
                       "Channels > Teams and Microsoft 365 Copilot", "See agent in Teams > Add",
                       "Make agent available in Microsoft 365 Copilot",
                       "authoring-solutions-import-export", "publication-add-bot-to-microsoft-teams"):
            self.assertIn(phrase, steps)
        self.assertNotIn("creation/revision", steps)
    def test_deployment_screenshots_are_pinned_visible_and_qualified(self):
        root = MODULE_PATH.parent.parent
        manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
        crops = [a for a in manifest["assets"] if a["kind"] == "deployment-setup-preview"]
        expected = {
            "deployment-onedrive-folders.png":
                ("872237872dba402f042ebb5b5b5173b75a63d0ea43c86074af8ad1b1b715b06f", 585, 320),
            "deployment-onedrive-template-files.png":
                ("0e2d4da212dfc5f57f57ffef9329678ca12a78f92c8623b1ce8467d8e75268a7", 826, 303),
        }
        self.assertEqual({Path(a["path"]).name for a in crops}, set(expected))
        for asset in crops:
            self.assertEqual((asset["sha256"], asset["width"], asset["height"]),
                             expected[Path(asset["path"]).name])
            raw = (root / asset["path"]).read_bytes()
            self.assertEqual(release.digest(raw), asset["sha256"])
            release.check_png(raw, asset["path"], asset)
            self.assertIn("Pixels inside the crop are unchanged", asset["transformation"])
            self.assertIn("Raw original remains private", asset["transformation"])
        html = (root / "docs" / "index.html").read_text(encoding="utf-8")
        preview = re.search(r'<aside id="deployment-storage-previews".*?</aside>', html, re.S).group()
        self.assertNotIn("<details", preview)
        self.assertEqual(preview.count("<figure>"), 2)
        images = re.findall(r'<a href="([^"]+)"><img [^>]*src="([^"]+)"[^>]*></a>', preview)
        self.assertEqual(len(images), 2)
        guide = (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8")
        for full_size, image in images:
            self.assertEqual(full_size, image)
            self.assertIn(Path(image).name, expected)
            self.assertIn("../" + image, guide)
        for phrase in ("Modified By", "no UI was recreated", "Raw screenshots remain private",
                       "authenticated connections", "exact file bytes/hashes", "bindings",
                       "agent publication or runtime"):
            self.assertIn(phrase, preview)
            self.assertIn(phrase, guide)
        self.assertIn("NOT_VERIFIED", preview)
    def test_deployment_flow_map_and_storage_match_unchanged_native_archive(self):
        root = MODULE_PATH.parent.parent
        guide = (root / "docs" / "downloads" / "reuse-guide.md").read_text(encoding="utf-8")
        native, _ = self.native_solution()
        expected = {
            "DraftStructuredConte": ("Run_dedicated_prompt",),
            "RenderWordTablesv02": ("Check_template_metadata", "Populate_Word_template", "Save_Word_draft"),
            "RenderWordDraftv01": ("Check_template_metadata", "Populate_Word_template", "Save_Word_draft"),
            "DraftSlideContentv01": ("Run_dedicated_prompt",),
            "RenderPreparedTemplatev01": ("Run_renderer", "Get_template_metadata",
                                          "Recheck_template_metadata", "Get_template_content",
                                          "Save_PowerPoint_draft", "Return_file"),
        }
        def flatten(actions):
            result = dict(actions)
            for value in actions.values():
                result.update(flatten(value.get("actions", {})))
                result.update(flatten(value.get("else", {}).get("actions", {})))
            return result
        predict_fields = 0
        output_actions = 0
        with zipfile.ZipFile(native) as archive:
            for flow, action_names in expected.items():
                paths = [p for p in archive.namelist() if p.startswith("Workflows/") and flow in p]
                self.assertEqual(len(paths), 1)
                definition = json.loads(archive.read(paths[0]))["properties"]["definition"]
                actions = flatten(definition["actions"])
                self.assertIn(flow, guide)
                for action in action_names:
                    self.assertIn(action, actions)
                    self.assertIn(f"`{action}`", guide)
                for action in actions.values():
                    inputs = action.get("inputs", {})
                    if not isinstance(inputs, dict):
                        continue
                    parameters = inputs.get("parameters", {})
                    predict_fields += "organization" in parameters
                    if inputs.get("host", {}).get("operationId") == "CreateFile":
                        self.assertEqual(parameters["folderPath"], "/Technical Documentation Builder/Generated Drafts")
                        self.assertIn(parameters["folderPath"], guide)
                        output_actions += 1
                if "Populate_Word_template" in actions:
                    self.assertEqual(actions["Populate_Word_template"]["inputs"]["parameters"]["source"], "me")
                if "Get_template_content" in actions:
                    path = actions["Get_template_content"]["inputs"]["parameters"]["path"]
                    self.assertEqual(path, "/Technical Documentation Builder/Templates/Copilot-session-7c585847.pptx")
                    self.assertIn(path, guide)
        self.assertEqual(predict_fields, 3)
        self.assertEqual(output_actions, 3)
if __name__ == "__main__":
    unittest.main()
