from pathlib import Path
import re
import unittest
from html import unescape
import json


ROOT = Path(__file__).resolve().parents[1]


def read_required(relative_path: str) -> str:
    path = ROOT / relative_path
    if not path.is_file():
        raise AssertionError(f"Required file is missing: {relative_path}")
    return path.read_text(encoding="utf-8")


def visible_words(fragment: str) -> list[str]:
    text = re.sub(r"<script\b.*?</script>", " ", fragment, flags=re.I | re.S)
    text = re.sub(r"<style\b.*?</style>", " ", text, flags=re.I | re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.findall(r"\b[A-Za-z]+(?:[’'-][A-Za-z]+)*\b", unescape(text))


class FoundationTests(unittest.TestCase):
    def test_shared_assets_exist(self):
        self.assertTrue((ROOT / "css" / "style.css").is_file())
        self.assertTrue((ROOT / "js" / "main.js").is_file())
        self.assertTrue((ROOT / "images" / "README.md").is_file())

    def test_numbered_image_references_are_relative(self):
        readme = read_required("images/README.md")
        for number in range(1, 11):
            self.assertIn(f"{number}.png", readme)
        self.assertIn("LOGO3.png", readme)
        self.assertNotIn('src="/images/', readme)

    def test_missing_images_have_fallback_behavior(self):
        script = read_required("js/main.js")
        css = read_required("css/style.css")
        self.assertIn("initImageFallbacks", script)
        self.assertIn("img-error", script)
        self.assertIn(".img-error", css)

    def test_mobile_menu_accessibility_contract(self):
        script = read_required("js/main.js")
        self.assertIn("initNavigation", script)
        self.assertIn("aria-expanded", script)
        self.assertIn("Escape", script)
        self.assertIn("setActiveNavigation", script)

    def test_css_contains_required_breakpoints_and_reduced_motion(self):
        css = read_required("css/style.css")
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn(":focus-visible", css)
        self.assertIn("--navy", css)
        self.assertIn("--gold", css)


class SitePageTests(unittest.TestCase):
    def test_home_and_about_structure(self):
        home = read_required("index.html")
        about = read_required("about.html")
        self.assertGreaterEqual(home.count("<section"), 6)
        self.assertGreaterEqual(about.count("<section"), 5)
        self.assertIn("QuantCore AI", home)
        self.assertIn("online and offline", about.lower())
        self.assertIn('href="css/style.css"', home)
        self.assertIn('src="js/main.js"', about)

    def test_home_and_about_seo_is_unique(self):
        home = read_required("index.html")
        about = read_required("about.html")
        home_title = re.search(r"<title>(.*?)</title>", home, re.S).group(1)
        about_title = re.search(r"<title>(.*?)</title>", about, re.S).group(1)
        self.assertNotEqual(home_title, about_title)
        self.assertIn("VMA Community", home_title)
        self.assertIn("VMA Community", about_title)
        self.assertRegex(home, r'<meta name="description" content="[^"]{80,}">')
        self.assertRegex(about, r'<meta name="description" content="[^"]{80,}">')

    def test_home_and_about_canonicals(self):
        home = read_required("index.html")
        about = read_required("about.html")
        self.assertIn('<link rel="canonical" href="https://VMACommunityOfficial.github.io/">', home)
        self.assertIn('<link rel="canonical" href="https://VMACommunityOfficial.github.io/about.html">', about)
        self.assertIn('href="images/LOGO3.png"', home)
        self.assertIn('href="images/LOGO3.png"', about)

    def test_home_and_about_jsonld(self):
        home = read_required("index.html")
        about = read_required("about.html")
        self.assertIn('"@type": "Organization"', home)
        self.assertIn('"@type": "WebSite"', home)
        self.assertRegex(about, r'"@type"\s*:\s*"AboutPage"')

    def test_internal_links_are_relative(self):
        for filename in ("index.html", "about.html"):
            html = read_required(filename)
            local_links = re.findall(r'href="([^"]+\.html(?:#[^"]*)?)"', html)
            self.assertGreaterEqual(len(local_links), 5)
            self.assertFalse(any(link.startswith("/") for link in local_links))


class InsightsTests(unittest.TestCase):
    article_files = [f"insight-{number}.html" for number in range(1, 6)]

    def test_insights_index_lists_five_articles(self):
        html = read_required("insights.html")
        for filename in self.article_files:
            self.assertIn(f'href="{filename}"', html)
        self.assertEqual(len(re.findall(r'class="insight-card', html)), 5)

    def test_article_titles_include_keyword(self):
        for filename in self.article_files:
            html = read_required(filename)
            title = re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S)
            self.assertIsNotNone(title, filename)
            self.assertIn("VMA Community", re.sub(r"<[^>]+>", "", title.group(1)), filename)

    def test_each_article_body_exceeds_1000_words(self):
        for filename in self.article_files:
            html = read_required(filename)
            body = re.search(r'<article class="article-body">(.*?)</article>', html, re.S)
            self.assertIsNotNone(body, filename)
            count = len(visible_words(body.group(1)))
            self.assertGreater(count, 1000, f"{filename} has {count} article words")

    def test_article_metadata_is_unique(self):
        titles = set()
        descriptions = set()
        canonicals = set()
        for filename in self.article_files:
            html = read_required(filename)
            titles.add(re.search(r"<title>(.*?)</title>", html, re.S).group(1))
            descriptions.add(re.search(r'<meta name="description" content="([^"]+)">', html).group(1))
            canonical = re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1)
            canonicals.add(canonical)
            self.assertTrue(canonical.endswith(filename))
        self.assertEqual(len(titles), 5)
        self.assertEqual(len(descriptions), 5)
        self.assertEqual(len(canonicals), 5)

    def test_article_schema_and_breadcrumbs(self):
        for filename in self.article_files:
            html = read_required(filename)
            self.assertRegex(html, r'"@type"\s*:\s*"Article"')
            self.assertRegex(html, r'"@type"\s*:\s*"BreadcrumbList"')
            self.assertIn('href="images/LOGO3.png"', html)

    def test_article_related_links_resolve(self):
        for filename in self.article_files:
            html = read_required(filename)
            related = re.search(r'<div class="related">(.*?)</div>', html, re.S)
            self.assertIsNotNone(related, filename)
            links = re.findall(r'href="(insight-[1-5]\.html)"', related.group(1))
            self.assertGreaterEqual(len(set(links)), 2, filename)
            for link in links:
                self.assertTrue((ROOT / link).is_file(), link)


