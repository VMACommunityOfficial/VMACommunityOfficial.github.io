# VMA Community Website

A complete English-language static website built with HTML, CSS and vanilla JavaScript for GitHub Pages.

## Publish with GitHub Pages

1. Upload the contents of this project to the repository used by `VMACommunityOfficial.github.io`.
2. Keep the existing folder structure, including `css`, `js` and `images`.
3. In the repository settings, enable GitHub Pages from the production branch and root directory.
4. Confirm that `https://VMACommunityOfficial.github.io/` loads and that `sitemap.xml` is accessible.

## Add the image files

Upload the supplied PNG files to the `images` directory without renaming them:

- `1.png`
- `2.png`
- `3.png`
- `4.png`
- `5.png`
- `6.png`
- `7.png`
- `8.png`
- `9.png`
- `10.png`
- `LOGO3.png` — favicon

The responsive image containers preserve proportions and show a styled fallback while an image is missing. Do not add extra folders or change the filenames, because the HTML references these exact relative paths.

## Project pages

- Home: `index.html`
- About: `about.html`
- Insights index: `insights.html`
- Articles: `insight-1.html` through `insight-5.html`
- FAQ: `faq.html`
- Contact: `contact.html`

## Validate locally

Run `python3 -m unittest discover -s tests -v` from this directory. To preview the site, run `python3 -m http.server 8000` and open `http://localhost:8000/`.
