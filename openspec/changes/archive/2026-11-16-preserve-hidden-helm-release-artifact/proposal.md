## Why

The release job successfully pushed its chart to GHCR but upload-artifact ignored
the archive inside `.helm-pkg` because hidden paths are excluded by default.
The job incorrectly reported success without the artifact required by the
GitHub Release job.

## What Changes

- Explicitly include the selected hidden chart path in artifact upload.
- Fail the job when the chart artifact is missing.
- Verify the final GitHub Release contains the chart and checksums.

## Impact

Release workflow only. Application code, database migrations and deployment
configuration are unchanged. The first stable attempt was canceled before
PyPI or GitHub publication.
