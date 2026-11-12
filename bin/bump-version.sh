#!/usr/bin/env bash
# Bump the project version, commit, and tag it.
#
# Usage: bin/bump-version.sh [major|minor|patch] [-p|--push] [-r|--release] [-f|--force] [-n|--new-commit] [--dry]
#        bin/bump-version.sh release [VERSION]
#
# After pushing, it offers to create a GitHub release whose notes are written
# by Claude Code (`claude -p`) from the commits since the previous tag. The
# notes are shown for review before publishing. Pass -r/--release to skip the
# "create release?" question. Requires the `claude` and `gh` CLIs.
#
# `release [VERSION]` skips the bump and only writes the release for an
# existing tag (default: the current version). If the release already exists,
# its notes are replaced after review.
#
# By default, if HEAD has no tag pointing at it, the version bump is folded
# into HEAD via `git commit --amend`. Pass -n/--new-commit to always create a
# separate commit instead. If HEAD already has a tag, a new commit is always
# created (amending a tagged commit would orphan the tag).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VERSION_FILE="$REPO_ROOT/material_joapuiib/__init__.py"
REPO_URL="https://github.com/joapuiib/mkdocs-material-joapuiib"
DOCS_URL="https://joapuiib.github.io/mkdocs-material-joapuiib"

# ---------------------------------------------------------------------------
# UI helpers
# ---------------------------------------------------------------------------
if [ -t 1 ]; then
    BOLD=$'\e[1m' DIM=$'\e[2m' RED=$'\e[1;31m' GREEN=$'\e[1;32m'
    YELLOW=$'\e[1;33m' BLUE=$'\e[1;34m' RESET=$'\e[0m'
else
    BOLD="" DIM="" RED="" GREEN="" YELLOW="" BLUE="" RESET=""
fi

info() { echo "${BLUE}[bump]${RESET} $*"; }
ok()   { echo "${GREEN}✔${RESET} $*"; }
skip() { echo "${YELLOW}-${RESET} $*"; }
hint() { echo "  ${DIM}$*${RESET}"; }
err()  { echo "${RED}[bump] ERROR:${RESET} $*" >&2; }
die()  { err "$*"; exit 1; }

