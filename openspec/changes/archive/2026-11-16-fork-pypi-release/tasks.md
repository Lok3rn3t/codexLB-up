## 1. Package identity

- [x] 1.1 Set the fork distribution name and update its frozen lockfile.
- [x] 1.2 Support project-specific package names in version updates and guards,
      including historical revisions with the upstream name.
- [x] 1.3 Update publisher identity and generated installation commands.

## 2. Verification

- [x] 2.1 Cover renamed distributions and historical metadata in release tests.
- [x] 2.2 Remove locale assumptions from the two failing UI assertions and rerun.
- [x] 2.3 Build and inspect wheel and sdist, then smoke-test the installed wheel.
- [x] 2.4 Validate the OpenSpec change and archive verified artifacts.
