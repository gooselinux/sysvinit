Summary: Programs which control basic system processes
Name: sysvinit
Version: 2.87
Release: 3.dsf%{?dist}
License: GPLv2+
Group: System Environment/Base
Source: https://alioth.debian.org/frs/download.php/3060/sysvinit-%{version}dsf.tar.gz
URL: https://alioth.debian.org/projects/pkg-sysvinit/
Patch1: sysvinit-2.78-man.patch
Patch2: sysvinit-2.86-autofsck.patch
Patch3: sysvinit-2.86-loginshell.patch
Patch4: sysvinit-2.86-inittab.patch
Patch5: sysvinit-2.86-single.patch
Patch6: sysvinit-2.86-quiet.patch
Patch10: sysvinit-2.87-pidof.patch
Patch11: sysvinit-2.86-pidof-man.patch
Patch12: sysvinit-2.87-sulogin.patch
Patch13: sysvinit-2.87-wide.patch
Patch14: sysvinit-2.87-ipv6.patch
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
Requires: pam >= 0.66-5
Requires: filesystem >= 2.2.4-1
Requires: libselinux >= 1.21.10-1 libsepol >= 1.3.5
Requires: sysvinit-tools = %{version}-%{release}
Obsoletes: SysVinit < 2.86-17
Provides: SysVinit = %{version}-%{release}
BuildRequires: libselinux-devel >= 1.21.10-1 libsepol-devel >= 1.3.5

%description
The sysvinit package contains a group of processes that control
the very basic functions of your system. sysvinit includes the init
program, the first program started by the Linux kernel when the
system boots. Init then controls the startup, running, and shutdown
of all other programs.

%package tools
Summary: Tools used for process and utmp management.
Group: System Environment/Base

%description tools
The sysvinit-tools package contains various tools used for process
management.

%prep
%setup -q -n sysvinit-%{version}dsf
# We use a shell, not sulogin. Other random man fixes go here (such as #192804)
%patch1 -p1 -b .manpatch
# Unlink /.autofsck on shutdown -f
%patch2 -p1 -b .autofsck
# Invoke single-user shell as a login shell (#105653)
%patch3 -p1 -b .loginshell
# Adjust examples in inittab(5) to more accurately reflect RH/Fedora
# usage (#173572)
%patch4 -p1 -b .inittabdocs
# Fix single user mode (#176348)
%patch5 -p1 -b .single
# Be less verbose when booted with 'quiet'
%patch6 -p1 -b .quiet
# Fix various things in pidof - pidof /x/y matching /z/y, pidof -x
# for scripts, etc.
%patch10 -p1 -b .pidof
# Document some of the behavior of pidof. (#201317)
%patch11 -p1 -b .pidof
# get_default_context_with_level returns 0 on success (#568531)
%patch12 -p1 -b .sulogin
# Add wide output names with -w (#585907)
%patch13 -p1 -b .wide
# Change accepted ipv6 addresses (#585880)
%patch14 -p1 -b .ipv6


%build
make %{?_smp_mflags} CC="%{__cc}" CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE" LDFLAGS="" LCRYPT="-lcrypt" -C src

%install
rm -rf $RPM_BUILD_ROOT
for I in bin sbin usr/{bin,include} %{_mandir}/man{1,3,5,8} etc var/run dev; do
	mkdir -p $RPM_BUILD_ROOT/$I
done
make -C src ROOT=$RPM_BUILD_ROOT MANDIR=%{_mandir} STRIP=/bin/true \
	BIN_OWNER=`id -nu` BIN_GROUP=`id -ng` install

rm -f $RPM_BUILD_ROOT/bin/pidof
ln -snf killall5 $RPM_BUILD_ROOT/sbin/pidof
rm -f $RPM_BUILD_ROOT/sbin/bootlogd
rm -f $RPM_BUILD_ROOT/%{_mandir}/man8/bootlogd*
chmod 755 $RPM_BUILD_ROOT/usr/bin/utmpdump

