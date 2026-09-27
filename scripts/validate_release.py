"""Offline release allowlist, link, privacy and Office integrity checks."""

import argparse
import hashlib
from html.parser import HTMLParser
import json
import os
from pathlib import Path, PurePosixPath
import posixpath
import re
import shutil
import struct
import sys
from urllib.parse import unquote, urlsplit
import xml.etree.ElementTree as ET
import zipfile
import zlib


ROOT = Path(__file__).resolve().parent.parent
UUID = re.compile(r"\b[0-9a-f]{8}-(?:[0-9a-f]{4}-){3}[0-9a-f]{12}\b", re.I)
PATTERNS = {
    "personal email": r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b",
    "local user path": r"(?:[A-Z]:[\\/]+(?:Users|Documents and Settings)[\\/]|/(?:Users|home)/[^/\s]+/)",
    "tenant host": r"https?://[^\s\"<>]*\.(?:sharepoint\.com|onmicrosoft\.com|crm\d*\.dynamics\.com)",
    "browser control endpoint": r"wss?://(?:127\.0\.0\.1|localhost)",
    "credential assignment": r"(?:[?&](?:sig|sas|access_token)=|Bearer\s+[A-Za-z0-9._~+/=-]{12,})",
    "token value": r"(?:gh[pousr]_[A-Za-z0-9]{20,}|eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,})",
}
TEXT_EXTENSIONS = {".html", ".css", ".js", ".md", ".json", ".py", ".yml", ".txt"}
OFFICE_MAIN = {
    ".docx": "word/document.xml",
    ".pptx": "ppt/presentation.xml",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
DRAW_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
WORD_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
THEME_NS = "http://schemas.microsoft.com/office/thememl/2012/main"
LABEL_PART = "docMetadata/LabelInfo.xml"
LABEL_NS = "http://schemas.microsoft.com/office/2020/mipLabelMetadata"
LABEL_REL = "http://schemas.microsoft.com/office/2020/02/relationships/classificationlabels"
LABEL_TYPE = "application/vnd.ms-office.classificationlabels+xml"
PUBLIC_COPIES = {
    "docs/downloads/Cats-and-Dogs-Creation05-PUBLIC.pptx",
    "docs/downloads/Cats-and-Dogs-Revision06-PUBLIC.pptx",
}


class ReleaseError(ValueError):
    pass


def require(condition, message):
    if not condition:
        raise ReleaseError(message)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def safe_path(value):
    path = PurePosixPath(value)
    require(
        value and "\\" not in value and not path.is_absolute()
        and ".." not in path.parts and ":" not in value and value == path.as_posix(),
        "Noncanonical or unsafe manifest path",
    )
    return path


def scan_text(text, label, check_uuid=True):
    for name, pattern in PATTERNS.items():
        require(not re.search(pattern, text, re.I), f"{label}: {name} marker")
    if check_uuid:
        require(not UUID.search(text), f"{label}: unreviewed identifier")


def check_png(data, label, expected=None, reviewed_software=None):
    require(data.startswith(b"\x89PNG\r\n\x1a\n"), f"{label}: not PNG")
    position, chunks, dimensions = 8, [], None
    while position < len(data):
        require(position + 12 <= len(data), f"{label}: truncated PNG")
        length, kind = struct.unpack(">I4s", data[position:position + 8])
        end = position + 12 + length
        require(end <= len(data), f"{label}: invalid PNG chunk length")
        body = data[position + 8:position + 8 + length]
        crc = struct.unpack(">I", data[end - 4:end])[0]
        require(zlib.crc32(kind + body) & 0xFFFFFFFF == crc, f"{label}: PNG CRC mismatch")
        require(kind in {b"IHDR", b"IDAT", b"IEND", b"pHYs", b"sRGB", b"gAMA", b"cHRM", b"PLTE", b"tRNS"}
                or kind == b"tEXt" and reviewed_software == "Figma" and body == b"Software\x00Figma",
                f"{label}: unreviewed PNG metadata chunk")
        if kind == b"IHDR":
            require(not chunks and length == 13, f"{label}: invalid PNG header")
            dimensions = struct.unpack(">II", body[:8])
        chunks.append(kind)
        position = end
        if kind == b"IEND":
            require(length == 0 and position == len(data), f"{label}: trailing PNG data")
            break
    require(chunks and chunks[-1] == b"IEND" and b"IDAT" in chunks, f"{label}: incomplete PNG")
    require(dimensions and all(0 < d <= 10000 for d in dimensions), f"{label}: invalid PNG dimensions")
    if expected:
        require(dimensions == (expected["width"], expected["height"]), f"{label}: PNG size changed")


def check_office_identifiers(tree, label):
    # Format extension, theme and field IDs are not environment or tenant identities.
    for element in tree.iter():
        require(not UUID.search(element.text or ""), f"{label}: identifier in document text")
        require(not UUID.search(element.tail or ""), f"{label}: identifier in XML tail")
        local = element.tag.rsplit("}", 1)[-1]
        for key, value in element.attrib.items():
            if not UUID.search(value):
                continue
            allowed = (
                local == "ext" and key == "uri"
                or element.tag == f"{{{DRAW_NS}}}tblStyleLst" and key == "def"
                or element.tag == f"{{{THEME_NS}}}themeFamily" and key in {"id", "vid"}
                or element.tag == f"{{{DRAW_NS}}}fld" and key == "id"
            )
            require(allowed, f"{label}: identifier outside reviewed Office format fields")


def relationship_source(part):
    if part == "_rels/.rels":
        return ""
    path = PurePosixPath(part)
    require(path.parent.name == "_rels", f"{part}: invalid relationship part")
    return (path.parent.parent / path.name.removesuffix(".rels")).as_posix()


def check_public_label(data, tree, spec, label):
    expected = spec["publicSensitivityLabel"]
    require(spec.get("kind") == "public-release-copy" and spec.get("path") in PUBLIC_COPIES,
            f"{label}: Public metadata exception is restricted to two reviewed copies")
    require(expected.get("part") == LABEL_PART and expected.get("name") == "Public"
            and digest(data) == expected.get("sha256"),
            f"{label}: Public metadata checksum or approval mismatch")
    require(tree.tag == f"{{{LABEL_NS}}}labelList" and not tree.attrib and len(tree) == 1,
            f"{label}: unexpected Public label history")
    record = tree[0]
    require(record.tag == f"{{{LABEL_NS}}}label" and not len(record),
            f"{label}: unexpected Public label record")
    fixed = {"enabled": "1", "method": "Privileged", "contentBits": "0", "removed": "0"}
    require(set(record.attrib) == set(fixed) | {"id", "siteId"}
            and all(record.get(key) == value == expected.get(key) for key, value in fixed.items()),
            f"{label}: Public label attributes changed")
    for key, pin in (("id", "labelIdSha256"), ("siteId", "siteIdSha256")):
        value = record.get(key, "")
        require(value.startswith("{") and value.endswith("}") and UUID.fullmatch(value[1:-1]),
                f"{label}: invalid Public policy identifier")
        require(digest(value[1:-1].lower().encode()) == expected.get(pin),
                f"{label}: unreviewed Public policy identifier")


def check_label_reference(tree, part, label):
    if part == "_rels/.rels":
        matches = [e for e in tree if e.get("Type") == LABEL_REL]
        require(len(matches) == 1 and matches[0].tag == f"{{{REL_NS}}}Relationship"
                and set(matches[0].attrib) == {"Id", "Type", "Target"}
                and matches[0].get("Target") == LABEL_PART,
                f"{label}: unexpected classification relationship")
    else:
        matches = [e for e in tree if e.get("ContentType") == LABEL_TYPE]
        require(len(matches) == 1
                and matches[0].tag == "{http://schemas.openxmlformats.org/package/2006/content-types}Override"
                and matches[0].attrib == {"PartName": "/" + LABEL_PART, "ContentType": LABEL_TYPE},
                f"{label}: unexpected classification content type")


def check_office(path, spec):
    label = path.name
    with zipfile.ZipFile(path) as archive:
        names = archive.namelist()
        files = {name for name in names if not name.endswith("/")}
        require(not archive.comment and all(not part.comment and not part.extra for part in archive.infolist()),
                f"{label}: unreviewed ZIP metadata")
        require(len(names) == len(set(names)), f"{label}: duplicate ZIP names")
        require(sum(part.file_size for part in archive.infolist()) < 20_000_000,
                f"{label}: unexpectedly large expanded package")
        require(archive.testzip() is None, f"{label}: ZIP CRC failure")
        require({"[Content_Types].xml", "_rels/.rels", OFFICE_MAIN[path.suffix]} <= files,
                f"{label}: missing required Office parts")
        public_label = spec.get("publicSensitivityLabel")
        require((LABEL_PART in files) == bool(public_label), f"{label}: unreviewed or missing label metadata")
        if public_label:
            require(spec.get("path") == "docs/downloads/" + path.name,
                    f"{label}: Public metadata exception path mismatch")
        xml = {}
        media = {}
        for name in files:
            safe_path(name)
            scan_text(name, f"{label}:part-name")
            require(name == LABEL_PART and public_label
                    or not re.search(r"docMetadata|customXml|vbaProject|embeddings|activeX|oleObject|signature", name, re.I),
                    f"{label}: unreviewed metadata or active-content part")
            data = archive.read(name)
            if name.endswith((".xml", ".rels")):
                text = data.decode("utf-8")
                scan_text(text, f"{label}:{name}", check_uuid=False)
                require(not re.search(r"<!DOCTYPE|<!ENTITY", text, re.I), f"{label}: unsafe XML metadata")
                tree = ET.fromstring(text)
                xml[name] = tree
                metadata = re.findall(r"mipLabelMetadata|classificationlabels|MSIP_Label|sensitivity", text, re.I)
                if name == LABEL_PART:
                    check_public_label(data, tree, spec, label)
                else:
                    if metadata:
                        require(public_label and name in {"_rels/.rels", "[Content_Types].xml"}
                                and metadata == ["classificationlabels"],
                                f"{label}: unreviewed classification metadata")
                        check_label_reference(tree, name, label)
                    check_office_identifiers(tree, f"{label}:{name}")
                for element in tree.iter():
                    local = element.tag.rsplit("}", 1)[-1]
                    require(local not in {"comment", "ins", "del", "documentProtection", "writeProtection", "modifyVerifier"},
                            f"{label}: comments, tracked edits or editing protection")
                    if local in {"creator", "lastModifiedBy"}:
                        allowed_authors = {""} if public_label else {"Technical Documentation Builder", "Un-named", ""}
                        require((element.text or "") in allowed_authors,
                                f"{label}: unreviewed personal metadata")
            else:
                require(name.startswith(("ppt/media/", "word/media/")) and name.endswith(".png"),
                        f"{label}: unreviewed binary part")
                check_png(data, f"{label}:{name}", reviewed_software=spec.get("knownSoftwareMetadata", {}).get(name))
                media[name] = digest(data)
        require(media == spec.get("media", {}), f"{label}: embedded media differs from allowlist")
        if public_label:
            check_label_reference(xml["_rels/.rels"], "_rels/.rels", label)
            check_label_reference(xml["[Content_Types].xml"], "[Content_Types].xml", label)
        for name, tree in xml.items():
            if name.endswith(".rels"):
                source = relationship_source(name)
                require(not source or source in files, f"{label}: orphan relationship part")
                ids = set()
                for rel in tree:
                    require(rel.tag == f"{{{REL_NS}}}Relationship", f"{label}: invalid relationship")
                    require(rel.get("Id") not in ids, f"{label}: duplicate relationship ID")
                    ids.add(rel.get("Id"))
                    require(rel.get("TargetMode", "Internal") == "Internal", f"{label}: external relationship")
                    target = unquote(rel.get("Target", ""))
                    require(target and not urlsplit(target).scheme and "\\" not in target,
                            f"{label}: unsafe relationship target")
                    resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), target)) if not target.startswith("/") else target[1:]
                    require(resolved in files, f"{label}: broken relationship target")
                if source:
                    for element in xml[source].iter():
                        for key, value in element.attrib.items():
                            if key.startswith("{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"):
                                require(value in ids, f"{label}: missing relationship ID")
        types = xml["[Content_Types].xml"]
        defaults = {x.get("Extension") for x in types if x.tag.endswith("}Default")}
        overrides = {x.get("PartName", "").lstrip("/") for x in types if x.tag.endswith("}Override")}
        require(sorted(overrides - files) == spec.get("knownUnusedContentTypeOverrides", []),
                f"{label}: unreviewed dangling content-type override")
        require(all(name == "[Content_Types].xml" or name in overrides or name.rsplit(".", 1)[-1] in defaults for name in files),
                f"{label}: missing content type")
        main = xml[OFFICE_MAIN[path.suffix]]
        if path.suffix == ".docx":
            require(len(main.findall(f".//{{{WORD_NS}}}tbl")) == spec["tables"], f"{label}: table count changed")
            require(len(main.findall(f".//{{{WORD_NS}}}sdt")) == spec["contentControls"], f"{label}: editable controls changed")
            require(bool(main.findall(f".//{{{WORD_NS}}}t")), f"{label}: no editable text")
        else:
            slides = sorted(name for name in files if re.fullmatch(r"ppt/slides/slide\d+\.xml", name))
            require(len(slides) == spec["slides"], f"{label}: slide count changed")
            require(len(main.findall(".//{*}sldId")) == spec["slides"], f"{label}: slide order count changed")
            for slide in slides:
                require(xml[slide].get("show", "1") in {"1", "true"}, f"{label}: hidden slide")
                require(bool(xml[slide].findall(f".//{{{DRAW_NS}}}t")), f"{label}: no editable slide text")


