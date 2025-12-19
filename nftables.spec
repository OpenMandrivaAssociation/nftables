%define major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d
# (tpg) optimize it a bit
%global optflags %{optflags} -Oz

Summary:	Netfilter Tables userspace utillites
Name:		nftables
Version:	1.1.1
Release:	2
License:	GPLv2
Group:		System/Kernel and hardware
URL:		https://netfilter.org/projects/nftables/
Source0:	http://ftp.netfilter.org/pub/nftables/nftables-%{version}.tar.xz
Source1:	nftables.service
Source2:	nftables.conf
BuildRequires:	make
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	docbook2x
BuildRequires:	flex
BuildRequires:	libtool
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
	--with-json

%make_build

cd py/
%py_build

%check
make check

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

%post
%systemd_post nftables.service

%preun
%systemd_preun nftables.service

%postun
%systemd_postun_with_restart nftables.service

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
