# MacroSilicon MS9133 USB Display Driver for Linux

Linux DRM/KMS driver for the MacroSilicon MS9133 USB display adapter.

**Current release:** 3.1.9  
**Supported packaging target:** Enterprise Linux 10 family (AlmaLinux 10, Rocky Linux 10, Oracle Linux 10, and CentOS Stream 10)  
**Package type:** kernel-independent DKMS RPM

- [GitHub releases and RPM downloads](https://github.com/azwieg103/ms91xx-linux-drm/releases)
- [Build and test workflow](https://github.com/azwieg103/ms91xx-linux-drm/actions/workflows/build-el10-rpm.yml)

## Tested hardware and software

The current verified hardware test system is:

| Item | Tested configuration |
|---|---|
| Host | HP MP9 G4 Retail System |
| Distribution | AlmaLinux 10.2 |
| Kernel | `6.12.0-211.69.1.el10_2.x86_64` |
| Architecture | x86_64 |
| USB adapter | MacroSilicon MS9133 |
| USB ID | `345f:9133` (`MS USB Video`) |
| Desktop | KDE Plasma on Wayland |
| Verified display mode | 1920x1080 at 60 Hz |

The adapter successfully initialized, registered its DRM framebuffer, and started video output on this configuration. This is a hardware test result for this specific system—not a guarantee for other kernels, adapters, or desktop environments.

## What is included

The driver builds two kernel modules:

- `usbdisp_drm.ko` — DRM/platform driver.
- `usbdisp_usb.ko` — USB interface and display transport driver.

The source includes compatibility and lifecycle fixes for modern kernels. The DKMS package installs the source and builds modules against each installed kernel's matching development files.

## Latest changes in 3.1.9

- Corrected the embedded module version metadata so both modules report 3.1.9.
- Updated the DKMS package version to 3.1.9.
- Made the RPM build version derive from the RPM spec, with release-tag validation.
- Added CI checks that verify both modules' reported versions match the package version on every EL10 build target.
- Retained the safer RPM upgrade behavior: previous DKMS versions are not retired unless the new version builds successfully for all installed `kernel-devel` packages.

## Install the RPM on Enterprise Linux 10

The GitHub Actions pipeline builds and tests the RPM on all four supported EL10 build environments:

- AlmaLinux 10
- Rocky Linux 10
- Oracle Linux 10
- CentOS Stream 10

A tagged release is published only after all four distribution jobs pass. Download the **3.1.9** RPM from the [GitHub Releases page](https://github.com/azwieg103/ms91xx-linux-drm/releases). Do not use an older release if you specifically need the 3.1.9 fixes.

### 1. Install prerequisites

Enable EPEL and install DKMS plus the build dependencies:

```bash
sudo dnf install -y https://dl.fedoraproject.org/pub/epel/epel-release-latest-10.noarch.rpm
sudo dnf install -y dkms gcc make elfutils-libelf-devel kernel-devel
```

Ensure the development files match every kernel you intend to use. For the currently running kernel:

```bash
KVER="$(uname -r)"
test -e "/lib/modules/$KVER/build/Makefile" || {
    echo "Missing kernel-devel for $KVER"
    exit 1
}
```

### 2. Install the release RPM

Download the 3.1.9 binary RPM from the release assets at:

https://github.com/azwieg103/ms91xx-linux-drm/releases

Then install the downloaded file (replace the filename below with the exact asset filename shown on the release page):

```bash
sudo dnf install ./ms91xx-linux-drm-dkms-3.1.9-1.el10.noarch.rpm
```

The RPM installs the driver source under `/usr/src/msdisp-3.1.9`, registers it with DKMS, builds the modules for installed kernels with matching `kernel-devel` packages, and installs:

```text
/usr/lib/modules-load.d/msdisp.conf
```

That modules-load configuration loads `usbdisp_drm` before `usbdisp_usb` at boot.

### 3. Verify installation

```bash
rpm -q ms91xx-linux-drm-dkms
dkms status -m msdisp
modinfo -F version usbdisp_drm
modinfo -F version usbdisp_usb
modinfo -n usbdisp_drm
modinfo -n usbdisp_usb
cat /usr/lib/modules-load.d/msdisp.conf
```

For version 3.1.9, both `modinfo -F version` commands should report `3.1.9`. The module paths should resolve to the DKMS-installed modules for the selected kernel.

Reboot after installation so the newly installed modules are loaded cleanly. Do not force-unload the display modules while the graphical session is using them.

### Secure Boot

If Secure Boot is enabled, configure and enroll a DKMS signing key before loading the modules. A successful DKMS build does not enroll a signing key or authorize unsigned modules under Secure Boot.

## Build manually from source

These instructions are for developers or distributions without a published package. The RPM is the recommended installation method on EL10.

### Build dependencies

Install a compiler, make, and development files for the exact target kernel. On Enterprise Linux:

```bash
sudo dnf install -y gcc make elfutils-libelf-devel kernel-devel
```

### Clone and compile

```bash
git clone https://github.com/azwieg103/ms91xx-linux-drm.git
cd ms91xx-linux-drm
KVER="$(uname -r)"
test -e "/lib/modules/$KVER/build/Makefile" || {
    echo "Missing kernel-devel for $KVER"
    exit 1
}
make clean
make -j"$(nproc)" KVER="$KVER"
```

The resulting modules should be:

```text
drm/usbdisp_drm.ko
drm/usbdisp_usb.ko
```

Inspect them with:

```bash
modinfo drm/usbdisp_drm.ko
modinfo drm/usbdisp_usb.ko
```

To compile for another installed kernel, set `KVER` to that kernel's exact version and ensure its matching development package is installed.

### Manual load test

Loading an out-of-tree kernel driver can crash or hang a system. Save work first and ensure you have a recovery path. Do not force-unload modules that are in use.

With the adapter connected, load the DRM module first, then the USB module:

```bash
sudo insmod ./drm/usbdisp_drm.ko
sleep 2
ls -l /sys/class/drm/
sudo insmod ./drm/usbdisp_usb.ko
```

Check module and display initialization:

```bash
lsmod | grep usbdisp
ls -l /sys/class/drm/
journalctl -k -b | grep -E 'msdisp|usbdisp|start video|pipe enable'
```

The DRM device may appear as a separate `cardN` under `/sys/class/drm/`. The exact card and connector numbers depend on the other graphics devices in the system.

## Important implementation fixes

Recent work has addressed issues encountered while bringing the driver up on modern kernels:

- Avoided overwriting kernel-owned device IOMMU state with a pointer to a stack-local structure. The old pointer could become invalid and crash during platform-device removal.
- Fixed fbdev initialization for kernels where `drm_fb_helper.info` is not preallocated when the driver's fbdev probe runs. The previous code could pass a NULL `fb_info` to `drm_fb_helper_fill_info()` and crash during USB probe.
- Added validation and synchronization around USB HAL registration and DRM pipeline operations.
- Improved USB HAL sysfs initialization error handling and cleanup.
- Added guards for sysfs callbacks and USB device driver-data access during probe and teardown.
- Corrected the module version metadata and DKMS version tracking in 3.1.9.

## Contributing

Community contributions should be submitted as pull requests against the **`dev`** branch. Do not target `main` for feature or bug-fix contributions. See [CONTRIBUTING.md](CONTRIBUTING.md) for the fork, testing, and pull-request process. Security issues should be reported privately as described in [SECURITY.md](SECURITY.md).

Changes are tested on AlmaLinux 10, Rocky Linux 10, Oracle Linux 10, and CentOS Stream 10. A passing CI build is required but does not replace maintainer review or hardware validation. The maintainer promotes tested changes from `dev` to `main` and controls version tags and official releases.

## CI and release process

The workflow at `.github/workflows/build-el10-rpm.yml` runs on pushes to `main` and `dev`, version tags, pull requests targeting `main` or `dev`, and manual dispatch. Pull requests targeting `main` are restricted by CI to promotion from this repository's `dev` branch.

For each EL10 distribution, CI:

1. Installs build dependencies and kernel development files.
2. Builds the binary DKMS RPM and source RPM.
3. Installs the binary RPM in the distribution container.
4. Runs DKMS and verifies both modules build.
5. Checks that both modules report the same version as the RPM.
6. Uploads the RPM build artifacts.

When a version tag such as `v3.1.9` is pushed, the workflow first runs all four distribution builds. If all pass, the release job publishes a GitHub release and attaches the tested RPM assets. A successful push-to-main build alone does not publish a release.

## Known observations and limitations

During successful initialization on the tested system, the kernel emitted a warning from `__alloc_pages_noprof()` while the USB HAL attempted a high-order DMA allocation. The driver then reported:

```text
usb 2-9: buf type vmalloc
init usb_hal0 success!
```

The HAL continued initialization and video output started successfully. The allocation warning and fallback behavior remain an area for further investigation; successful display output does not establish that every DMA or memory-pressure scenario is safe.

The following have not yet been fully validated across the supported distribution matrix:

- Repeated USB unplug/replug and disconnect recovery.
- Suspend/resume.
- Long-duration operation and memory-pressure behavior.
- Multiple MS9133 adapters.
- Other USB display chipsets, kernel versions, and desktop environments.

CI confirms packaging and DKMS build behavior for its EL10 test environments. It does not replace hardware testing on every distribution or kernel combination. Treat this as experimental kernel software and keep a recovery path available.

## Troubleshooting

Check the adapter identity:

```bash
lsusb -d 345f:9133
```

Check the running kernel and matching development package:

```bash
uname -r
rpm -q "kernel-devel-$(uname -r)"
ls -ld "/lib/modules/$(uname -r)/build"
```

Review driver messages:

```bash
journalctl -k -b | grep -E -i 'msdisp|usbdisp|345f:9133|drm|dma'
```

When reporting an issue, include the adapter USB ID, distribution release, kernel version, build output, and relevant kernel log messages.

## Remove the RPM

```bash
sudo dnf remove ms91xx-linux-drm-dkms
```

Removing the RPM unregisters this driver version from DKMS. If a module is currently in use by the display session, reboot before expecting it to be fully unloaded.

## License and provenance

See [LICENSE](LICENSE) for the license terms included with the source. Retain applicable copyright and license notices when modifying or redistributing the driver.
