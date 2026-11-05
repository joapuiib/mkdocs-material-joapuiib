# Upstream PRs for `navigation.instant`

Proposed changes to third-party plugins, so the workarounds in this theme (see
`PLAN.md`) can eventually be removed.

**Status: proposals only.** The code below comes from reading the plugin sources
and the MaterialX 10.2.0 bundle. None of it has been built or run yet.

| Order | Plugin | Installed | Fix size | Replaces in this theme |
|---|---|---|---|---|
| 1 | [`tuunit/mkdocs-drawio`](https://github.com/tuunit/mkdocs-drawio) | 1.16.3 | ~25 lines of JS, ~5 of Python | `templates/javascript/drawio.js` |
| 2 | [`blueswen/mkdocs-glightbox`](https://github.com/blueswen/mkdocs-glightbox) | 0.5.3 | ~2 lines of Python and a test | `templates/javascript/glightbox.js` |

`mkdocs-drawio` goes first: its problem is bigger and its maintainer merges and
releases regularly. `mkdocs-glightbox` reviews are slow (#70 has had no review since
March 2026; #81 and #82 have no comments yet).

## Background

On each navigation, instant navigation swaps a fixed list of components, including
`container`, and diffs the `head` children. Scripts added to `head` or placed at the
end of `body` don't run; only scripts inside `container` run again. It then emits
`document$`.

Both plugins add their library outside `container`, and only on some pages. If the
first page loaded doesn't include it, later pages have no library.

## PR 1: `mkdocs-drawio`

### Problem

- The viewer is added at the end of `body`, only on pages with diagrams.
- It renders once, when it loads, so diagrams on later pages stay blank.

Issue [#11](https://github.com/tuunit/mkdocs-drawio/issues/11) was closed with a
workaround in the README, which has these problems:

- It loads the viewer on every page, and that file is 4.9 MB.
- `GraphViewer.processElements()` clears and rebuilds every diagram on each
  `document$` emission.
- The snippet calls `reload()`, which it never defines, so it probably throws an
  error. Confirm this in a browser before mentioning it in the PR.

### Fix

Make it work without configuration when `navigation.instant` is enabled. The viewer
loads only when a page needs it, and each diagram renders once.

`mkdocs_drawio/plugin.py`:

```python
# on_config, after self.js = []
# self.js is already copied and registered, but currently empty.
if "navigation.instant" in config.theme.get("features", []):
    self.js.append("js/drawio-instant.js")

# render_drawio_diagrams, before the loop
viewer_url = normalize_url(self.config.viewer_js, page)
lib = soup.new_tag("script", src=viewer_url)
soup.body.append(lib)

# render_drawio_diagrams, just before diagram.replace_with(mxgraph_soup)
# Page-relative, which keeps viewer_js working with mike.
mxgraph_soup.find("div")["data-viewer-js"] = viewer_url
```

`mkdocs_drawio/js/drawio-instant.js`:

```js
(function () {
  "use strict";

  var loading = false;

  function render() {
    document.querySelectorAll(".mxgraph[data-mxgraph]:not([data-drawio-rendered])").forEach(function (el) {
      el.dataset.drawioRendered = "true";
      try {
        el.innerText = "";
        GraphViewer.createViewerForElement(el);
      } catch (error) {
        el.innerText = error.message;
        console.error(error);
      }
    });
  }

  // Called by the viewer when it loads, instead of rendering every diagram.
  window.onDrawioViewerLoad = render;

  document$.subscribe(function () {
    if (window.GraphViewer) {
      render();
      return;
    }
    var diagram = document.querySelector(".mxgraph[data-viewer-js]");
    if (diagram && !loading) {
      loading = true;
      var script = document.createElement("script");
      script.src = diagram.dataset.viewerJs;
      document.body.appendChild(script);
    }
  });
})();
```

`README.md`: replace the instant loading part of "Material Integration" with a note
that it works automatically.

### Things to check

- [ ] The new `js/` directory is included in the built package.
- [ ] The viewer isn't loaded twice on a first load, given that the plugin's own
      `<script>` is still at the end of `body`.
- [ ] The README's `minWidth` tip still applies; it's currently part of the snippet
      being removed.
- [ ] The separate "Using Tabs" snippet in the README still works.
- [ ] Diagrams loaded from a URL don't appear twice, which is what the README's
      `reload()` comment describes.
- [ ] A relative `viewer_js` works from pages at different depths.
- [ ] Sites without `navigation.instant` produce the same output, apart from the new
      `data-viewer-js` attribute.

### Points for the PR description

- `window.onDrawioViewerLoad` exists in `viewer-static.min.js`, but I found no
  documentation for it, so a viewer update could break it.
- The repo has no test directory, so describe the manual verification and add the
  feature to an example config if that helps review.

## PR 2: `mkdocs-glightbox`

### Problem

`on_post_page` returns early on pages with `glightbox: false`, so they don't get the
library or the init script. If one of those is the first page loaded, later pages
have `.glightbox` links but no library.

### Fix

Images are wrapped separately, in `on_page_content`, and that check doesn't change.
With instant navigation, pages with `glightbox: false` can load the library and still
leave their images alone.

`mkdocs_glightbox/plugin.py`:

```python
def on_post_page(self, output, page, config, **kwargs):
    instant = "navigation.instant" in config["theme"].get("features", [])
    # skip page with meta glightbox is false, unless a later page may need the
    # library: instant navigation doesn't run scripts added after the first load
    if page.meta.get("glightbox", True) is False and not instant:
        return output
```

The existing `document$` check further down can reuse `instant`.

### Test

Add a test to `tests/test_builds.py` that builds the `disable_by_page` page with
`tests/fixtures/mkdocs-material-instant.yml` and checks that:

- `glightbox.min.js` and `#init-glightbox` are present.
- The images aren't wrapped (`validate_lightbox_wrap_disable`).

The existing `test_disable_by_page` covers the case without instant navigation.

### Things to check

- [ ] Going from a `glightbox: false` page to a normal page opens the lightbox.
- [ ] Going from a normal page to a `glightbox: false` page leaves its images alone.
- [ ] Decide on `404.html`, which doesn't go through `on_post_page`, so a visit
      starting there still has no library. Either mention this in the PR or also
      handle it with `on_post_template`.

### Points for the PR description

- Mention [#70](https://github.com/blueswen/mkdocs-glightbox/pull/70), which edits the
  same function and claims instant support, but keeps this early return and so doesn't
  fix this bug. The two may conflict.

### Setup

The local checkout at `~/mkdocs/mkdocs-glightbox` only has the fork as a remote, and
its `main` looks out of date. Branch from upstream, not from
`fix/auto-height-description`:

```bash
git remote add upstream https://github.com/blueswen/mkdocs-glightbox.git
git fetch upstream
git switch -c fix/instant-disabled-page upstream/main
```

## Verification

Check each fix in a real browser (headless Chromium), in three ways:

1. Loading the page directly.
2. Arriving through instant navigation.
3. Arriving with the back and forward buttons.

Also check that a second `document$` emission on the same page doesn't render anything
twice. Unlocking protected content in this theme triggers one.

## After the releases

- [ ] Raise the minimum versions in `material_joapuiib/requirements.txt`.
- [ ] Remove `drawio.js` and `glightbox.js` from `templates/javascript/`, and their
      lines from `templates/theme-base.html`. Keep the `glightbox.js` reload guard if
      the `404.html` gap wasn't fixed upstream.
- [ ] Delete this file.

## Not part of these PRs

`mkdocs-glightbox` only adds its dark-mode CSS when the theme is named exactly
`material`, so `material-joapuiib` doesn't get it. #70 only adds `materialx`, so it
wouldn't cover this theme either. This is a separate issue.