# Full-width banner so each step's output is easy to spot when scrolling.
banner() {
    local text=" $1 " cols line
    cols="$(tput cols 2>/dev/null || echo 80)"
    [ "$cols" -gt 80 ] && cols=80
    printf -v line '%*s' $(( cols - ${#text} - 4 )) ''
    echo
    echo "${BLUE}━━━${BOLD}${text}${RESET}${BLUE}${line// /━}${RESET}"
}

# Aligned "label  value" row, used by the plan and the summary.
row() { printf "  ${DIM}%-9s${RESET} %s\n" "$1" "$2"; }

# confirm <question>: true if the user answers yes.
confirm() {
    local reply
    read -r -p "${BOLD}?${RESET} $1 ${DIM}[y/N]${RESET} " reply
    [[ "$reply" =~ ^[yY]([eE][sS])?$ ]]
}

# spin <pid> <message>: shows a spinner until <pid> exits, returns its status.
spin() {
    local pid="$1" msg="$2" frames='⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏' i=0
    if [ ! -t 1 ]; then
        info "$msg"
    else
        while kill -0 "$pid" 2>/dev/null; do
            printf '\r%s %s' "${BLUE}${frames:i++%${#frames}:1}${RESET}" "$msg"
            sleep 0.1
        done
        printf '\r\e[K'
    fi
    wait "$pid"
}

# Step results, shown in the final summary: "mark|label|detail".
RESULTS=()
record() { RESULTS+=("$1|$2|$3"); }

summary() {
    [ ${#RESULTS[@]} -gt 0 ] || return 0
    banner "Summary"
    local r mark label detail
    for r in "${RESULTS[@]}"; do
        IFS='|' read -r mark label detail <<< "$r"
        printf "  %s %-9s %s\n" "$mark" "$label" "$detail"
    done
}

usage() {
    cat <<USAGE
Usage: $(basename "$0") <major|minor|patch> [options]
       $(basename "$0") release [VERSION]

Bump the version in material_joapuiib/__init__.py, commit, tag, push and
publish a GitHub release with notes written by Claude.

Commands:
  major|minor|patch   Part of the version to bump
  release [VERSION]   Only write the GitHub release for an existing tag
                      (default: the current version)

Options:
  -p, --push          Push without asking
  -r, --release       Create the GitHub release without asking
  -f, --force         Skip the confirmation before bumping
  -n, --new-commit    Always create a separate commit instead of amending HEAD
      --dry           Show the plan and exit without changes
  -h, --help          Show this help
USAGE
}

usage_error() { err "$1"; echo >&2; usage >&2; exit 1; }

# ---------------------------------------------------------------------------
# Arguments
# ---------------------------------------------------------------------------
BUMP=""
PUSH=""
RELEASE=""
FORCE=""
DRY=""
NEW_COMMIT=""
RELEASE_ONLY=""
RELEASE_VERSION=""

for arg in "$@"; do
    case "$arg" in
        major|minor|patch) BUMP="$arg" ;;
        release)           RELEASE_ONLY="yes" ;;
        v[0-9]*.*.*|[0-9]*.*.*)
            [[ -n "$RELEASE_ONLY" ]] || usage_error "A version is only accepted after 'release'."
            RELEASE_VERSION="${arg#v}"
            ;;
        -p|--push)       PUSH="yes" ;;
        -r|--release)    RELEASE="yes" ;;
        -f|--force)      FORCE="yes" ;;
        -n|--new-commit) NEW_COMMIT="yes" ;;
        --dry)           DRY="yes" ;;
        -h|--help)       usage; exit 0 ;;
        *)               usage_error "Unknown argument '$arg'." ;;
    esac
done

cd "$REPO_ROOT"

current_version() { grep -oP "(?<=__version__ = ')[^']+" "$VERSION_FILE"; }

