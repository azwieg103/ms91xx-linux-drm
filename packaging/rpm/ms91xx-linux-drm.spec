Name:           ms91xx-linux-drm-dkms
Version:        3.1.9
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
%{_usrsrc}/msdisp-%{version}
%{_prefix}/lib/modules-load.d/msdisp.conf

%post
if command -v dkms >/dev/null 2>&1; then
    dkms add -m msdisp -v %{version} >/dev/null 2>&1 || :
    build_failed=0
    if rpm -q kernel-devel >/dev/null 2>&1; then
        for kver in $(rpm -q --qf '%%{VERSION}-%%{RELEASE}.%%{ARCH} ' kernel-devel); do
            echo "Building msdisp/%{version} for kernel $kver"
            if dkms install -m msdisp -v %{version} -k "$kver" --force; then
                /sbin/depmod -a "$kver" || :
            else
                echo "WARNING: DKMS build failed for kernel $kver; preserving previous driver."
                build_failed=1
            fi
        done
        if [ "$build_failed" -eq 0 ]; then
            # Retire older DKMS versions only after the new version built for
            # every installed kernel-devel package.
            for old_version in $(dkms status -m msdisp 2>/dev/null | awk -F'[/,: ]+' '{print $2}' | sort -u); do
                if [ "$old_version" != "%{version}" ]; then
                    dkms remove -m msdisp -v "$old_version" --all >/dev/null 2>&1 || :
                    rm -rf "/usr/src/msdisp-$old_version"
                fi
            done
        else
            echo "WARNING: Previous DKMS driver versions were retained."
        fi
    else
        echo "WARNING: Install matching kernel-devel packages; previous driver versions were retained."
    fi
fi
/sbin/depmod -a >/dev/null 2>&1 || :

%preun
if [ "$1" -eq 0 ] && command -v dkms >/dev/null 2>&1; then
    dkms remove -m msdisp -v %{version} --all >/dev/null 2>&1 || :
fi

%postun
/sbin/depmod -a >/dev/null 2>&1 || :

%changelog
* Wed Nov 04 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.9-1
- Correct embedded driver and DKMS version metadata to 3.1.9.
- Validate module metadata matches the RPM version in all EL10 builds.
- Derive build and release versions from the RPM spec and tag.

* Wed Nov 04 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.8-1
- Preserve the previous driver unless the new DKMS build succeeds for all installed kernels.
- Retire older DKMS versions only after successful replacement builds.
- Improve safe upgrade behavior for existing installations.

* Wed Nov 04 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.7-1
- Add feature detection for DRM API backports in Enterprise Linux kernels.
- Build and validate the kernel-independent DKMS RPM across EL10 distributions.

* Wed Nov 04 2026 Andrew Zwieg <andrew@zwiegnet.com> - 3.1.6-1
- Initial kernel-independent DKMS RPM packaging.
