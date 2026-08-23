#!/usr/bin/env python3
"""Dependency-free integrity checks for the static site and built release files."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unittest
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PUBLIC = ROOT / "public"
INDEX = (PUBLIC / "index.html").read_text(encoding="utf-8")
CSS = (PUBLIC / "styles.css").read_text(encoding="utf-8")
NOT_FOUND = (PUBLIC / "404.html").read_text(encoding="utf-8")
VERSION = (ROOT / "RELEASE_VERSION").read_text(encoding="utf-8").strip()
EXPECT_BUILT = "--built" in sys.argv
if EXPECT_BUILT:
    sys.argv.remove("--built")


class SiteParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.tags: Counter[str] = Counter()
        self.ids: list[str] = []
        self.hrefs: list[str] = []
        self.images: list[dict[str, str]] = []
        self.assets: list[str] = []
        self.metas: list[dict[str, str]] = []
        self.links: list[dict[str, str]] = []
        self.html_attrs: dict[str, str] = {}
        self.aria_references: list[str] = []
        self.inline_handlers: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {name: value or "" for name, value in attrs}
        self.tags[tag] += 1
        if tag == "html":
            self.html_attrs = values
        if "id" in values:
            self.ids.append(values["id"])
        if "href" in values:
            self.hrefs.append(values["href"])
        if tag == "img":
            self.images.append(values)
        if tag == "meta":
            self.metas.append(values)
        if tag == "link":
            self.links.append(values)
        for attribute in ("src", "poster"):
            if attribute in values:
                self.assets.append(values[attribute])
        if tag == "link" and values.get("rel") in {"stylesheet", "icon"}:
            self.assets.append(values.get("href", ""))
        if "aria-labelledby" in values:
            self.aria_references.extend(values["aria-labelledby"].split())
        self.inline_handlers.extend(name for name in values if name == "style" or name.startswith("on"))


PARSER = SiteParser()
PARSER.feed(INDEX)


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    """Read JPEG dimensions without an image-library dependency."""
    data = path.read_bytes()
    if not data.startswith(b"\xff\xd8"):
        raise ValueError("not a JPEG")
    offset = 2
    while offset + 9 < len(data):
        if data[offset] != 0xFF:
            offset += 1
            continue
        marker = data[offset + 1]
        offset += 2
        if marker in {0xD8, 0xD9}:
            continue
        if offset + 2 > len(data):
            break
        length = int.from_bytes(data[offset : offset + 2], "big")
        if marker in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
            height = int.from_bytes(data[offset + 3 : offset + 5], "big")
            width = int.from_bytes(data[offset + 5 : offset + 7], "big")
            return width, height
        if length < 2:
            break
        offset += length
    raise ValueError("JPEG dimensions not found")


class SourceTests(unittest.TestCase):
    def test_document_structure(self) -> None:
        self.assertTrue(INDEX.lower().startswith("<!doctype html>"))
        self.assertEqual(PARSER.html_attrs.get("lang"), "en")
        self.assertEqual(PARSER.tags["title"], 1)
        self.assertEqual(PARSER.tags["h1"], 1)
        self.assertEqual(PARSER.tags["main"], 1)
        self.assertEqual(PARSER.tags["script"], 0)
        self.assertEqual(PARSER.inline_handlers, [])

    def test_not_found_document(self) -> None:
        parser = SiteParser()
        parser.feed(NOT_FOUND)
        self.assertTrue(NOT_FOUND.lower().startswith("<!doctype html>"))
        self.assertEqual(parser.html_attrs.get("lang"), "en")
        self.assertEqual(parser.tags["title"], 1)
        self.assertEqual(parser.tags["h1"], 1)
        self.assertEqual(parser.tags["main"], 1)
        self.assertEqual(parser.tags["script"], 0)
        self.assertIn("/", parser.hrefs)
        self.assertIn("/styles.css", parser.assets)

    def test_ids_and_fragment_links(self) -> None:
        duplicates = [item for item, count in Counter(PARSER.ids).items() if count > 1]
        self.assertEqual(duplicates, [])
        missing = [href for href in PARSER.hrefs if href.startswith("#") and href[1:] not in PARSER.ids]
        self.assertEqual(missing, [])
        missing_aria = [item for item in PARSER.aria_references if item not in PARSER.ids]
        self.assertEqual(missing_aria, [])

    def test_images_are_explicit_and_local(self) -> None:
        for image in PARSER.images:
            self.assertIn("alt", image)
            self.assertIn("width", image)
            self.assertIn("height", image)
        external_assets = [asset for asset in PARSER.assets if not asset.startswith("/")]
        self.assertEqual(external_assets, [])
        self.assertNotRegex(CSS, r"url\(\s*['\"]?https?://")

    def test_metadata(self) -> None:
        by_name = {meta.get("name"): meta.get("content", "") for meta in PARSER.metas if meta.get("name")}
        by_property = {
            meta.get("property"): meta.get("content", "") for meta in PARSER.metas if meta.get("property")
        }
        description = by_name.get("description", "")
        self.assertGreaterEqual(len(description), 100)
        self.assertLessEqual(len(description), 160)
        for name in ("viewport", "color-scheme", "twitter:card", "twitter:image", "twitter:image:alt"):
            self.assertTrue(by_name.get(name), name)
        for name in ("og:type", "og:title", "og:description", "og:url", "og:image", "og:image:alt"):
            self.assertTrue(by_property.get(name), name)
        canonicals = [link.get("href") for link in PARSER.links if link.get("rel") == "canonical"]
        self.assertEqual(canonicals, ["https://claude-kiss.com/"])

    def test_version_references_stay_in_sync(self) -> None:
        self.assertRegex(VERSION, r"^\d+\.\d+\.\d+(?:[.-][0-9A-Za-z.-]+)?$")
        self.assertIn(f"v{VERSION}", INDEX)
        redirects = (PUBLIC / "_redirects").read_text(encoding="utf-8")
        versions = set(re.findall(r"/releases/v([^/\s]+)", redirects))
        self.assertEqual(versions, {VERSION})

    def test_policy_files(self) -> None:
        headers = (PUBLIC / "_headers").read_text(encoding="utf-8").lower()
        for header in (
            "content-security-policy:",
            "strict-transport-security:",
            "permissions-policy:",
            "referrer-policy:",
            "x-content-type-options:",
        ):
            self.assertIn(header, headers)
        self.assertIn("/releases/v:version/*", headers)
        self.assertNotIn("/releases/*\n", headers)
        self.assertIn("cache-control: no-transform", headers)
        self.assertIn("connect-src 'self'", headers)
        self.assertNotIn("cloudflareinsights", headers)
        robots = (PUBLIC / "robots.txt").read_text(encoding="utf-8")
        self.assertIn("Sitemap: https://claude-kiss.com/sitemap.xml", robots)
        sitemap = ET.parse(PUBLIC / "sitemap.xml")
        locations = [node.text for node in sitemap.findall("{http://www.sitemaps.org/schemas/sitemap/0.9}url/{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertEqual(locations, ["https://claude-kiss.com/"])

    def test_vector_assets_and_social_card(self) -> None:
        for filename in ("favicon.svg", "mark.svg", "og.svg"):
            ET.parse(PUBLIC / filename)
        self.assertEqual(jpeg_dimensions(PUBLIC / "og.jpg"), (1200, 630))
        self.assertLess((PUBLIC / "og.jpg").stat().st_size, 200_000)

    def test_site_stays_small_and_script_free(self) -> None:
        self.assertLess(len(INDEX.encode()), 20_000)
        self.assertLess(len(CSS.encode()), 25_000)
        self.assertEqual(list(PUBLIC.glob("*.js")), [])
        for required in ("prefers-color-scheme", "prefers-reduced-motion", "focus-visible", "forced-colors"):
            self.assertIn(required, CSS)


@unittest.skipUnless(EXPECT_BUILT, "run with --built after ./build.sh")
class BuiltReleaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.release = PUBLIC / "releases" / f"v{VERSION}"

    def test_generated_installer(self) -> None:
        installer = PUBLIC / "install.sh"
        self.assertTrue(installer.is_file())
        self.assertNotEqual(installer.stat().st_mode & 0o111, 0)
        self.assertIn(
            f"release_version=${{CLAUDE_KISS_VERSION:-{VERSION}}}",
            installer.read_text(encoding="utf-8"),
        )

    def test_generated_release(self) -> None:
        archive = self.release / "claude-kiss.tar.gz"
        checksum_file = self.release / "claude-kiss.tar.gz.sha256"
        metadata = json.loads((self.release / "release.json").read_text(encoding="utf-8"))
        expected = checksum_file.read_text(encoding="utf-8").split()[0].lower()
        actual = hashlib.sha256(archive.read_bytes()).hexdigest()
        self.assertEqual(actual, expected)
        self.assertEqual(metadata["version"], VERSION)
        self.assertEqual(metadata["sha256"], expected)
        self.assertEqual(metadata["archive"], f"https://claude-kiss.com/releases/v{VERSION}/claude-kiss.tar.gz")
        self.assertEqual(metadata["installer"], "https://claude-kiss.com/install.sh")
        self.assertEqual(
            metadata["release"],
            f"https://github.com/aphoristicartist/claude-kiss/releases/tag/v{VERSION}",
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
