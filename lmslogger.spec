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
BuildRequires: python3-pydantic
BuildRequires: systemd-rpm-macros


Requires: python3-pydantic
Requires: python3-pydantic-settings
Requires: python3-dotenv

%description
A specialized Python logging daemon designed to integration with Lyrion Music Server

%prep
%autosetup

%install
%py3_install

# install the systemd service file
%{__install} -D -m 0644 %{SOURCE1} %{buildroot}%{_unitdir}/lmslogger.service

# install environment configuration file into /etc/lmslogger
%{__install} -D -m 0600 %{SOURCE2} %{buildroot}%{_sysconfdir}/lmslogger/lmslogger.env

%files
%{python3_sitelib}/lmslogger/
%{python3_sitelib}/lmslogger-%{version}.dist-info/
%{_bindir}/lmslogger
%{_unitdir}/lmslogger.service

# %config(noreplace) ensures package updates wont overwrite custom admin edits
%dir %{_sysconfdir}/lmslogger
%config(noreplace) %{_sysconfdir}/lmslogger/lmslogger.env

%post
%systemd_post lmslogger.service

%preun
%systemd_preun lmslogger.service

%postun
%systemd_postun_with_restart lmslogger.service

%changelog
* Tue Jul 24 2026 Your Name <you@example.com> - 0.1.0-1
- Initial RPM packaging and spec cleanup

