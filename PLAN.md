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
| Calendar tooltips | Cells are bound once; a pinned tooltip survives navigation | Bind through `document$`, once per cell; reset state on each run | Done |
| Giscus palette sync | Listener waits for `DOMContentLoaded`; throws without a frame | One delegated `change` listener, tolerating a missing frame | Done |
| Access | Material re-runs the JSON payload `<script>` as JavaScript and drops its class, so pages never unlock | Move the payload to a `data-access-payload` attribute | Done |
| Per-page `extra_javascript` | Tags are in `block scripts` | List them inside `container`; a loader adds those not loaded yet | Done |
| Slides, entering | Reveal.js never loads | Force a full reload when the slides container is swapped in | Done |
| Slides, back button | After the reload, the URL changes but the slides stay | Reload on `popstate` when the path differs | Done |
| Slides, leaving | Custom header, nav and footer stay | Remove `navigation.instant*` from the features on slides pages | Done |

### Plugins

The theme scripts `javascript/drawio.js` and `javascript/glightbox.js` are temporary
workarounds. Remove them, and their tags in `theme-base.html`, once new plugin
versions with instant navigation support are released (see `PR.md`).

| Plugin | Problem | Fix | Status |
|---|---|---|---|
| `drawio` | Viewer is at the end of `body`; diagrams stay blank | Theme script loads the viewer on demand and renders new diagrams | Done |
| `glightbox` | No library if the first page has `glightbox: false` | Reload when lightbox links exist but the library is missing | Done |

`search`, `tags`, Mermaid, `alias`, `awesome-nav`, `exclude-search`, `macros` and
`git-revision-date-localized` need no changes.

`i18n` needs no changes either: its switcher reconfiguration only runs for a theme
named `material`, so here `extra.alternate` is static site-wide configuration.

### Related: repeated `document$` emissions

Unlocking protected content calls `document$.next(document)`, so subscribers also
run again on a page that was not replaced.

| Feature | Problem | Fix | Status |
|---|---|---|---|
| Carousel | Duplicate controls | Set up each carousel once | Done |
| Tablesort | Second instance on the same table | Set up each table once | Done |

## Known issues outside instant navigation

- Comments never render: `partials/comments.html` checks `page_is_page`, which
  nothing defines. Probably meant to be `page.is_page`. Fixing it would make
  comments appear on sites that already set `comments: true`.
- Draw.io diagrams in protected content stay as plain images, even on a direct
  load: the plugin's `on_post_page` runs after the content is encrypted, so it never
  sees them. `PR.md` may need updating if the plugin fix should cover this.
- `.venv` can have outdated plugin metadata, which makes `properdocs build` fail with
  "`material-joapuiib/access` plugin is not installed". Reinstalling the package
  should fix it. The tests worked around this without changing `.venv`.

## Verification

No browser tests exist in the repo, so this is checked by hand with a temporary
config that enables the feature (headless Chromium, not committed). Check each
feature in three ways:

1. Loading the page directly.
2. Arriving through instant navigation.
3. Arriving with the back and forward buttons.

Result: 45 of 46 checks pass. The failure is the protected diagram issue above, which
also happens on a direct load. Giscus was tested with a stubbed client and frame, and
with `page_is_page` defined in a temporary hook, not against the real service.

Not fully covered yet:

- Back and forward buttons: only tested for slides and `drawio`.
- Not tested in a browser: xref tooltips, the print title, Mermaid and search.
- Giscus: not tested against the real service.
- The test site lives outside the repo and left out `git-revision-date-localized`.

Bugs the browser checks caught, which reading the code had missed or got wrong:

- Access was first assessed as working, but protected pages could never unlock under
  instant navigation.
- The first slides fix left the slides on screen when going back.
- Comments were first assessed as still loading, but they never render at all.

## Open questions

1. Fix the comments bug? It is a one-line change, but comments would appear on any
   site that already sets `comments: true`, so it should be a separate commit.
2. Make `navigation.instant` a default? Recommendation: keep it opt-in until the
   remaining checks pass and the plugin releases are out, since a default would change
   behaviour for every site using the theme.

## Remaining

- [x] Implement the fixes above
- [x] Browser verification of the main fixes
- [ ] Finish the browser checks listed under "Not fully covered yet"
- [ ] Document the feature in `docs/` (in Valencian, using `apunts:redaccio`)
- [ ] Remove the plugin workarounds once new versions are released
- [ ] Answer the open questions
- [ ] Delete this file before merging
