%if 0%{?fedora} || 0%{?rhel} == 6
%global with_devel 1
%global with_bundled 0
%global with_debug 0
%global with_check 1
%global with_unit_test 1
%else
%global with_devel 0
%global with_bundled 0
%global with_debug 0
%global with_check 0
%global with_unit_test 0
%endif

%if 0%{?with_debug}
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global provider        github
%global provider_tld    com
%global project         mesos
%global repo            mesos-go
# https://github.com/mesos/mesos-go
%global provider_prefix %{provider}.%{provider_tld}/%{project}/%{repo}
%global import_path     %{provider_prefix}
%global commit          83b52d7f648d2a2fa91330123d348d4090be2aed
%global shortcommit     %(c=%{commit}; echo ${c:0:7})

Name:           golang-%{provider}-%{project}-%{repo}
Version:        0
Release:        0.9.git%{shortcommit}%{?dist}
Summary:        Go language bindings for Apache Mesos
License:        ASL 2.0
URL:            https://%{provider_prefix}
Source0:        https://%{provider_prefix}/archive/%{commit}/%{repo}-%{shortcommit}.tar.gz

# e.g. el6 has ppc64 arch without gcc-go, so EA tag is required
ExclusiveArch:  %{?go_arches:%{go_arches}}%{!?go_arches:%{ix86} x86_64 %{arm}}
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%description
%{summary}

%if 0%{?with_devel}
%package devel
Summary:       %{summary}
BuildArch:     noarch

%if 0%{?with_check}
BuildRequires: golang(code.google.com/p/go-uuid/uuid)
BuildRequires: golang(github.com/gogo/protobuf/proto)
BuildRequires: golang(github.com/golang/glog)
BuildRequires: golang(github.com/samuel/go-zookeeper/zk)
BuildRequires: golang(github.com/stretchr/testify/assert)
BuildRequires: golang(github.com/stretchr/testify/mock)
BuildRequires: golang(github.com/stretchr/testify/suite)
BuildRequires: golang(golang.org/x/net/context)
%endif

Requires:      golang(code.google.com/p/go-uuid/uuid)
Requires:      golang(github.com/gogo/protobuf/proto)
Requires:      golang(github.com/golang/glog)
Requires:      golang(github.com/samuel/go-zookeeper/zk)
Requires:      golang(github.com/stretchr/testify/assert)
Requires:      golang(github.com/stretchr/testify/mock)
Requires:      golang(github.com/stretchr/testify/suite)
Requires:      golang(golang.org/x/net/context)

Provides:      golang(%{import_path}/auth) = %{version}-%{release}
Provides:      golang(%{import_path}/auth/callback) = %{version}-%{release}
Provides:      golang(%{import_path}/auth/sasl) = %{version}-%{release}
Provides:      golang(%{import_path}/auth/sasl/mech) = %{version}-%{release}
Provides:      golang(%{import_path}/auth/sasl/mech/crammd5) = %{version}-%{release}
Provides:      golang(%{import_path}/detector) = %{version}-%{release}
Provides:      golang(%{import_path}/detector/zoo) = %{version}-%{release}
Provides:      golang(%{import_path}/executor) = %{version}-%{release}
Provides:      golang(%{import_path}/healthchecker) = %{version}-%{release}
Provides:      golang(%{import_path}/mesos) = %{version}-%{release}
Provides:      golang(%{import_path}/mesosproto) = %{version}-%{release}
Provides:      golang(%{import_path}/mesosutil) = %{version}-%{release}
Provides:      golang(%{import_path}/mesosutil/process) = %{version}-%{release}
Provides:      golang(%{import_path}/messenger) = %{version}-%{release}
Provides:      golang(%{import_path}/messenger/testmessage) = %{version}-%{release}
Provides:      golang(%{import_path}/scheduler) = %{version}-%{release}
Provides:      golang(%{import_path}/testutil) = %{version}-%{release}
Provides:      golang(%{import_path}/upid) = %{version}-%{release}

%description devel
%{summary}

