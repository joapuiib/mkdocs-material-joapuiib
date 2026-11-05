# Support `navigation.instant`

Goal: every theme feature and bundled plugin keeps working when a site enables
`navigation.instant`, and works the same as on a full page load.

## How instant navigation works

On each navigation the MaterialX bundle fetches the page and then:

- Replaces `container`, `announce`, `header-topic`, `outdated`, `logo` and `skip`.
  The rest of the header and everything else in `body` stay in place.
- Compares `head` children: new ones are added and missing ones removed. Added
  stylesheets and meta tags apply, but added scripts do not run.
- Re-runs only the scripts inside `container`.
- Emits `document$`.

So anything in `{% block scripts %}`, or appended to the end of `body`, runs only
on the first page load. Page setup has to subscribe to `document$`, or use
delegated listeners.

## Status

### Theme

| Feature | Problem | Fix | Status |
|---|---|---|---|
| Calendar tooltips | Cells are bound once; a pinned tooltip survives navigation | Bind through `document$`, once per cell; reset state on each run | Todo |
| Giscus palette sync | Listener waits for `DOMContentLoaded`; throws without a frame | One delegated `change` listener, tolerating a missing frame | Todo |
| Per-page `extra_javascript` | Tags are in `block scripts` | List them inside `container`; a loader adds those not loaded yet | Todo |
| Slides, entering | Reveal.js never loads | Force a full reload when the slides container is swapped in | Todo |
| Slides, leaving | Custom header, nav and footer stay | Remove `navigation.instant*` from the features on slides pages | Todo |

### Plugins

| Plugin | Problem | Fix | Status |
|---|---|---|---|
| `drawio` | Viewer is at the end of `body`; diagrams stay blank | Theme script loads the viewer on demand and renders new diagrams | Todo |
| `glightbox` | No library if the first page has `glightbox: false` | Reload when lightbox links exist but the library is missing | Todo |

`search`, `tags`, Mermaid, `alias`, `awesome-nav`, `exclude-search`, `macros` and
`git-revision-date-localized` need no changes.

`i18n` needs no changes either: its switcher reconfiguration only runs for a theme
named `material`, so here `extra.alternate` is static site-wide configuration.

### Related: repeated `document$` emissions

Unlocking protected content calls `document$.next(document)`, so subscribers also
run again on a page that was not replaced.

| Feature | Problem | Fix | Status |
|---|---|---|---|
| Carousel | Duplicate controls | Set up each carousel once | Todo |
| Tablesort | Second instance on the same table | Set up each table once | Todo |

## Verification

No browser tests exist in the repo, so this is checked by hand with a temporary
config that enables the feature (headless Chromium, not committed). Check each
feature in three ways:

1. Loading the page directly.
2. Arriving through instant navigation.
3. Arriving with the back and forward buttons.

Giscus needs a production build and a configured repository, so it may only be
partly testable locally.

## Remaining

- [ ] Implement the fixes above
- [ ] Browser verification
- [ ] Document the feature in `docs/` (in Valencian, using `apunts:redaccio`)
- [ ] Decide whether `navigation.instant` stays opt-in or joins the defaults in
      `mkdocs_theme.yml`
- [ ] Delete this file before merging
