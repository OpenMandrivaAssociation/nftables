%define major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
# (tpg) optimize it a bit
%global optflags %{optflags} -Oz

Summary:	Netfilter Tables userspace utillites
Name:		nftables
Version:	1.1.6
Release:	2
License:	GPLv2
Group:		System/Kernel and hardware
URL:		https://netfilter.org/projects/nftables/
Source0:	http://ftp.netfilter.org/pub/nftables/nftables-%{version}.tar.xz
Source1:	nftables.service
Source2:	nftables.conf
BuildRequires:	autoconf
BuildRequires:	slibtool
BuildRequires:	make
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	docbook2x
BuildRequires:	flex
BuildRequires:	python%{pyver}dist(pip)
BuildRequires:	python%{pyver}dist(setuptools)
BuildRequires:	pkgconfig(gmp)
BuildRequires:	a2x
BuildRequires:	pkgconfig(xtables)
BuildRequires:	pkgconfig(readline)
BuildRequires:	pkgconfig(libedit)
BuildRequires:	pkgconfig(libmnl)
BuildRequires:	pkgconfig(libnftnl)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(jansson)
BuildRequires:	systemd-rpm-macros
Provides:	/usr/sbin/nft
%systemd_requires

%description
Netfilter Tables userspace utilities.

#------------------------------------------------

%package -n %{libname}
Summary:	Netfilter Tables userspace utillites
Group:		System/Libraries

%description -n %{libname}
Netfilter Tables userspace utilities.

#------------------------------------------------

%package -n %{develname}
Summary:	Development package for %{name}
Group:		Development/C++
Requires:	%{libname} = %{EVRD}
Provides:	%{name}-devel = %{EVRD}

%description -n %{develname}
Header files for development with %{name}.

#------------------------------------------------
%package -n python-%{name}
Summary:	Python bindings for %{name}
Group:		Development/Python
Requires:	%{name} >= %{EVRD}

%description -n python-%{name}
Python files for development with %{name}.

%prep
%autosetup -p1

%build
%configure \
	--with-xtables \
	--with-json \
	--with-stable-release=1

# config.status leaves VERSION empty, so nftversion.h starts with a bare comma.
python - << 'PY'
ver = "%{version}".split(".")
lines = [
    "static char nftversion[] = {",
    "\t" + ",".join(ver) + ",",
    "\t1",
    "};",
    "static char nftbuildstamp[] = {",
]
for shift in range(56, -1, -8):
    lines.append(f"\t((uint64_t)MAKE_STAMP >> {shift}) & 0xff,")
lines.append("};")
open("nftversion.h", "w").write("\n".join(lines) + "\n")
PY

%make_build

cd py/
%py_build

%check
# tests/build reclones the tree with git and runs distcheck. The release
# tarball has no repository, so that test cannot pass here.
# tests/shell needs a network namespace through unshare, which the builder
# refuses. The remaining tests skip themselves when not root.
make check TESTS="tests/json_echo/run-test.py tests/monitor/run-tests.sh tests/py/nft-test.py"

%install
export SETUPTOOLS_USE_DISTUTILS=stdlib
%make_install

find %{buildroot} -name '*.la' -delete
chmod 644 %{buildroot}%{_mandir}/man8/nft*

mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE1} %{buildroot}%{_unitdir}/

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/
chmod 600 %{buildroot}%{_sysconfdir}/sysconfig/nftables.conf

mkdir -m 700 -p %{buildroot}%{_sysconfdir}/nftables
mv %{buildroot}%{_datadir}/nftables/*.nft %{buildroot}%{_sysconfdir}/nftables/

find %{buildroot}%{_sysconfdir} \
    \( -type d -exec chmod 0700 {} \; \) , \
    \( -type f -exec chmod 0600 {} \; \)

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nftables.preset << EOF
enable nftables.service
EOF

cd py/
%py_install

%files
%config(noreplace) %{_sysconfdir}/nftables/
%config(noreplace) %{_sysconfdir}/sysconfig/nftables.conf
%dir %{_datadir}/%{name}
%{_presetdir}/86-nftables.preset
%{_unitdir}/nftables.service
%{_bindir}/nft
%doc %{_mandir}/man8/*nft*
%doc %{_mandir}/man3/*nft*
%doc %{_mandir}/man5/*nft*

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n python-%{name}
%{python_sitelib}/%{name}*

%files -n %{develname}
%doc COPYING
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_datadir}/doc/%{name}/examples/*