class FaqTests(unittest.TestCase):
    def faq_entries(self):
        html = read_required("faq.html")
        entries = re.findall(r'<article class="faq-item">(.*?)</article>', html, re.S)
        return html, entries

    def test_faq_has_exactly_30_entries(self):
        _, entries = self.faq_entries()
        self.assertEqual(len(entries), 30)

    def test_faq_questions_are_distinct(self):
        _, entries = self.faq_entries()
        questions = [re.search(r'<h2 class="faq-question">(.*?)</h2>', item, re.S).group(1) for item in entries]
        normalized = [re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", question)).strip().lower() for question in questions]
        self.assertEqual(len(set(normalized)), 30)

    def test_faq_keyword_in_every_question_and_answer(self):
        _, entries = self.faq_entries()
        for index, item in enumerate(entries, 1):
            question = re.search(r'<h2 class="faq-question">(.*?)</h2>', item, re.S).group(1)
            answer = re.search(r'<div class="faq-answer">(.*?)</div>', item, re.S).group(1)
            self.assertIn("VMA Community", question, index)
            self.assertIn("VMA Community", answer, index)

    def test_faq_answers_exceed_80_words(self):
        _, entries = self.faq_entries()
        for index, item in enumerate(entries, 1):
            answer = re.search(r'<div class="faq-answer">(.*?)</div>', item, re.S).group(1)
            count = len(visible_words(answer))
            self.assertGreater(count, 80, f"FAQ {index} has {count} words")

    def test_faq_entries_are_not_collapsed(self):
        html, _ = self.faq_entries()
        self.assertNotIn("<details", html.lower())
        self.assertNotRegex(html.lower(), r'class="[^"]*accordion')
        self.assertNotRegex(html.lower(), r'<article class="faq-item"[^>]*hidden')
        self.assertNotIn("togglefaq", html.lower())

    def test_faq_schema_matches_visible_content(self):
        html, entries = self.faq_entries()
        self.assertRegex(html, r'"@type"\s*:\s*"FAQPage"')
        self.assertEqual(len(re.findall(r'"@type"\s*:\s*"Question"', html)), len(entries))

    def test_faq_schema_answers_are_visible(self):
        html, entries = self.faq_entries()
        payload = re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1)
        data = json.loads(payload)
        schema_entries = data["mainEntity"]
        self.assertEqual(len(schema_entries), len(entries))
        for visible, schema in zip(entries, schema_entries):
            visible_question = " ".join(visible_words(re.search(r'<h2 class="faq-question">(.*?)</h2>', visible, re.S).group(1)))
            visible_answer = " ".join(visible_words(re.search(r'<div class="faq-answer">(.*?)</div>', visible, re.S).group(1)))
            schema_question = " ".join(visible_words(schema["name"]))
            schema_answer = " ".join(visible_words(schema["acceptedAnswer"]["text"]))
            self.assertEqual(schema_question, visible_question)
            self.assertIn(schema_answer, visible_answer)


