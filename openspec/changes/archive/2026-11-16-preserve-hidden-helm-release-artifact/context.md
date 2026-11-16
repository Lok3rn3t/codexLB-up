# Evidence

Release attempt 43843120520, Helm job 133217053409, logged a successfully
packaged `.helm-pkg/codex-lb-1.25.0.tgz` and successful GHCR push. The artifact
step then reported `include-hidden-files: false` and no matching files. Its
default missing-file behavior was a warning, so downstream publication would
have had no chart artifact to download.

The fix enables hidden-file inclusion only for the explicit `.helm-pkg/*.tgz`
selection and makes missing files an error. It does not expand the upload to
unrelated hidden files. The incomplete attempt was canceled before PyPI and
GitHub publication; the release must be rebuilt with the corrected workflow.
