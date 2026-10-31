Name:           ms91xx-linux-drm
Version:        3.1.6
Release:        1%{?dist}
Summary:        MacroSilicon MS9133 USB display DRM driver
License:        GPL-2.0-only
URL:            https://github.com/azwieg103/ms91xx-linux-drm
Source0:        %{name}-%{version}.tar.gz

# Build only for an explicitly selected kernel release.
%{!?kver:%{error:Pass --define 'kver <kernel-release>' to rpmbuild}}
BuildRequires:  gcc
BuildRequires:  make
BuildRequires:  kernel-devel = %{kver}
BuildRequires:  elfutils-libelf-devel
Requires:       kernel-uname-r = %{kver}
Requires:       kmod

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Out-of-tree DRM/KMS and USB interface kernel modules for the MacroSilicon
MS9133 USB display adapter. This package is built for one exact kernel
release and is not a kABI-compatible, cross-kernel module package.

%prep
%autosetup -n %{name}-%{version}

%build
make clean
make -j%{?_smp_build_ncpus} KVER=%{kver} KDIR=/usr/src/kernels/%{kver}

%install
rm -rf %{buildroot}
install -D -m 0644 drm/usbdisp_drm.ko %{buildroot}/lib/modules/%{kver}/extra/ms91xx/usbdisp_drm.ko
install -D -m 0644 drm/usbdisp_usb.ko %{buildroot}/lib/modules/%{kver}/extra/ms91xx/usbdisp_usb.ko
install -D -m 0644 packaging/rpm/msdisp.modules-load %{buildroot}%{_prefix}/lib/modules-load.d/msdisp.conf
install -D -m 0644 packaging/rpm/msdisp.conf %{buildroot}%{_sysconfdir}/modprobe.d/msdisp.conf

%files
%defattr(-,root,root,-)
/lib/modules/%{kver}/extra/ms91xx/usbdisp_drm.ko
/lib/modules/%{kver}/extra/ms91xx/usbdisp_usb.ko
%{_prefix}/lib/modules-load.d/msdisp.conf
%config(noreplace) %{_sysconfdir}/modprobe.d/msdisp.conf

%post
/sbin/depmod -a %{kver} || :
/usr/bin/systemctl try-restart systemd-modules-load.service >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ]; then
    /usr/bin/rm -f %{_sysconfdir}/modprobe.d/msdisp.conf
    /usr/bin/rm -f %{_prefix}/lib/modules-load.d/msdisp.conf
fi

%postun
/sbin/depmod -a %{kver} || :

%changelog
* Sat Oct 31 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.6-1
- Initial kernel-specific RPM packaging for AlmaLinux 10.
