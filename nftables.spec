%define major 1
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Netfilter Tables userspace utillites
Name:		nftables
Version:	0.9.3
Release:	3
License:	GPLv2
Group:		System/Kernel and hardware
URL:		http://netfilter.org/projects/nftables/
Source0:	http://ftp.netfilter.org/pub/nftables/nftables-%{version}.tar.bz2
Source1:	nftables.service
Source2:	nftables.conf
BuildRequires:	bison
BuildRequires:	docbook2x
BuildRequires:	flex
BuildRequires:	gmp-devel
BuildRequires:	a2x
BuildRequires:	pkgconfig(xtables)
BuildRequires:	pkgconfig(readline)
BuildRequires:	pkgconfig(libmnl)
BuildRequires:	pkgconfig(libnftnl)
BuildRequires:	pkgconfig(python)
BuildRequires:	pkgconfig(jansson)
BuildRequires:	systemd-macros

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
Requires:	%{libname} = %{EVRD}

%description -n python-%{name}
Python files for development with %{name}.

%prep
%autosetup -p1

%build
%configure \
	--with-xtables \
	--with-json \
	--enable-python \
	--with-python-bin=%{__python3}

%make_build

%install
%make_install

find %{buildroot} -name '*.la' -delete
chmod 644 %{buildroot}%{_mandir}/man8/nft*

mkdir -p %{buildroot}%{_unitdir}
cp -a %{SOURCE1} %{buildroot}%{_unitdir}/

mkdir -p %{buildroot}%{_sysconfdir}/sysconfig
cp -a %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/

mkdir -p %{buildroot}%{_sysconfdir}/nftables

# make nftables.py use the real library file name
# to avoid nftables-devel package dependency
sofile=$(readlink %{buildroot}%{_libdir}/libnftables.so)
sed -i -e 's/\(sofile=\)".*"/\1"'$sofile'"/' %{buildroot}%{python_sitelib}/nftables/nftables.py

install -d %{buildroot}%{_presetdir}
cat > %{buildroot}%{_presetdir}/86-nftables.preset << EOF
enable nftables.service
EOF

%files
%config(noreplace) %{_sysconfdir}/nftables/
%config(noreplace) %{_sysconfdir}/sysconfig/nftables.conf
%{_presetdir}/86-nftables.preset
%{_unitdir}/nftables.service
%{_sbindir}/nft
%{_mandir}/man8/*nft*
%{_mandir}/man3/*nft*
%{_mandir}/man5/*nft*

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n python-%{name}
%{python_sitelib}/%{name}-*-py%{py_ver}.egg-info
%{python_sitelib}/%{name}

%files -n %{develname}
%doc COPYING
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc
%{_datadir}/doc/%{name}/examples/*
