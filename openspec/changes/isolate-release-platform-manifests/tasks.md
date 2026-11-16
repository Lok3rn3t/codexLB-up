## 1. Fix and verify platform selection

- [x] 1.1 Confirm the failure is an index-reference collision after successful amd64 startup.
- [x] 1.2 Resolve immutable executable child manifests and use them in release gates.
- [x] 1.3 Cover valid selection, attestations, and missing or ambiguous platforms; pass lint and strict OpenSpec validation.
- [ ] 1.4 Verify both architectures, original beta.9 upgrade, and final publication in Actions, then archive.
- [x] 1.5 Run each architecture smoke on its native runner and require both before image promotion and publication.
