Name:           ms91xx-linux-drm-dkms
Version:        3.1.6
Release:        1%{?dist}
Summary:        MacroSilicon MS9133 USB display driver (DKMS source)
License:        GPL-2.0-only
URL:            https://github.com/azwieg103/ms91xx-linux-drm
Source0:        ms91xx-linux-drm-%{version}.tar.gz
BuildArch:      noarch
Requires:       dkms

%description
DKMS source package for the MacroSilicon MS9133 USB display adapter.
The package installs the driver source and registers it with DKMS so that
modules are built for installed and future kernels using their matching
kernel-devel packages. It is not tied to one specific kernel release.

%prep
%autosetup -n ms91xx-linux-drm-%{version}

%build
# Kernel modules are compiled by DKMS against each target kernel.

%install
rm -rf %{buildroot}
install -d -m 0755 %{buildroot}%{_usrsrc}/msdisp-%{version}
cp -a . %{buildroot}%{_usrsrc}/msdisp-%{version}/
rm -rf %{buildroot}%{_usrsrc}/msdisp-%{version}/.git
find %{buildroot}%{_usrsrc}/msdisp-%{version} -type f \
  \( -name '*.o' -o -name '*.ko' -o -name '*.mod' -o -name '*.mod.c' \
     -o -name '*.cmd' -o -name '.*.cmd' -o -name 'Module.symvers' \
     -o -name 'modules.order' \) -delete
install -D -m 0644 packaging/rpm/msdisp.modules-load \
  %{buildroot}%{_prefix}/lib/modules-load.d/msdisp.conf

%files
%defattr(-,root,root,-)
%dir %{_usrsrc}/msdisp-%{version}
%{_usrsrc}/msdisp-%{version}
%{_prefix}/lib/modules-load.d/msdisp.conf

%post
if command -v dkms >/dev/null 2>&1; then
    dkms add -m msdisp -v %{version} >/dev/null 2>&1 || :
    dkms autoinstall -m msdisp -v %{version} >/dev/null 2>&1 || :
fi
/sbin/depmod -a >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ] && command -v dkms >/dev/null 2>&1; then
    dkms remove -m msdisp -v %{version} --all >/dev/null 2>&1 || :
fi

%postun
/sbin/depmod -a >/dev/null 2>&1 || :

%changelog
* Wed Nov 04 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.6-1
- Package driver source as a kernel-independent DKMS RPM.
- Register and build modules through DKMS on installation.
- Rebuild for installed and future kernels with matching kernel-devel packages.
