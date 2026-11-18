## Why

The fork's beta publisher requires a personal access token and creates a public release before its artifacts pass validation. Its tag and release events can both start publication with the default PyPI settings.

## What changes

Use the repository workflow token to tag a validated merge and explicitly dispatch the artifact workflow at that tag with PyPI skipped for the fork. The upstream dispatch continues to publish to PyPI. The artifact workflow owns final GitHub prerelease creation.
