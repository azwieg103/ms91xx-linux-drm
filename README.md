# MacroSilicon MS9133 USB Display Driver for Linux

Linux DRM/KMS driver for the MacroSilicon MS9133 USB display adapter.

## Tested hardware and software

The current verified test system is:

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

The adapter successfully initialized, registered its DRM framebuffer, and started video output on this configuration. This is a hardware test result for this specific system—not a guarantee for other kernels, distributions, adapters, or desktop environments.

## What is included

The build produces two kernel modules:

- `usbdisp_drm.ko` — DRM/platform driver.
- `usbdisp_usb.ko` — USB interface and display transport driver.

The source is based on MacroSilicon's Linux driver and includes compatibility and lifecycle fixes for modern kernels.

## Build

Install the compiler, make, and matching kernel development packages:

```bash
sudo dnf install -y gcc make kernel-devel kernel-headers elfutils-libelf-devel
```

Verify that the running kernel has matching build files:

```bash
KVER="$(uname -r)"
test -e "/lib/modules/$KVER/build/Makefile" || {
    echo "Missing kernel development files for $KVER"
    exit 1
}
```

Clone and build:

```bash
git clone https://github.com/azwieg103/ms91xx-linux-drm.git
cd ms91xx-linux-drm
make clean
make -j"$(nproc)" KVER="$(uname -r)"
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

To build for a different installed kernel, set `KVER` to that kernel's exact version and ensure its matching development package is installed.

## Loading for a manual test

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

Recent work has addressed several issues encountered while bringing the driver up on the tested 6.12 kernel:

- Avoided overwriting kernel-owned device IOMMU state with a pointer to a stack-local structure. The old pointer could become invalid and crash during platform-device removal.
- Fixed fbdev initialization for kernels where `drm_fb_helper.info` is not preallocated at the time the driver's fbdev probe runs. The previous code could pass a NULL `fb_info` to `drm_fb_helper_fill_info()` and crash during USB probe.
- Added validation and synchronization around USB HAL registration and DRM pipeline operations.
- Improved USB HAL sysfs initialization error handling and cleanup.
- Added guards for sysfs callbacks and USB device driver-data access during probe and teardown.

## Known observations and limitations

During successful initialization on the tested system, the kernel emitted a warning from `__alloc_pages_noprof()` while the USB HAL attempted a high-order DMA allocation. The driver then reported:

```text
usb 2-9: buf type vmalloc
init usb_hal0 success!
```

The HAL continued initialization and video output started successfully. The allocation warning and fallback behavior remain an area for further investigation; successful display output does not establish that every DMA or memory-pressure scenario is safe.

The following have not yet been fully validated:

- Reboot-time or automatic module loading.
- Repeated USB unplug/replug and disconnect recovery.
- Suspend/resume.
- Long-duration operation and memory-pressure behavior.
- Multiple MS9133 adapters.
- Other distributions, kernel versions, USB display chipsets, and desktop environments.

Treat this as experimental kernel software until those cases have been tested.

## DKMS

The repository includes DKMS-related files. Review `dkms.conf`, `dkms-install.sh`, and `dkms-remove.sh` before using them. DKMS installation changes system module directories and may attempt to load or unload modules; those workflows have not been validated as part of the current hardware test.

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

## License and provenance

See [LICENSE](LICENSE) for the license terms included with the source. Retain applicable copyright and license notices when modifying or redistributing the driver.