This package contains library source intended for
building other packages which use import path with
%{import_path} prefix.
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%package unit-test
Summary:         Unit tests for %{name} package
# If go_compiler is not set to 1, there is no virtual provide. Use golang instead.
BuildRequires:  %{?go_compiler:compiler(go-compiler)}%{!?go_compiler:golang}

%if 0%{?with_check}
#Here comes all BuildRequires: PACKAGE the unit tests
#in %%check section need for running
%endif

# test subpackage tests code from devel subpackage
Requires:        %{name}-devel = %{version}-%{release}

%description unit-test
%{summary}

This package contains unit tests for project
providing packages with %{import_path} prefix.
%endif

%prep
%setup -q -n %{repo}-%{commit}

%build

%install
# source codes for building projects
%if 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
echo "%%dir %%{gopath}/src/%%{import_path}/." >> devel.file-list
# *.proto files defines a golang package as well
for file in $(find . -iname "*.proto") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
# find all *.go but no *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*.go" \! -iname "*_test.go") ; do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> devel.file-list
done
%endif

# testing files for this project
%if 0%{?with_unit_test} && 0%{?with_devel}
install -d -p %{buildroot}/%{gopath}/src/%{import_path}/
# find all *_test.go files and generate unit-test.file-list
for file in $(find . -iname "*_test.go"); do
    echo "%%dir %%{gopath}/src/%%{import_path}/$(dirname $file)" >> devel.file-list
    install -d -p %{buildroot}/%{gopath}/src/%{import_path}/$(dirname $file)
    cp $file %{buildroot}/%{gopath}/src/%{import_path}/$file
    echo "%%{gopath}/src/%%{import_path}/$file" >> unit-test.file-list
done
%endif

%if 0%{?with_devel}
sort -u -o devel.file-list devel.file-list
%endif

%check
%if 0%{?with_check} && 0%{?with_unit_test} && 0%{?with_devel}
%if ! 0%{?with_bundled}
export GOPATH=%{buildroot}/%{gopath}:%{gopath}
%else
export GOPATH=%{buildroot}/%{gopath}:$(pwd)/Godeps/_workspace:%{gopath}
%endif

%if ! 0%{?gotest:1}
%global gotest go test
%endif

%gotest %{import_path}/auth/sasl
%gotest %{import_path}/detector
#%%gotest %%{import_path}/detector/zoo
#%%gotest %%{import_path}/executor
%gotest %{import_path}/healthchecker
%gotest %{import_path}/mesosproto
%gotest %{import_path}/mesosutil
%gotest %{import_path}/messenger
#%%gotest %%{import_path}/scheduler
%gotest %{import_path}/upid
%endif

#define license tag if not already defined
%{!?_licensedir:%global license %doc}

%if 0%{?with_devel}
%files devel -f devel.file-list
%license LICENSE
%doc README.md Godeps/Godeps.json
%dir %{gopath}/src/%{provider}.%{provider_tld}/%{project}
%endif

%if 0%{?with_unit_test} && 0%{?with_devel}
%files unit-test -f unit-test.file-list
%license LICENSE
%doc README.md messenger/README.md
%endif

%changelog
* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.9.git83b52d7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.8.git83b52d7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.7.git83b52d7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Thu Jul 21 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.6.git83b52d7
- https://fedoraproject.org/wiki/Changes/golang1.7

* Mon Feb 22 2016 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 0-0.5.git83b52d7
- https://fedoraproject.org/wiki/Changes/golang1.6

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 0-0.4.git83b52d7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Sat Sep 12 2015 jchaloup <jchaloup@redhat.com> - 0-0.3.git83b52d7
- Update to spec-2.1
  related: #1250493

* Mon Aug 24 2015 jchaloup <jchaloup@redhat.com> - 0-0.2.git83b52d7
- Update ifarch for secondary architectures
  resolves: #1250493

* Tue Jul 28 2015 jchaloup <jchaloup@redhat.com> - 0-0.1.git83b52d7
- First package for Fedora
  resolves: #1246740

