Name: lmslogger
Version: 0.1.5
Release: 1%{?dist}
Summary: Lyrion Media System logging daemon

License: MIT
URL: https://github.com/tpbrisco/lmslogger
Source0: %{name}-%{version}.tar.gz
Source1: lmslogger.service
Source2: lmslogger.env

BuildArch: noarch

BuildRequires: python3-devel
BuildRequires: python3-setuptools
BuildRequires: python3-wheel
BuildRequires: python3-build
BuildRequires: python3-pydantic
BuildRequires: systemd-rpm-macros


Requires: python3-pydantic
Requires: python3-pydantic-settings
Requires: python3-dotenv

%description
A specialized Python logging daemon designed to integration with Lyrion Music Server

%prep
%autosetup

%build
python3 -m build --wheel --no-isolation

%install
python3 -m pip install --root %{buildroot} --no-deps dist/*.whl

# install the systemd service file
%{__install} -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/lmslogger.service

# install environment configuration file into /etc/lmslogger
%{__install} -D -m 0600 %{SOURCE2} %{buildroot}%{_sysconfdir}/lmslogger/lmslogger.env

%files
%{python3_sitelib}/lmslogger/
%{python3_sitelib}/lmslogger-%{version}.dist-info/
%{_bindir}/lmslogger
%{_unitdir}/lmslogger.service

%dir %{_sysconfdir}/lmslogger
%config(noreplace) %{_sysconfdir}/lmslogger/lmslogger.env

%check
true

%post
%systemd_post lmslogger.service

%preun
%systemd_preun lmslogger.service

%postun
%systemd_postun_with_restart lmslogger.service

%changelog
* Mon Jul 24 2026 Your Name <you@example.com> - 0.1.5-1
- Initial RPM packaging and spec cleanup

