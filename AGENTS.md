# Prismo repository instructions

Preserve the six operations (`init`, `foundations`, `tokens`, `create`, `document`,
`audit`), the existing architecture, and documented experimental limitations.
Do not modify POCs or add product functionality as part of release administration.

## Commit policy

AI-created commits must follow [Conventional Commits 1.0.0](https://www.conventionalcommits.org/en/v1.0.0/).
Write the entire commit message in English. Every commit requires:

1. A title in the form `type(scope): description`, or `type: description` when no
   scope helps. Use a specific, imperative description. Use `feat`, `fix`, `docs`,
   `refactor`, `test`, `chore`, or `ci` according to the actual change. Mark genuine
   breaking changes with the Conventional Commits notation and explain the impact.
2. A nonempty body explaining what changed and why, separated from the title by
   one blank line. Generic titles or bodies are not acceptable.
3. A `Co-authored-by: Name <email>` trailer, separated from the body by a blank
   line, using the AI identity explicitly authorized by the user. This is a format
   template, not an identity to copy into a commit.

Keep the user's configured Git identity as the author. Do not replace the author
with the AI, set AI author environment variables, use `--author` for the AI, or
rewrite `user.name`/`user.email`. Check the effective author before committing;
if the user's author identity is missing, request a valid configuration.

Use an explicitly authorized AI identity from the current session or the repository
local Git setting `prismo.aiCoauthor`. Do not invent names, email addresses, or
noreply accounts, or infer authorization from an address found in unrelated files.
If no authorized AI identity is available, request it and stop before creating a
commit. Record a user-approved reusable identity only in local Git configuration,
not as a fabricated default in this file. The coauthor must not substitute for the
user's author identity.

Make small, coherent commits grouped by purpose. Do not mix unrelated changes,
fabricate historical development stages, amend someone else's work, or rewrite
published history. Prismo has not previously been versioned: its first commit must
capture the approved stabilized initial state, including release metadata and this
policy, as one baseline. Do not manufacture earlier feature/fix commits.

Before each commit:

- Inspect the working tree and review the complete staged diff and file list.
- Check whitespace errors, relevant validation results, and the exact message,
  including the nonempty body and authorized coauthor trailer.
- Exclude credentials, local settings, caches, temporary files, generated outputs,
  dependencies, and other unnecessary artifacts. Inspect staged content as well
  as filenames; a `.gitignore` entry alone does not prove safety.
- Stage only reviewed paths. Do not bypass failing checks or hooks to commit.
- Verify the resulting author, message, trailer, and committed file list.

## Release publication

Use the approved experimental version and an annotated, unused tag. Preserve
experimental limitations in the release notes and publish experimental releases
with GitHub's pre-release flag. Before creating a public remote or publishing,
present the exact owner/repository, visibility, version, and reviewed file scope,
and report the sensitive/unwanted-file review. Obtain explicit approval of that
concrete public destination before the external publication actions.

Do not force-push, reuse tags, overwrite a remote history, or claim publication
without verifying the remote commit, annotated tag, and GitHub Release URL.
