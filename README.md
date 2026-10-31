# MacroSilicon MS9133 USB Display Driver for Linux

This repository contains a Linux **USB display driver** for the **MacroSilicon MS9133** USB display controller.

| Item | Details |
|---|---|
| Device / chip | MacroSilicon MS9133 |
| USB vendor:product ID | `345f:9133` |
| USB device description | Commonly reported as `MS USB Video` |
| Linux kernel modules | `usbdisp_drm` and `usbdisp_usb` |
| Display subsystem | Linux DRM/KMS |
| Tested operating system | **AlmaLinux 10.2 only** |

> **Compatibility notice:** This driver has only been tested on AlmaLinux 10.2. Other distributions, AlmaLinux releases, kernel versions, desktop environments, and USB display devices have not been verified. A successful build does not establish that the driver is safe or functional on other systems.

## Overview

The driver connects a compatible MacroSilicon USB display controller to the Linux Direct Rendering Manager (DRM/KMS) subsystem so that a connected USB display can be exposed to the desktop as an additional display.

This is a **USB display adapter driver**. It is not a driver for a conventional PCIe graphics card or an integrated GPU.

The source tree builds two kernel modules:

- `usbdisp_drm.ko` — DRM/platform portion of the driver.
- `usbdisp_usb.ko` — USB interface portion of the driver.

The source is based on MacroSilicon's Linux driver source and includes changes for building against the tested AlmaLinux 10.2 kernel.

## Hardware identification

Connect the adapter and inspect USB devices:

```bash
lsusb -d 345f:9133
```

The device may appear with a description similar to:

```text
ID 345f:9133 MS USB Video
```

Confirm the USB ID before assuming that a device is supported. Other products may use different MacroSilicon chips or USB IDs; they are not covered by the MS9133 test result.

## Build environment

The tested environment is:

- AlmaLinux 10.2
- Kernel: `6.12.0-211.69.1.el10_2.x86_64`
- x86_64

The build requires a compiler, make, and the kernel development files matching the kernel being built for.

Install the build dependencies on AlmaLinux:

```bash
sudo dnf install -y gcc make kernel-devel kernel-headers elfutils-libelf-devel
```

For an out-of-tree module build, the matching kernel development directory must exist:

```bash
KVER="$(uname -r)"
test -e "/lib/modules/$KVER/build/Makefile" || {
    echo "Missing kernel development files for $KVER"
    exit 1
}
```

If the running kernel was recently updated, reboot into that kernel or install the matching `kernel-devel` package before building.

## Build

Clone the repository and build against the running kernel:

```bash
git clone https://github.com/azwieg103/ms91xx-linux-drm.git
cd ms91xx-linux-drm

make
```

To select a specific installed kernel version:

```bash
make KVER="6.12.0-211.69.1.el10_2.x86_64"
```

The build should produce:

```text
drm/usbdisp_drm.ko
drm/usbdisp_usb.ko
```

Check the resulting modules:

```bash
file drm/usbdisp_drm.ko drm/usbdisp_usb.ko
modinfo drm/usbdisp_drm.ko
modinfo drm/usbdisp_usb.ko
```

To remove generated build files:

```bash
make clean
```

## DKMS packaging

The repository includes `dkms.conf`, `dkms-install.sh`, and `dkms-remove.sh` for DKMS packaging.

**Do not run the DKMS installation or removal scripts without first reviewing them for your system.** They modify files under `/usr/src` and `/lib/modules`, update the initramfs, and may attempt to unload or load kernel modules. In particular, the install script includes a live module-reload attempt. Module loading and unloading have not been established as safe on all systems.

The presence of DKMS packaging does not mean that installation or automatic loading has been validated on distributions other than the tested AlmaLinux 10.2 environment.

## Installation and runtime caution

Building the modules is separate from loading them into the running kernel. A successful compilation only verifies that the source compiled against the selected kernel headers; it does not verify USB enumeration, display output, disconnect handling, suspend/resume, or system stability.

**Use caution before loading either module.** A kernel driver runs with kernel privileges, and a fault can hang or crash the system. Keep a way to recover the machine and save important work before performing hardware tests. Do not force-unload a module that is in use.

No general installation or runtime procedure is claimed to be safe for all systems at this time. Runtime behavior must be validated on the specific hardware and kernel before relying on this driver.

## Troubleshooting build problems

### Kernel build directory is missing

Check that the development package matches the running kernel:

```bash
uname -r
rpm -q "kernel-devel-$(uname -r)"
ls -ld "/lib/modules/$(uname -r)/build"
```

### Module version information

Inspect a built module with:

```bash
modinfo drm/usbdisp_drm.ko
modinfo drm/usbdisp_usb.ko
```

The module's `vermagic` should match the target kernel. If it does not, rebuild using the matching kernel development files and `KVER`.

## Project status

This is an experimental, hardware-specific Linux kernel driver project. The current documented test baseline is **AlmaLinux 10.2 with the kernel listed above**. Testing on other systems is not implied.

Issues and contributions are welcome, but please include the exact adapter USB ID, distribution release, kernel version, build output, and relevant kernel log messages when reporting a problem.

## License and provenance

See [LICENSE](LICENSE) for the license terms included with the source. The driver is derived from MacroSilicon's published Linux source; retain the applicable copyright and license notices when modifying or redistributing it.