# ---------------------------------------------------------------------------
# GitHub release
# ---------------------------------------------------------------------------
create_release() {
    if ! command -v claude >/dev/null || ! command -v gh >/dev/null; then
        skip "Skipped release: the 'claude' and 'gh' CLIs are required."
        record "${YELLOW}-${RESET}" "Release" "skipped (claude or gh missing)"
        return
    fi

    local exists=""
    if gh release view "$TAG" >/dev/null 2>&1; then
        exists="yes"
        if ! confirm "GitHub release $TAG already exists. Write new notes for it?"; then
            skip "Kept the existing release $TAG."
            record "${YELLOW}-${RESET}" "Release" "kept existing $TAG"
            return
        fi
    fi

    local prev_tag range notes_file highlights_file err_file prompt
    prev_tag="$(git describe --tags --abbrev=0 "$TAG^" 2>/dev/null || true)"
    range="${prev_tag:+$prev_tag..}$TAG"
    notes_file="$(mktemp --suffix=.md)"
    highlights_file="$(mktemp --suffix=.md)"
    err_file="$(mktemp)"

    prompt="Write the highlights of the GitHub release notes for $TAG of mkdocs-material-joapuiib, \
a custom MkDocs Material theme (plugins, Markdown extensions and styles) for course notes written in Valencian. \
The commits${prev_tag:+ since $prev_tag}, the changed files and the diff of the documentation are provided on stdin. \
Output only a Markdown bullet list, with no preamble, no title and no headings. \
Write one bullet per user-facing change, merging related commits: start it with a short bold summary, \
then ' — ' and one or two sentences on what changed for the theme's users. \
Put options, admonition types, CSS classes and file names in backticks. \
When a change is documented, end its bullet with a link like [Admonitions docs]($DOCS_URL/features/admonitions/), \
where docs/<path>.md is published at $DOCS_URL/<path>/. \
Leave out internal changes (tests, refactors, CI, version bumps). Write in English."

    {
        echo "Commits:"
        git log --no-merges --format='- %s%n%b' "$range"
        echo "Changed files:"
        if [[ -n "$prev_tag" ]]; then
            git diff --stat "$prev_tag" "$TAG"
            echo "Documentation diff:"
            git diff "$prev_tag" "$TAG" -- docs README.md
        fi
    } | claude -p "$prompt" --tools "" > "$highlights_file" 2> "$err_file" &
    spin $! "Writing release notes for $TAG${prev_tag:+ (since $prev_tag)} with Claude..." || true

    if [[ ! -s "$highlights_file" ]]; then
        err "Could not generate release notes."
        [[ -s "$err_file" ]] && sed 's/^/  /' "$err_file" >&2
        hint "Run 'gh release create $TAG --generate-notes' instead."
        record "${RED}✘${RESET}" "Release" "notes generation failed"
        rm -f "$notes_file" "$highlights_file" "$err_file"
        return
    fi
    ok "Release notes written."

    {
        echo "## Highlights"
        echo
        cat "$highlights_file"
        if [[ -n "$prev_tag" ]]; then
            echo
            echo "**Full Changelog**: $REPO_URL/compare/$prev_tag...$TAG"
        fi
    } > "$notes_file"
    rm -f "$highlights_file" "$err_file"

    local question reply
    if [[ -n "$exists" ]]; then
        question="Replace the notes of GitHub release $TAG with these?"
    else
        question="Publish GitHub release $TAG with these notes?"
    fi

    while true; do
        banner "Release notes $TAG"
        cat "$notes_file"
        echo
        read -r -p "${BOLD}?${RESET} $question ${DIM}[y]es/[e]dit/[N]o${RESET} " reply
        case "$reply" in
            [yY]|[yY][eE][sS])
                if [[ -n "$exists" ]]; then
                    gh release edit "$TAG" --notes-file "$notes_file" >/dev/null
                    ok "Updated the notes of release $TAG."
                    record "${GREEN}✔${RESET}" "Release" "notes updated: $REPO_URL/releases/tag/$TAG"
                else
                    gh release create "$TAG" --verify-tag --title "$TAG" --notes-file "$notes_file" >/dev/null
                    ok "Published release $TAG."
                    record "${GREEN}✔${RESET}" "Release" "$REPO_URL/releases/tag/$TAG"
                fi
                hint "$REPO_URL/releases/tag/$TAG"
                break
                ;;
            [eE]|[eE][dD][iI][tT])
                "${EDITOR:-vi}" "$notes_file"
                ;;
            *)
                skip "Skipped release."
                hint "Run '$(basename "$0") release ${TAG#v}' when ready."
                record "${YELLOW}-${RESET}" "Release" "skipped"
                break
                ;;
        esac
    done
    rm -f "$notes_file"
}

# ---------------------------------------------------------------------------
# release [VERSION]
# ---------------------------------------------------------------------------
if [[ -n "$RELEASE_ONLY" ]]; then
    [[ -z "$BUMP" ]] || usage_error "'release' can't be combined with '$BUMP'."
    RELEASE_VERSION="${RELEASE_VERSION:-$(current_version)}"
    TAG="v$RELEASE_VERSION"
    git rev-parse -q --verify "refs/tags/$TAG" >/dev/null || die "Tag $TAG does not exist."
    banner "Release $TAG"
    create_release
    summary
    exit 0
fi

# ---------------------------------------------------------------------------
# Bump
# ---------------------------------------------------------------------------
[[ -n "$BUMP" ]] || usage_error "Missing the part to bump (major, minor or patch)."

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
[[ "$BRANCH" == "main" ]] || die "Must be on 'main' branch (currently on '$BRANCH')."
[[ -z "$(git status --porcelain)" ]] || die "Working tree not clean. Commit or stash changes first."

CURRENT_VERSION="$(current_version || true)"
[[ -n "$CURRENT_VERSION" ]] || die "Could not find __version__ in $VERSION_FILE."

IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT_VERSION"
case "$BUMP" in
    major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
    minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
    patch) PATCH=$((PATCH + 1)) ;;
esac

NEW_VERSION="$MAJOR.$MINOR.$PATCH"
TAG="v$NEW_VERSION"

! git rev-parse "$TAG" >/dev/null 2>&1 || die "Tag $TAG already exists."

if [[ -n "$NEW_COMMIT" ]] || [[ -n "$(git tag --points-at HEAD)" ]]; then
    MODE="new"
else
    MODE="amend"
fi

PREV_TAG="$(git describe --tags --abbrev=0 2>/dev/null || true)"

banner "Bump $BUMP"
row "Version" "$CURRENT_VERSION → ${BOLD}$NEW_VERSION${RESET}"
row "Tag" "$TAG"
if [[ "$MODE" == "amend" ]]; then
    row "Commit" "amend $(git log -1 --format='%h %s')"
else
    row "Commit" "new: chore: bump version to $NEW_VERSION"
fi
if [[ -n "$PREV_TAG" ]]; then
    echo
    echo "  ${DIM}Commits since $PREV_TAG:${RESET}"
    git log --no-merges --format="    %C(yellow)%h%C(reset) %s" --color="$([ -t 1 ] && echo always || echo never)" "$PREV_TAG..HEAD"
fi
echo

if [[ -n "$DRY" ]]; then
    skip "Dry run: no changes made."
    exit 0
fi

if [[ -z "$FORCE" ]] && ! confirm "Proceed with bump, commit and tag?"; then
    skip "Aborted."
    exit 1
fi

trap summary EXIT

sed -i "s/__version__ = '$CURRENT_VERSION'/__version__ = '$NEW_VERSION'/" "$VERSION_FILE"
git add "$VERSION_FILE"
if [[ "$MODE" == "amend" ]]; then
    ORIG_MSG="$(git log -1 --pretty=%B)"
    git commit --quiet --amend -m "$ORIG_MSG

Bump version to $NEW_VERSION."
else
    git commit --quiet -m "chore: bump version to $NEW_VERSION"
fi
ok "Bumped version to $NEW_VERSION ($MODE commit $(git rev-parse --short HEAD))."
record "${GREEN}✔${RESET}" "Commit" "$CURRENT_VERSION → $NEW_VERSION ($MODE, $(git rev-parse --short HEAD))"

git tag -a "$TAG" -m "$TAG"
ok "Created tag $TAG."
record "${GREEN}✔${RESET}" "Tag" "$TAG"

# ---------------------------------------------------------------------------
# Push
# ---------------------------------------------------------------------------
banner "Push"
if [[ -z "$PUSH" ]]; then
    confirm "Push main and $TAG to origin?" && PUSH="yes" || PUSH="no"
fi

if [[ "$MODE" == "amend" ]]; then
    PUSH_MAIN=(git push --force-with-lease origin main)
else
    PUSH_MAIN=(git push origin main)
fi

if [[ "$PUSH" == "yes" ]]; then
    "${PUSH_MAIN[@]}"
    git push origin "$TAG"
    ok "Pushed main and $TAG."
    record "${GREEN}✔${RESET}" "Push" "main and $TAG"
else
    skip "Skipped push."
    hint "Run '${PUSH_MAIN[*]} && git push origin $TAG' when ready."
    record "${YELLOW}-${RESET}" "Push" "skipped"
    exit 0
fi

# ---------------------------------------------------------------------------
# Release
# ---------------------------------------------------------------------------
banner "Release"
if [[ -z "$RELEASE" ]]; then
    confirm "Create GitHub release with notes written by Claude?" && RELEASE="yes"
fi

if [[ -n "$RELEASE" ]]; then
    create_release
else
    skip "Skipped release."
    hint "Run '$(basename "$0") release $NEW_VERSION' when ready."
    record "${YELLOW}-${RESET}" "Release" "skipped"
fi