class Page(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.ids = set()
        self.links = []
        self.feed(text)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "id" in attrs:
            require(attrs["id"] not in self.ids, "Duplicate HTML id")
            self.ids.add(attrs["id"])
        for attr in ("href", "src"):
            if attr in attrs:
                self.links.append(attrs[attr])
        require(tag not in {"iframe", "object", "embed"}, "Embedded external/active page content")
        if tag == "img":
            require("alt" in attrs, "Image missing alternative text")


def resolve_link(source, url, allowed, pages):
    parts = urlsplit(url)
    if parts.scheme:
        require(parts.scheme in {"http", "https"}, f"{source}: unsafe link scheme")
        return
    require(not parts.netloc and not parts.path.startswith("/"), f"{source}: link breaks project-path hosting")
    relative = unquote(parts.path)
    require("\\" not in relative, f"{source}: invalid URL path")
    target = posixpath.normpath(posixpath.join(posixpath.dirname(source), relative)) if relative else source
    require(target in allowed or any(item.startswith(target.rstrip("/") + "/") for item in allowed),
            f"{source}: broken local link")
    if source.startswith("docs/"):
        require(target.startswith("docs/"), f"{source}: link escapes site artifact")
    if parts.fragment and target in pages:
        require(unquote(parts.fragment) in pages[target].ids, f"{source}: missing fragment")


def tree_files(root):
    result = set()
    for folder, directories, files in os.walk(root):
        base = Path(folder)
        for name in directories + files:
            require(not (base / name).is_symlink(), "Symlinks are not permitted in release tree")
        directories[:] = [
            name for name in directories
            if name != "__pycache__" and not (base == root and name in {".git", ".pages-artifact", ".local-preview"})
        ]
        for name in files:
            if base == root and name == ".git":
                continue
            result.add((base / name).relative_to(root).as_posix())
    return result


def validate(root=ROOT):
    manifest = json.loads((root / "release-manifest.json").read_text(encoding="utf-8"))
    require(manifest.get("schemaVersion") == 1 and manifest.get("siteRoot") == "docs", "Unsupported manifest")
    entries = manifest["sourceFiles"] + [asset["path"] for asset in manifest["assets"]]
    for entry in entries:
        safe_path(entry)
    require(len(entries) == len(set(entries)), "Duplicate allowlist entries")
    allowed = set(entries)
    actual = tree_files(root)
    require(actual == allowed, f"Allowlist mismatch: {len(actual - allowed)} unexpected, {len(allowed - actual)} missing files")
    pages = {}
    text_files = {}
    for name in sorted(allowed):
        path = root.joinpath(*PurePosixPath(name).parts)
        if path.suffix in TEXT_EXTENSIONS or path.name in {".gitignore", ".nojekyll"}:
            text = path.read_text(encoding="utf-8")
            scan_text(text, name)
            text_files[name] = text
            if path.suffix == ".html":
                pages[name] = Page(text)
    for asset in manifest["assets"]:
        path = root.joinpath(*PurePosixPath(asset["path"]).parts)
        data = path.read_bytes()
        require(digest(data) == asset["sha256"], f"{path.name}: SHA-256 mismatch")
        require("bytes" not in asset or len(data) == asset["bytes"], f"{path.name}: file length mismatch")
        if path.suffix in OFFICE_MAIN:
            check_office(path, asset)
        elif path.suffix == ".png":
            check_png(data, path.name, asset)
        else:
            raise ReleaseError("Unreviewed binary type")
    for name, page in pages.items():
        for link in page.links:
            resolve_link(name, link, allowed, pages)
    for name, text in text_files.items():
        if name.endswith(".md"):
            for link in re.findall(r"\[[^\]]+\]\(([^ )]+)\)", text):
                resolve_link(name, link, allowed, pages)
        if name.endswith(".css"):
            require(not re.search(r"#[0-9a-f]{3,8}\b|(?:rgb|hsl)a?\(", text, re.I), "Use Clawpilot color variables")
    print(f"PASS: {len(allowed)} allowlisted files; {len(manifest['assets'])} pinned assets; links, privacy and Office integrity.")
    return sorted(name for name in allowed if name.startswith("docs/"))


def stage(root, target, site_files):
    target = Path(os.path.abspath(target))
    require(not target.is_symlink(), "Stage target cannot be a symlink")
    require(not target.exists() or target.is_dir() and not any(target.iterdir()),
            "Stage target must be new or empty; existing artifacts are never merged")
    require(target.name == ".pages-artifact" and target.parent.resolve() == root.resolve(),
            "Stage target must be the repository's .pages-artifact directory")
    target.mkdir(exist_ok=True)
    for name in site_files:
        relative = PurePosixPath(name).relative_to("docs")
        destination = target.joinpath(*relative.parts)
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(root.joinpath(*PurePosixPath(name).parts), destination)
    require(tree_files(target) == {PurePosixPath(name).relative_to("docs").as_posix() for name in site_files},
            "Staged artifact does not match allowlist")
    print(f"PASS: staged exactly {len(site_files)} public-site files.")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--stage", type=Path)
    args = parser.parse_args()
    try:
        site_files = validate()
        if args.stage:
            stage(ROOT, args.stage, site_files)
    except (ReleaseError, OSError, UnicodeError, ET.ParseError, zipfile.BadZipFile, json.JSONDecodeError) as error:
        print(f"FAIL: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
