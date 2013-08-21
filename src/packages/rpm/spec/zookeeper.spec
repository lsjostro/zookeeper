#   Licensed to the Apache Software Foundation (ASF) under one or more
#   contributor license agreements.  See the NOTICE file distributed with
#   this work for additional information regarding copyright ownership.
#   The ASF licenses this file to You under the Apache License, Version 2.0
#   (the "License"); you may not use this file except in compliance with
#   the License.  You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

#
# RPM Spec file for ZooKeeper version @version@
#

%define name         zookeeper
%define version      @version@
%define release      @package.release@

# Installation Locations
%define _prefix      @package.prefix@
%define _bin_dir     %{_prefix}/bin
%define _conf_dir    @package.conf.dir@
%define _include_dir %{_prefix}/include
%define _lib_dir     %{_prefix}/lib
%define _lib64_dir   %{_prefix}/lib64
%define _libexec_dir %{_prefix}/libexec
%define _log_dir     @package.log.dir@
%define _man_dir     %{_prefix}/man
%define _pid_dir     @package.pid.dir@
%define _sbin_dir    %{_prefix}/sbin
%define _share_dir   %{_prefix}/share/zookeeper
%define _src_dir     %{_prefix}/src
%define _var_dir     @package.var.dir@

# Build time settings
%define _build_dir    @package.build.dir@
%define _final_name   @final.name@
%define _c_lib        @c.lib@
%define debug_package %{nil}

# Disable brp-java-repack-jars for aspect J
%define __os_install_post    \
    /usr/lib/rpm/redhat/brp-compress \
    %{!?__debug_package:/usr/lib/rpm/redhat/brp-strip %{__strip}} \
    /usr/lib/rpm/redhat/brp-strip-static-archive %{__strip} \
    /usr/lib/rpm/redhat/brp-strip-comment-note %{__strip} %{__objdump} \
    /usr/lib/rpm/brp-python-bytecompile %{nil}

# RPM searches perl files for dependancies and this breaks for non packaged perl lib
# like thrift so disable this
%define _use_internal_dependency_generator 0

Summary: ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services.
License: Apache License, Version 2.0
URL: http://zookeeper.apache.org/
Vendor: Apache Software Foundation
Group: Development/Libraries
Name: %{name}
Version: %{version}
Release: %{release} 
Source0: %{_final_name}.tar.gz
Source1: %{_final_name}-lib.tar.gz
Prefix: %{_prefix}
Prefix: %{_conf_dir}
Prefix: %{_log_dir}
Prefix: %{_pid_dir}
Prefix: %{_var_dir}
Requires: sh-utils, textutils, /usr/sbin/useradd, /usr/sbin/usermod, /sbin/chkconfig, /sbin/service, java >= 1:1.6.0
AutoReqProv: no
Provides: zookeeper, libzookeeper_mt.so.2()(64bit)
Obsoletes: zookeeper-lib

%description
ZooKeeper is a centralized service for maintaining configuration information, naming, providing distributed synchronization, and providing group services. All of these kinds of services are used in some form or another by distributed applications. Each time they are implemented there is a lot of work that goes into fixing the bugs and race conditions that are inevitable. Because of the difficulty of implementing these kinds of services, applications initially usually skimp on them ,which make them brittle in the presence of change and difficult to manage. Even when done correctly, different implementations of these services lead to management complexity when the applications are deployed.

%package lib
Summary: ZooKeeper C binding library
Group: Development/Libraries
#Requires: %{name} == %{version}
Provides: zookeeper-lib

%description lib
ZooKeeper C client library for communicating with ZooKeeper Server.

%prep
%setup -q -T -b 0 -n %{_final_name}
%setup -q -T -D -a 1 -n %{_final_name}

%build
#########################
#### INSTALL SECTION ####
#########################

%install
mkdir -p ${RPM_BUILD_ROOT}%{_prefix}
mkdir -p ${RPM_BUILD_ROOT}%{_bin_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_include_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_lib_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_libexec_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_log_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_conf_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_man_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_pid_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_sbin_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_share_dir}
mkdir -p ${RPM_BUILD_ROOT}%{_var_dir}
mkdir -p ${RPM_BUILD_ROOT}/etc/init.d

cp -p src/packages/rpm/init.d/zookeeper ${RPM_BUILD_ROOT}/etc/init.d/zookeeper
cp -p src/packages/update-zookeeper-env.sh ${RPM_BUILD_ROOT}%{_sbin_dir}/update-zookeeper-env.sh
chmod 0755 ${RPM_BUILD_ROOT}/etc/init.d/zookeeper

cp -p bin/* ${RPM_BUILD_ROOT}%{_bin_dir}
cp -p libexec/* ${RPM_BUILD_ROOT}%{_libexec_dir}
cp -pr share/zookeeper/* ${RPM_BUILD_ROOT}%{_share_dir}
cp -p conf/* ${RPM_BUILD_ROOT}%{_conf_dir}
cp -p sbin/* ${RPM_BUILD_ROOT}%{_sbin_dir}
chmod 0755 ${RPM_BUILD_ROOT}%{_sbin_dir}/
cp -p conf/zoo_sample.cfg ${RPM_BUILD_ROOT}%{_conf_dir}/zoo.cfg

%ifarch amd64 x86_64
[ -d usr/lib64 ] && mkdir -p ${RPM_BUILD_ROOT}%{_lib64_dir} && \
                    cp -p usr/lib64/* ${RPM_BUILD_ROOT}%{_lib64_dir}
%endif

cp -p usr/lib/* ${RPM_BUILD_ROOT}%{_lib_dir}
cp -p usr/bin/* ${RPM_BUILD_ROOT}%{_bin_dir}
cp -pr usr/include/* ${RPM_BUILD_ROOT}%{_include_dir}

%clean 
rm -rf ${RPM_BUILD_ROOT}

%pre
getent group hadoop 2>/dev/null >/dev/null || /usr/sbin/groupadd -r hadoop

/usr/sbin/useradd --comment "ZooKeeper" --shell /bin/bash -M -r --groups hadoop --home %{_share_dir} zookeeper 2> /dev/null || :

%post
bash ${RPM_INSTALL_PREFIX0}/sbin/update-zookeeper-env.sh \
       --prefix=${RPM_INSTALL_PREFIX0} \
       --conf-dir=${RPM_INSTALL_PREFIX1} \
       --log-dir=${RPM_INSTALL_PREFIX2} \
       --pid-dir=${RPM_INSTALL_PREFIX3} \
       --var-dir=${RPM_INSTALL_PREFIX4}

%preun
bash ${RPM_INSTALL_PREFIX0}/sbin/update-zookeeper-env.sh \
       --prefix=${RPM_INSTALL_PREFIX0} \
       --conf-dir=${RPM_INSTALL_PREFIX1} \
       --log-dir=${RPM_INSTALL_PREFIX2} \
       --pid-dir=${RPM_INSTALL_PREFIX3} \
       --var-dir=${RPM_INSTALL_PREFIX4} \
       --uninstall

%files 
%defattr(-,root,root)
%attr(0755,root,hadoop) %{_log_dir}
%attr(0775,root,hadoop) %{_pid_dir}
%attr(0775,root,hadoop) /etc/init.d/zookeeper
%config(noreplace) %{_conf_dir}/*
%{_prefix}

%post lib
/sbin/ldconfig

%files lib
%defattr(-,root,root)
%{_lib_dir}
%{_bin_dir}