class ContactAndSeoTests(unittest.TestCase):
    expected_pages = [
        "", "about.html", "insights.html", "insight-1.html", "insight-2.html",
        "insight-3.html", "insight-4.html", "insight-5.html", "faq.html", "contact.html",
    ]

    def test_contact_links_are_exact_and_clickable(self):
        html = read_required("contact.html")
        self.assertIn('href="https://www.veritasmindai.com"', html)
        self.assertIn('href="mailto:service@veritasmindai.com"', html)
        self.assertIn("4040 Civic Center Dr, San Rafael, CA 94903, United States", html)
        self.assertRegex(html, r'href="https://www\.google\.com/maps/search/\?api=1&amp;query=[^"]+"')

    def test_contact_page_schema(self):
        html = read_required("contact.html")
        self.assertRegex(html, r'"@type"\s*:\s*"ContactPage"')
        self.assertIn("service@veritasmindai.com", html)
        self.assertIn('href="images/LOGO3.png"', html)

    def test_sitemap_contains_all_ten_pages_once(self):
        xml = read_required("sitemap.xml")
        urls = re.findall(r"<loc>(.*?)</loc>", xml)
        expected = [f"https://VMACommunityOfficial.github.io/{page}" for page in self.expected_pages]
        self.assertEqual(len(urls), 10)
        self.assertEqual(set(urls), set(expected))
        self.assertEqual(len(urls), len(set(urls)))

    def test_robots_points_to_canonical_sitemap(self):
        robots = read_required("robots.txt")
        self.assertIn("User-agent: *", robots)
        self.assertIn("Allow: /", robots)
        self.assertIn("Sitemap: https://VMACommunityOfficial.github.io/sitemap.xml", robots)

    def test_readme_lists_all_future_image_names(self):
        readme = read_required("README.md")
        for number in range(1, 11):
            self.assertIn(f"{number}.png", readme)
        self.assertIn("LOGO3.png", readme)
        self.assertIn("GitHub Pages", readme)


