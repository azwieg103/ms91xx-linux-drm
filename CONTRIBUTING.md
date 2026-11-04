# Contributing

Thank you for helping improve the MS91xx Linux DRM driver.

## Contribution flow

All community changes must be proposed against the `dev` branch. The `main` branch is reserved for stable, maintainer-approved code and releases.

1. Fork this repository.
2. Create a focused feature or fix branch in your fork (for example, `fix-kernel-6.12`).
3. Make your changes and include tests or reproducible validation where practical.
4. Open a pull request against **`azwieg103/ms91xx-linux-drm:dev`**, not `main`.
5. Describe the problem, the change, affected distributions and kernel versions, and the tests you ran.
6. Respond to review feedback. A maintainer will decide whether and when the change is merged.

Do not submit pull requests that change the release version, create release tags, publish packages, or alter repository security settings unless a maintainer has explicitly requested it.

## Development and testing

- Keep changes narrowly scoped and explain the reason for each non-obvious change.
- Preserve compatibility across the supported Enterprise Linux 10 distributions.
- Test against the relevant kernel headers and DKMS build process when possible.
- Do not include compiled kernel modules, object files, build directories, private keys, credentials, personal data, or proprietary vendor material that you are not authorized to redistribute.
- Never include real signing keys or certificates. Use test-only material for local testing.
- Do not claim hardware validation unless you actually tested the hardware; include the adapter, distribution, kernel, desktop session, and result.
- For driver or packaging changes, include build output or a concise reproduction of the validation performed.

## Pull request checks

Pull requests are expected to pass the repository's automated EL10 build and DKMS checks. A passing CI run is necessary but does not replace maintainer review or hardware testing.

## Code of conduct

Be respectful and constructive. Report bugs with enough detail to reproduce them, but do not post sensitive security details publicly; follow [SECURITY.md](SECURITY.md) instead.

By submitting a contribution, you agree that it may be distributed under the repository's existing license. Please ensure you have the right to submit the code.
