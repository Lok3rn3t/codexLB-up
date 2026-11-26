## 1. Establish the source

- [x] 1.1 Verify the original PyPI version and immutable Docker image, and compare migration histories.
- [x] 1.2 Reproduce the existing beta.9 upgrade path using disposable representative data.

## 2. Protect and document the upgrade

- [x] 2.1 Add a container upgrade regression check that creates data with the original image and verifies the target image.
- [x] 2.2 Run the upgrade check in CI and before release image promotion.
- [x] 2.3 Document preservation of the data mount, encryption key, configuration, existing database engine, and rollback backup.

## 3. Verify

- [x] 3.1 Pass focused validation and strict OpenSpec validation.
- [x] 3.2 Pass the actual Docker upgrade check in GitHub CI and archive the verified change.
