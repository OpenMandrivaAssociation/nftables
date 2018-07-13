%define major 0
%define libname %mklibname %{name} %{major}
%define develname %mklibname %{name} -d

Summary:	Netfilter Tables userspace utillites
Name:		nftables
Version:	0.9.0
Release:	1
License:	GPLv2
Group:		System/Kernel and hardware
URL:		http://netfilter.org/projects/nftables/
Source0:	http://ftp.netfilter.org/pub/nftables/nftables-%{version}.tar.bz2
BuildRequires:	bison
BuildRequires:	docbook2x
BuildRequires:	flex
BuildRequires:	gmp-devel
BuildRequires:	readline-devel
BuildRequires:	pkgconfig(libmnl)
BuildRequires:	pkgconfig(libnftnl)

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

%prep
%autosetup -p1

%build
%configure
%make_build

%install
%make_install

find %{buildroot} -name '*.la' -delete
chmod 644 %{buildroot}%{_mandir}/man8/nft*

%files
%config(noreplace) %{_sysconfdir}/nftables/
%{_sbindir}/nft
%{_mandir}/man8/nft*

%files -n %{libname}
%{_libdir}/lib%{name}.so.%{major}*

%files -n %{develname}
%doc COPYING
%{_includedir}/%{name}/
%{_libdir}/lib%{name}.so
%{_libdir}/pkgconfig/lib%{name}.pc
