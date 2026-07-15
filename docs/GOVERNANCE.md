# Repository governance

A small set of rules that keep the docs and the file tree from turning into a mess as
features pile up. These are cheap to follow now and expensive to retrofit later. Most are
enforced automatically in CI (see [`.github/workflows/build-resumes.yml`](../.github/workflows/build-resumes.yml)).

## 1. One documentation directory

There is exactly **one** docs directory: `docs/`. **Never** create a `doc/` (singular).

- Cross-cutting guides, plans, schemas → `docs/`.
- Package-specific docs → that package's own `README.md` (next to the code).
- User-facing overview → root `README.md` / `README.zh-CN.md`.

> **Enforced:** CI fails if a `doc/` directory reappears in the tree.

## 2. Every doc is indexed

Every file added under `docs/` must be listed in [`docs/README.md`](README.md). The index is
the entry point; an unlisted doc is an orphan nobody will find. If you add `docs/foo.md`,
add its row in the same PR.

## 3. Docs live close to what they describe

Prefer documenting a thing where it lives. A package's quirks belong in that package's
`README.md`, not in a distant `docs/` note that drifts out of sync. Reserve `docs/` for
things that span multiple packages (build setup, roadmap, schemas, the Skill).

## 4. No personal data in the public repo

Examples use placeholders only: `YOUR_NAME`, `your-email@example.com`, `(+86) 138-0000-0000`.
Real resumes, the experience bank, tracker output, and history are gitignored. Do not commit
anything that identifies a real person.

> **Enforced (partial):** the sample resume and example bank ship depersonalized; `.gitignore`
> covers `outputs/`, `history/`, `docs/experience_bank.md`, and personal `.tex` variants.

## 5. Attribution stays in one place per document

The upstream LaTeX template is acknowledged **once, at the end** of the relevant Markdown
docs (root `README.md`, `README.zh-CN.md`, and `resume_template/README.md`). Elsewhere, refer
to it generically as "the LaTeX template" — don't scatter upstream project/author names
through prose, so readers aren't burdened with attribution noise mid-document.

## 6. Tests stay green, new adapters get tests

`pytest` must pass before merge. A new conversion adapter or site adapter ships with a test
under `convert/tests/` or `apply/tests/`. CI compiles the sample resume on every push/PR.

---

*Adding a rule here? Keep it short, say why it exists, and note whether/how it's enforced.*