class WholeSiteTests(unittest.TestCase):
    html_files = [
        "index.html", "about.html", "insights.html", "insight-1.html", "insight-2.html",
        "insight-3.html", "insight-4.html", "insight-5.html", "faq.html", "contact.html",
    ]

    def test_all_local_links_resolve(self):
        for filename in self.html_files:
            html = read_required(filename)
            for href in re.findall(r'href="([^"]+)"', html):
                if href.startswith(("http://", "https://", "mailto:", "#")):
                    continue
                target = href.split("#", 1)[0]
                if not target:
                    continue
                if target.startswith("images/") and Path(target).name in {"LOGO3.png", *(f"{n}.png" for n in range(1, 11))}:
                    continue
                self.assertFalse(target.startswith("/"), f"Root-relative link in {filename}: {target}")
                self.assertTrue((ROOT / target).is_file(), f"Broken link in {filename}: {target}")

    def test_all_html_pages_use_shared_assets(self):
        for filename in self.html_files:
            html = read_required(filename)
            self.assertIn('href="css/style.css"', html, filename)
            self.assertIn('src="js/main.js"', html, filename)
            self.assertIn('href="images/LOGO3.png"', html, filename)

    def test_every_page_has_unique_required_seo(self):
        titles, descriptions, canonicals, og_urls = set(), set(), set(), set()
        for filename in self.html_files:
            html = read_required(filename)
            titles.add(re.search(r"<title>(.*?)</title>", html, re.S).group(1).strip())
            descriptions.add(re.search(r'<meta name="description" content="([^"]+)">', html).group(1))
            canonicals.add(re.search(r'<link rel="canonical" href="([^"]+)">', html).group(1))
            og_urls.add(re.search(r'<meta property="og:url" content="([^"]+)">', html).group(1))
            self.assertIn('<meta property="og:title"', html, filename)
            self.assertIn('<meta name="twitter:card"', html, filename)
        self.assertEqual(len(titles), len(self.html_files))
        self.assertEqual(len(descriptions), len(self.html_files))
        self.assertEqual(len(canonicals), len(self.html_files))
        self.assertEqual(canonicals, og_urls)

    def test_no_required_content_is_placeholder_text(self):
        forbidden = ("lorem ipsum", "todo", "coming soon", "replace this text")
        for filename in self.html_files:
            html = read_required(filename).lower()
            for phrase in forbidden:
                self.assertNotIn(phrase, html, f"{phrase} in {filename}")

    def test_html_heading_hierarchy(self):
        for filename in self.html_files:
            html = re.sub(r"<script\b.*?</script>", "", read_required(filename), flags=re.I | re.S)
            headings = [int(level) for level in re.findall(r"<h([1-6])\b", html, flags=re.I)]
            self.assertEqual(headings.count(1), 1, filename)
            previous = headings[0]
            for level in headings[1:]:
                self.assertLessEqual(level, previous + 1, f"Heading jump in {filename}: h{previous} to h{level}")
                previous = level

    def test_archive_file_manifest(self):
        archive = ROOT.parent / "VMA-Community-Website.zip"
        self.assertTrue(archive.is_file(), "Delivery ZIP has not been created")
        import zipfile
        with zipfile.ZipFile(archive) as bundle:
            names = set(bundle.namelist())
        for filename in self.html_files:
            self.assertIn(f"VMA-Community-Website/{filename}", names)
        self.assertIn("VMA-Community-Website/css/style.css", names)
        self.assertIn("VMA-Community-Website/js/main.js", names)
        self.assertIn("VMA-Community-Website/sitemap.xml", names)
        self.assertIn("VMA-Community-Website/robots.txt", names)

    def test_archive_matches_current_project_files(self):
        archive = ROOT.parent / "VMA-Community-Website.zip"
        self.assertTrue(archive.is_file(), "Delivery ZIP has not been created")
        import zipfile
        project_files = [
            *self.html_files,
            "css/style.css",
            "js/main.js",
            "sitemap.xml",
            "robots.txt",
            "README.md",
            "images/README.md",
            "tests/test_site.py",
        ]
        with zipfile.ZipFile(archive) as bundle:
            for filename in project_files:
                archived = bundle.read(f"VMA-Community-Website/{filename}")
                current = (ROOT / filename).read_bytes()
                self.assertEqual(archived, current, f"Stale file in delivery ZIP: {filename}")


if __name__ == "__main__":
    unittest.main()