# Remove these files, as we use upstart as /sbin/init.
rm -f $RPM_BUILD_ROOT/sbin/{halt,init,poweroff,reboot,runlevel,shutdown,telinit}
rm -f $RPM_BUILD_ROOT/%{_includedir}/initreq.h
rm -f $RPM_BUILD_ROOT/%{_mandir}/man5/*
rm -f $RPM_BUILD_ROOT/%{_mandir}/man8/{halt,init,poweroff,reboot,runlevel,shutdown,telinit}*

%post
[ -x /sbin/telinit -a -p /dev/initctl -a -f /proc/1/exe -a -d /proc/1/root ] && /sbin/telinit u
exit 0

%clean
rm -rf $RPM_BUILD_ROOT

%if 0
# Disabled for upstart.
%files
%defattr(-,root,root)
%doc doc/Changelog doc/Install COPYRIGHT
/sbin/halt
/sbin/init
/sbin/poweroff
/sbin/reboot
/sbin/runlevel
/sbin/shutdown
/sbin/telinit
%{_includedir}/initreq.h
%{_mandir}/man5/*
%{_mandir}/man8/halt*
%{_mandir}/man8/init*
%{_mandir}/man8/poweroff*
%{_mandir}/man8/reboot*
%{_mandir}/man8/runlevel*
%{_mandir}/man8/shutdown*
%{_mandir}/man8/telinit*
%endif

%files tools
%defattr(-,root,root)
%doc doc/Changelog COPYRIGHT
/bin/mountpoint
%{_bindir}/last
%{_bindir}/lastb
%{_bindir}/mesg
%{_bindir}/utmpdump
%attr(2555,root,tty)  /usr/bin/wall
/sbin/pidof
/sbin/killall5
/sbin/sulogin
%{_mandir}/man1/*
%{_mandir}/man8/killall5*
%{_mandir}/man8/pidof*
%{_mandir}/man8/sulogin*

%changelog
* Tue Apr 27 2010 Petr Lautrbach <plautrba@redhat.com> 2.87-3.dsf
- Add -w option to last command for wide output (#585907)
- Changed IPv4 vs IPv6 heuristic in last command (#585880)

* Mon Mar 08 2010 Petr Lautrbach <plautrba@redhat.com> 2.87-2.dsf
- fix using get_default_context_with_level (#568531)

* Thu Sep 17 2009 Ville Skyttä <ville.skytta@iki.fi> - 2.87-1.dsf
- Avoid stripping binaries during build to fix -debuginfo.

* Mon Jul 27 2009 Bill Nottingham <notting@redhat.com> - 2.87-0.dsf
- Update to new upstream release 2.87dsf
-- remove many upstreamed/obsolete patches

* Sun Jul 26 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.86-28
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Wed Feb 25 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.86-27
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Mon Dec  8 2008 Bill Nottingham <notting@redhat.com> - 2.86-26
- document readlink() behavior in pidof (#201317)
- fix potential issue in utmpdmp (#473485)

* Wed Oct  1 2008 Bill Nottingham <notting@redhat.com> - 2.86-25
- rediff patches (#464940)
- remove change_console, it's no longer needed with plymouth

* Tue Mar 11 2008 Bill Nottingham <notting@redhat.com> - 2.86-24
- replace change_console with a script that does the proper upstart
  machinations

* Fri Mar  7 2008 Bill Nottingham <notting@redhat.com> - 2.86-23
- move mountpoint to -tools subpackage
- don't build sysvinit package itself

* Fri Feb 29 2008 Bill Nottingham <notting@redhat.com> - 2.86-22
- don't kill pid 1 with killall5

* Fri Feb 15 2008 Bill Nottingham <notting@redhat.com> - 2.86-21
- split off a -tools subpackage to avoid upstart conflicts (#431110)

* Fri Feb 15 2008 Bill Nottingham <notting@redhat.com> - 2.86-20
- don't abort if policy is already loaded (#431113)

* Wed Oct 10 2007 Bill Nottingham <notting@redhat.com> - 2.86-18
- rebuild for buildid

* Fri Aug  3 2007 Bill Nottingham <notting@redhat.com>
- tweak license tag

* Fri May  4 2007 Bill Nottingham <notting@redhat.com> - 2.86-17
- rename to sysvinit to match upstream, do the usual
  provides/obsoletes (#226475)

* Mon Apr 16 2007 Bill Nottingham <notting@redhat.com> - 2.86-16
- pidof: ignore '-c' when called as non-root (#230829)

* Tue Feb 13 2007 Bill Nottingham <notting@redhat.com> - 2.86-15
- spec cleanups; remove initunlvl part of %%post, as that hasn't
  been supported for nearly 4 years

* Fri Oct 13 2006 Bill Nottingham <notting@redhat.com> - 2.86-14
- revert fix for #184340 (#210549, #209169)

* Sun Oct 01 2006 Jesse Keating <jkeating@redhat.com> - 2.86-13
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Thu Sep 21 2006 Bill Nottingham <notting@redhat.com> - 2.86-12
- set controlling tty for /etc/rc so that ctrl-c can be passed to hung
  services (#184340)

* Thu Aug 10 2006 Bill Nottingham <notting@redhat.com> - 2.86-11
- fix warning on SELinux policy load failure (#185603)
- don't package /dev/initctl (#174652, #199939)
- allow some time for failed console opens to resolve themselves (#181546)
- add documentation of -f to last(1) (#192804)

* Wed Aug  9 2006 Bill Nottingham <notting@redhat.com> - 2.86-9
- preserve 'WAITING' across re-exec (#143289, others)
- actually apply quiet patch
- don't write garbage to utmp on x86-64 (#176494)

* Tue Aug  8 2006 Bill Nottingham <notting@redhat.com> - 2.86-7
- be slightly less verbose when booted with 'quiet'

* Wed Jul 19 2006 Bill Nottingham <notting@redhat.com> - 2.86-6
- fix IPv6 patch (<mzazrive@redhat.com>)

* Tue Jul 18 2006 Bill Nottingham <notting@redhat.com> - 2.86-5
- IPv6 support for last (<mzazrive@redhat.com>)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.86-4.1
- rebuild

* Wed May 10 2006 Bill Nottingham <notting@redhat.com> - 2.86-3
- fix potential under-copy of proc title (#188160, <kir@sacred.ru>)

* Fri Mar 17 2006 Bill Nottingham <notting@redhat.com> - 2.86-3
- document that the kernel may sync even if reboot is called with -n (#180967)

* Mon Feb 13 2006 Bill Nottingham <notting@redhat.com> - 2.86-2.2.2
- and again...

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.86-2.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.86-2.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Wed Dec 21 2005 Bill Nottingham <notting@redhat.com> - 2.86-2
- fix single user mode (#176348)

* Mon Dec 19 2005 Bill Nottingham <notting@redhat.com> - 2.86-1
- update to upstream 2.86
- adjust patches
- install initreq.h (#119039)
- allow halt/reboot to handle being called by login correctly (#104062, <worley@theworld.com>)
- document pam_console usage for halt (#114970)

* Fri Dec 16 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt for new gcj

* Mon Dec 5 2005 Dan Walsh <dwalsh@redhat.com> - 2.85-43
- Use log(L_VB for SELinux error

* Fri Nov 18 2005 Bill Nottingham <notting@redhat.com>
- clean up examples in inittab(5) (#173572)

* Sat Oct 14 2005 Dan Walsh <dwalsh@redhat.com> - 2.85-42
- Fix patch

* Fri Oct 14 2005 Dan Walsh <dwalsh@redhat.com> - 2.85-41
- replace load_policy with selinux_init_load_policy
- add getseuserbyname to sulogin

* Thu Jun 30 2005 Bill Nottingham <notting@redhat.com> - 2.85-40
- pidof: fix the fix for #85796, which broke the fix for #138788

* Wed Apr 27 2005 Bill Nottingham <notting@redhat.com> - 2.85-39
- invoke single-user shell as a login shell (#105653)

* Mon Apr 25 2005 Bill Nottingham <notting@redhat.com> - 2.85-38
- pidof: use readlink instead of stat to avoid NFS hangs (#138788, <constgq@yahoo.com))
- pidof: fix handling of scripts (#85796)
- pidof: add -c option for only matching processes with the same root (<twoerner@redhat.com>)

* Wed Feb 23 2005 Bill Nottingham <notting@redhat.com> - 2.85-37
- add patch for SELinux user configs (<dwalsh@redhat.com>)
- disable readlink patch while it's being fixed

* Mon Nov 15 2004 Bill Nottingham <notting@redhat.com> - 2.85-35
- use readlink instead of stat to avoid NFS hangs (#138788, <constgq@yahoo.com>)

* Thu Oct 07 2004 Florian La Roche <Florian.LaRoche@redhat.de>
- add patch from Steve Grubb to re-build as non-root, #131841

* Fri Sep 17 2004 Bill Nottingham <notting@redhat.com> 2.85-33
- updated SELinux patch from Stephen Smalley

* Wed Aug 11 2004 Dan Walsh <dwalsh@redhat.com> 2.85-32
- Read booleans file to setup booleans on reboot

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Wed Jun 8 2004 Dan Walsh <dwalsh@redhat.com> 2.85-30
- Remove MLS Support from selinux patch, new design allows this for free

* Thu Jun 3 2004 Dan Walsh <dwalsh@redhat.com> 2.85-29
- Add MLS Support to selinux patch

* Thu Jun  3 2004 Bill Nottingham <notting@redhat.com> 2.85-28
- fix overrun of argv[0] (#125172, #124813, <alexl@redhat.com>)

* Wed Jun  2 2004 Bill Nottingham <notting@redhat.com> 2.85-27
- cleanup logic some

* Thu May 27 2004 Dan Walsh <dwalsh@redhat.com> 2.85-26
- Use selinux_getenforcemode

* Tue May 25 2004 Dan Walsh <dwalsh@redhat.com> 2.85-25
- Change to use /etc/sysconfig/selinux to find policy file.

* Thu Apr 29 2004 Bill Nottingham <notting@redhat.com> 2.85-25
- fix build warning on make install (#121977)
- umount the SELinux filesystem on disabling it

* Fri Apr 23 2004 Dan Walsh <dwalsh@redhat.com> 2.85-24
- Add security-disable, for disabling SELinux entirely

* Mon Apr  5 2004 Bill Nottingham <notting@redhat.com> 2.85-23
- fix selinux=0 booting (#118826, #119037)

* Tue Mar 23 2004 Bill Nottingham <notting@redhat.com> 2.85-22
- move /selinux to filesystem
- print out warning if we're terminating because of enforcing + no policy
- handle non-selinux kernels better (#118826)

* Thu Mar 18 2004 Bill Nottingham <notting@redhat.com> 2.85-21
- fix parsing of /proc/cmdline

* Tue Mar 16 2004 Bill Nottingham <notting@redhat.com> 2.85-20
- handle /etc/sysconfig/selinux

* Tue Mar 9 2004 Dan Walsh <dwalsh@redhat.com> 2.85-19
- Add SELinux support to sulogin

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Feb 10 2004 Dan Walsh <dwalsh@redhat.com> 2.85-17
- Check for current policy and previous depending on how policy was written

* Thu Feb  5 2004 Jonathan Blandford <jrb@redhat.com> 2.85-15
- rebuild w/o SELINUX for RHEL 3 U2

* Mon Dec 22 2003 Dan Walsh <dwalsh@redhat.com> 2.85-15
- Change pidof to not call getsid since it does not use it
- Eliminates SELinux access control.

* Wed Dec 17 2003 Dan Walsh <dwalsh@redhat.com> 2.85-14
- set selinux-mnt so libraries will work.

* Wed Dec 17 2003 Dan Walsh <dwalsh@redhat.com> 2.85-13
- Rollback

* Wed Dec 17 2003 Dan Walsh <dwalsh@redhat.com> 2.85-12
- Fix protocol change via libselinux that broke sysinit.

* Mon Dec 1 2003 Dan Walsh <dwalsh@redhat.com> 2.85-11.sel
- Don't umount /selinux, this is required for selinux to work correctly.

* Fri Oct 24 2003 Dan Walsh <dwalsh@redhat.com> 2.85-10.sel
- Create /selinux mount point
- Don't exit on non selinux kernel boot.

* Fri Oct 24 2003 Dan Walsh <dwalsh@redhat.com> 2.85-9.sel
- close file descriptor

* Tue Oct 21 2003 Dan Walsh <dwalsh@redhat.com> 2.85-8.sel
- Remove constants that were added to libselinux

* Tue Oct 21 2003 Dan Walsh <dwalsh@redhat.com> 2.85-7.sel
- Fix error handling on enforcing kernels

* Tue Oct 21 2003 Dan Walsh <dwalsh@redhat.com> 2.85-7
- Turn off selinux

* Mon Oct 20 2003 Dan Walsh <dwalsh@redhat.com> 2.85-6.sel
- add selinux processing

* Mon Sep 22 2003 Bill Nottingham <notting@redhat.com> 2.85-5
- add change_console, for changing console used by init

* Wed Jun 25 2003 Bill Nottingham <notting@redhat.com> 2.85-4
- block signals when calling syslog() (#97534, <joden@lee.k12.nc.us>)

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri May 23 2003 Bill Nottingham <notting@redhat.com> 2.85-2
- clean up killall5 some

* Thu May 22 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- update to 2.85, remove already applied patches

* Mon Feb 10 2003 Bill Nottingham <notting@redhat.com> 2.84-13
- fix s390x build
- fix silly warning (#83943)

* Mon Feb 10 2003 Arjan van de Ven <arjanv@redhat.com>
- fix wait() handling wrt setting SIGCHLD to SIG_IGN in shutdown
- fix segfault in spawn() function in shutdown

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Thu Dec 05 2002 Elliot Lee <sopwith@redhat.com> 2.84-7
- Pass __cc macro to build, to facilitate cross-compiling
- _smp_mflags

* Mon Dec  2 2002 Bill Nottingham <notting@redhat.com> 2.84-6
- rebuild on all arches
- change sulogin message to be slightly more correct (#65828)

* Thu Jul 18 2002 Bill Nottingham <notting@redhat.com>
- don't strip binaries
- have wall not write to non-ttys (#65412)
- update usage for halt/reboot (#57753)
- allow '-t' argument to last for checking state at certain times (#56863)
- make 'pidof /foo/bar' not match /baz/bar (#53918)

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Mar 12 2002 Bill Nottingham <notting@redhat.com> 2.84-2
- add patch to log messages on shutdown/reboot

* Fri Feb 22 2002 Bill Nottingham <notting@redhat.com> 2.84-1
- update to 2.84

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Fri Nov  9 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.79-2
- Fix pidof -o (#55954)
- Handle RPM_OPT_FLAGS
- s/Copyright/License/

* Mon Sep 17 2001 Bill Nottingham <notting@redhat.com>
- update to 2.79

* Tue Aug 28 2001 Bill Nottingham <notting@redhat.com>
- unlink /.autofsck on shutdown -f

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Thu Jun 21 2001 Bill Nottingham <notting@redhat.com>
- update 'no logout' patch
- fix setting of CREAD to work with 2.4.3+ kernels (#45284)

* Tue Jun 12 2001 Bill Nottingham <notting@redhat.com>
- show users with no login pid but no logout record as gone (#42550,
  <cwolf@starclass.com>)
- fix sulogin to *always* work without a tty (#40934)

* Tue Apr  3 2001 Bill Nottingham <notting@redhat.com>
- set umask 022 on startup
- manpage tweaks (#21628, #27173)

* Mon Apr  2 2001 Bill Nottingham <notting@redhat.com>
- fix dangling symlink in %%doc (#34383)

* Thu Mar 15 2001 Bill Nottingham <notting@redhat.com>
- don't run telinit u if we don't appear to be on the root fs

* Fri Feb 16 2001 Bill Nottingham <notting@redhat.com>
- run telinit u on upgrade

* Wed Jan 31 2001 Bill Nottingham <notting@redhat.com>
- document '-n' option to wall, make it root-only (#18672)
- don't open files in sulogin unless they're really ttys (#21862)

* Tue Aug  8 2000 Bill Nottingham <notting@redhat.com>
- set SHLVL in sulogin so /etc/profile.d stuff isn't run by default

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jun  8 2000 Bill Nottingham <notting@redhat.com>
- fix the md5 code (#11534)
- rebuild for FHS & the like

* Wed Apr 19 2000 Bill Nottingham <notting@redhat.com>
- ignore sigint in sulogin (#9803)
- touch file in root directory if powering off (#7318)

* Tue Mar  7 2000 Jeff Johnson <jbj@redhat.com>
- rebuild for sparc baud rates > 38400.

* Thu Feb 24 2000 Bill Nottingham <notting@redhat.com>
- update to 2.78-final

* Mon Feb  7 2000 Bill Nottingham <notting@redhat.com>
- handle compressed manpages

* Mon Jan 31 2000 Cristian Gafton <gafton@redhat.com>
- build to fix dependency problem

* Tue Jan 10 2000 Bill Nottingham <notting@redhat.com>
- update to 2.78

* Mon Sep 06 1999 Jakub Jelinek <jj@ultra.linux.cz>
- on big endian machines use a kludge for broken pam md5 passwords

* Fri Aug 27 1999 Bill Nottingham <notting@redhat.com>
- update to 2.77

* Tue Jul 06 1999 Bill Nottingham <notting@redhat.com>
- move pam_console stuff to usermode package

* Fri Jul 02 1999 Cristian Gafton <gafton@redhat.com>
- requires usermode to express the dependency on /usr/bin/consolehelper
(#2813)

* Wed Jun 23 1999 Bill Nottingham <notting@redhat.com>
- make man page references to single-user mode consistent with RH usage

* Sat Apr 17 1999 Jeff Johnson <jbj@redhat.com>
- remove /etc/initlvl compatibility symlink from file list (#2236).

* Fri Mar 26 1999 Michael Johnson <johnsonm@redhat.com>
- pam.d files marked noreplace
- added poweroff as a console application

* Mon Mar 22 1999 Michael Johnson <johnsonm@redhat.com>
- marked config files as such in consolehelper part of filelist

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 8)

* Fri Mar 19 1999 Michael Johnson <johnsonm@redhat.com>
- consolehelper support

* Wed Jan 06 1999 Cristian Gafton <gafton@redhat.com>
- glibc 2.1

* Sun Aug 23 1998 Jeff Johnson <jbj@redhat.com>
- poweroff symlink not included (problem #762)

* Thu Jul 09 1998 Chris Evans <chris@ferret.lmh.ox.ac.uk>
- Fix a securelevel releated security hole. Go on, try and break append
  only files + securelevel now ;-)

* Wed Jul  8 1998 Jeff Johnson <jbj@redhat.com>
- remove /etc/nologin at end of shutdown.
- compile around missing SIGPWR on sparc

* Thu May 07 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Wed Apr 08 1998 Cristian Gafton <gafton@redhat.com>
- upgraded to 2.74
- fixed the package source url... (yeah, it was wrong !)

* Wed Oct 1 1997 Cristian Gafton <gafton@redhat.com>
- fixed the MD5 check in sulogin (128 hash bits encoded with base64 gives
  22 bytes, not 24...). Fix in -md5.patch

* Thu Sep 11 1997 Christian 'Dr. Disk' Hechelmann <drdisk@ds9.au.s.shuttle.de>
- /etc/initrunlvl gets linked to /tmp/init-root/var/run/initrunlvl which is
  just plain wrong..
- /usr/bin/utmpdump was missing in the files section, although it was
  explicitly patched into PROGS.
- added attr's to the files section.
- various small fixes.

* Tue Jun 17 1997 Erik Troan <ewt@redhat.com>
- updated to 2.71
- built against glibc 2.0.4

* Fri Feb 07 1997 Michael K. Johnson <johnsonm@redhat.com>
- Added sulogin.8 man page to file list.
