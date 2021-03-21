
%global __requires_exclude ^libwx_baseu-3.1.so|^libwx_baseu_net-3.1.so|^libwx_baseu_xml-3.1.so|^libwx_gtk2u_core-3.1.so|^libwx_gtk2u_html-3.1.so|^libwx_gtk2u_qa-3.1.so

# Compile options:
# invoke with: rpmbuild --with ffmpeg --with local_ffmpeg audacity.spec to use local ffmpeg
%bcond_without  ffmpeg
%bcond_with     local_ffmpeg

#global commit0 53a5c930a4b5b053ab06a8b975458fc51cf41f6c
#global shortcommit0 #(c=#{commit0}; echo ${c:0:7})

Name: audacity-freeworld

Version: 3.0.0
Release: 1%{?dist}
Summary: Multitrack audio editor
License: GPLv2
URL:     http://audacity.sourceforge.net

%define realname audacity
Conflicts: %{realname}

Source0: http://www.fosshub.com/Audacity.html/%{realname}-minsrc-%{version}.tar.xz
# For alpha git snapshots for testing use the github archive as upstream source:
#Source0: https://github.com/audacity/#{realname}/archive/#{commit0}/#{realname}-#{commit0}.tar.gz
# ie wget https://github.com/audacity/audacity/archive/ecdb1d81c9312789c6233aba2190572344b22188/audacity-ecdb1d81c9312789c6233aba2190572344b22188.tar.gz
Source1: https://github.com/audacity/wxWidgets/archive/Audacity-2.4.2.tar.gz#/%{realname}-wxWidgets.tar.gz


%define tartopdir audacity-minsrc-%{version}
#define tartopdir audacity-#{commit0}

# manual can be installed from the base Fedora Audacity package.

# Remove the pathetic wxwidgets check
Patch0: system-wx.patch
# Fix portmidi detection from cmake
Patch1: audacity-2.4.2-fix-portmidi-as-system.patch
# Fix libmp3lame detection from cmake
Patch2:	audacity-2.4.2-fix-libmp3lame-as-system.patch

BuildRequires: cmake
BuildRequires: gettext-devel

%if 0%{?rhel} == 7
BuildRequires: devtoolset-7-toolchain, devtoolset-7-libatomic-devel
%endif
BuildRequires: gcc
BuildRequires: gcc-c++

BuildRequires: alsa-lib-devel
BuildRequires: desktop-file-utils
BuildRequires: expat-devel
BuildRequires: flac-devel
BuildRequires: git
BuildRequires: gtk2-devel
BuildRequires: jack-audio-connection-kit-devel
BuildRequires: ladspa-devel
BuildRequires: lame-devel
BuildRequires: libid3tag-devel
BuildRequires: libjpeg-devel
BuildRequires: libmad-devel
BuildRequires: taglib-devel
BuildRequires: twolame-devel
BuildRequires: libogg-devel
BuildRequires: libsndfile-devel
BuildRequires: libvorbis-devel
BuildRequires: libX11-devel
BuildRequires: libXext-devel
BuildRequires: lilv-devel
BuildRequires: lv2-devel
BuildRequires: portaudio-devel >= 19-16
BuildRequires: portmidi-devel
BuildRequires: serd-devel
BuildRequires: sord-devel
BuildRequires: soundtouch-devel
BuildRequires: soxr-devel
BuildRequires: sqlite-devel
BuildRequires: sratom-devel
BuildRequires: suil-devel
BuildRequires: vamp-plugin-sdk-devel >= 2.0
BuildRequires: zip
BuildRequires: zlib-devel
BuildRequires: python3
%if 0%{?rhel} >= 8 || 0%{?fedora}
BuildRequires: libappstream-glib
%endif

%if %{with ffmpeg}
%if ! %{with local_ffmpeg}
BuildRequires: ffmpeg-devel
%endif
%endif
# For new symbols in portaudio
Requires:      portaudio%{?_isa} >= 19-16

ExcludeArch: s390x

%description
Audacity is a cross-platform multitrack audio editor. It allows you to
record sounds directly or to import files in various formats. It features
a few simple effects, all of the editing features you should need, and
unlimited undo. The GUI was built with wxWidgets and the audio I/O
supports PulseAudio, OSS and ALSA under Linux.
This build has support for mp3 and ffmpeg import/export.


%prep
%setup -q -n %{tartopdir}
mkdir -p %{_vpath_builddir}/cmake-proxies/wxWidgets/wxwidgets
tar -xvf %{SOURCE1} -C %{_vpath_builddir}/cmake-proxies/wxWidgets/wxwidgets --strip 1

%patch0 -p0
%patch1 -p1
%patch2 -p1

%build
%if 0%{?rhel} == 7
export WX_CONFIG=wx-config-3.0
%endif

%if 0%{?rhel} == 7
. /opt/rh/devtoolset-7/enable
%endif

# fix system lame detection
export PKG_CONFIG_PATH=$(pwd):$PKG_CONFIG_PATH

%cmake \
    -Daudacity_use_sndfile=system \
    -Daudacity_use_soxr=system \
    -Daudacity_use_lame=system \
    -Daudacity_use_twolame=system \
    -Daudacity_use_flac=system \
    -Daudacity_use_ladspa=on \
    -Daudacity_use_vorbis=system \
    -Daudacity_use_id3tag=system \
    -Daudacity_use_expat=system \
    -Daudacity_use_soundtouch=system \
    -Daudacity_use_vamp=system \
    -Daudacity_use_lv2=system \
    -Daudacity_use_midi=system \
    -Daudacity_use_ogg=system \
%if %{with ffmpeg}
%if ! %{with local_ffmpeg}
    -Daudacity_use_ffmpeg=linked \
%endif
%else
    -Daudacity_use_fmmpeg=off \
%endif
    -Daudacity_use_wxwidgets=local 

%cmake_build


%install
%cmake_install

%if 0%{?rhel} >= 8 || 0%{?fedora}
if appstream-util --help | grep -q replace-screenshots ; then
# Update the screenshot shown in the software center
#
# NOTE: It would be *awesome* if this file was pushed upstream.
#
# See http://people.freedesktop.org/~hughsient/appdata/#screenshots for more details.
#
appstream-util replace-screenshots $RPM_BUILD_ROOT%{_datadir}/appdata/audacity.appdata.xml \
  https://raw.githubusercontent.com/hughsie/fedora-appstream/master/screenshots-extra/audacity/a.png
fi
%endif

%{find_lang} %{realname}

desktop-file-install --dir $RPM_BUILD_ROOT%{_datadir}/applications \
        $RPM_BUILD_ROOT%{_datadir}/applications/audacity.desktop

mkdir %{buildroot}%{_datadir}/doc/%{realname}/nyquist
cp -pr lib-src/libnyquist/nyquist/license.txt %{buildroot}%{_datadir}/doc/%{realname}/nyquist
cp -pr lib-src/libnyquist/nyquist/Readme.txt %{buildroot}%{_datadir}/doc/%{realname}/nyquist
rm %{buildroot}%{_datadir}/doc/%{realname}/LICENSE.txt


%files -f %{realname}.lang
%{_bindir}/%{realname}
%{_libdir}/%{realname}/
%dir %{_datadir}/%{realname}
%{_datadir}/%{realname}/EQDefaultCurves.xml
%{_datadir}/%{realname}/modules/
%{_datadir}/%{realname}/nyquist/
%{_datadir}/%{realname}/plug-ins/
%{_mandir}/man*/*
%{_datadir}/applications/*
%{_datadir}/appdata/%{realname}.appdata.xml
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/%{realname}.png
%{_datadir}/icons/hicolor/scalable/apps/%{realname}.svg
%{_datadir}/mime/packages/*
%{_datadir}/doc/%{realname}
%license LICENSE.txt

%changelog
* Thu Mar 18 2021 Leigh Scott <leigh123linux@gmail.com> - 3.0.0-1
- 3.0.0
- Use local wxwidgets, audacity isn't usable with gtk3

* Tue Feb 23 2021 Sérgio Basto <sergio@serjux.com> - 2.4.2-4
- partial fedora sync

* Wed Feb 03 2021 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.4.2-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan  1 2021 Leigh Scott <leigh123linux@gmail.com> - 2.4.2-2
- Rebuilt for new ffmpeg snapshot

* Wed Oct 21 2020 Leigh Scott <leigh123linux@gmail.com> - 2.4.2-1
- Update to Audacity 2.4.2

* Wed Sep 02 2020 Leigh Scott <leigh123linux@gmail.com> - 2.3.3-5
- Add GDK_BACKEND=x11 to audacity.desktop exec line (rfbz#5551)
- Fix incorrect appdata.xml type tag (bug #1810509)

* Mon Aug 17 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.3.3-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Thu Mar 26 2020 leigh123linux <leigh123linux@googlemail.com> - 2.3.3-3
- Fix gcc-10 compile issue

* Tue Feb 04 2020 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.3.3-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Sat Nov 23 2019 David Timms <iinet.net.au@dtimms> - 2.3.3-1
- Update to Audacity 2.3.3.
- Modify wxWidgets build require to wxGTK3 (gtk3 version).
- Modify libdir patch for 2.3.3.
- Fix -manual file archive dropping the leading help/ in path.
- Disable twolame for EPEL-8 as the -devel package isn't available.

* Wed Aug 07 2019 Leigh Scott <leigh123linux@gmail.com> - 2.3.2-2
- Rebuild for new ffmpeg version

* Tue Jun  4 2019 David Timms <iinet.net.au@dtimms> - 2.3.2-1
- Update to Audacity 2.3.2 release.
- Rebase audacity-2.3.2-libdir.patch.

* Mon Mar 18 2019 Leigh Scott <leigh123linux@googlemail.com> - 2.3.1-1
- Update to Audacity 2.3.1 release
- Fixes Audacity 2.3.0 broken release (rfbz#5077)

* Mon Mar 04 2019 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.3.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Mon Oct  1 2018 David Timms <iinet.net.au@dtimms> - 2.3.0-1
- Update to Audacity 2.3.0 release.
- change mp3 capability to be always present rather than a compile option.
- Modify audacity-2.2.1-libdir.patch and audacity-2.2.1-libmp3lame-default.patch
    to apply the rpm macro path directly.
- Add grep check to fail if RPMLIB is found in modified source.
- Fix libid3tag configure option.

* Thu Jul 26 2018 RPM Fusion Release Engineering <leigh123linux@gmail.com> - 2.2.2-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Fri Apr 27 2018 Leigh Scott <leigh123linux@googlemail.com> - 2.2.2-5
- Revert 'Use compat-ffmpeg28 on Fedora 28+'

* Thu Mar 08 2018 RPM Fusion Release Engineering <leigh123linux@googlemail.com> - 2.2.2-4
- Rebuilt for new ffmpeg snapshot

* Mon Feb 26 2018 Sérgio Basto <sergio@serjux.com> - 2.2.2-3
- Restore remove after configure
- Remove obsolete scriptlets

* Sun Feb 25 2018 Sérgio Basto <sergio@serjux.com> - 2.2.2-2
- Use compat-ffmpeg28 on Fedora 28+
- Also add conditionals to be possible build with local ffmpeg (not in use)
- Use autoconf before ./configure
- Readd libmp3lame-default.patch and libdir.patch
- Readd to configure --disable-dynamic-loading
- General review of spec
- Comment BR portmidi-devel and remove no-local-includes.patch

* Thu Feb 22 2018 Sérgio Basto <sergio@serjux.com> - 2.2.2-1
- Update to 2.2.2
- Readd no-local-includes.patch
- Reorganize conditonal with_mp3, now have twolame, lame and libmad
- Readd desktop.in.patch
- Add to configure --with-lv2 --with-midi --with-portmidi with some commentaries
- Temporary fix to portaudio became permanent (--with-portaudio=local)

* Thu Feb 01 2018 Sérgio Basto <sergio@serjux.com> - 2.2.1-1
- Update to 2.2.1

* Sun Dec 03 2017 Sérgio Basto <sergio@serjux.com> - 2.2.0-1
- Update to 2.2.0

* Mon Oct 16 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.1.3-5
- Rebuild for ffmpeg update

* Sun Oct 08 2017 Sérgio Basto <sergio@serjux.com> - 2.1.3-4
- Rebuild for soundtouch 2.0.0
- Fix build for new wxBase
- Sync with Fedora proper

* Thu Aug 31 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.1.3-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Sat Apr 29 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.1.3-2
- Rebuild for ffmpeg update

* Fri Mar 24 2017 Leigh Scott <leigh123linux@googlemail.com> - 2.1.3-1
- 2.1.3 release.

* Sat Mar 18 2017 RPM Fusion Release Engineering <kwizart@rpmfusion.org> - 2.1.3-0.10.20161109git53a5c93
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Tue Nov 22 2016 Sérgio Basto <sergio@serjux.com> - 2.1.3-0.9.20161109git53a5c93
- Use bcond_without correctly, fix wx-config-3.0-gtk2 detection, also simplify
  some comments

* Thu Nov 17 2016 David Timms <iinet.net.au@dtimms> - 2.1.3-0.8.20161109git53a5c93
- fix mp3 build parameter by defining mp3importexport conditional.

* Wed Nov  9 2016 David Timms <iinet.net.au@dtimms> - 2.1.3-0.7.20161109git53a5c93
- 2.1.3 Alpha git snapshot 2016-11-09.

* Sat Jul 30 2016 Julian Sikorski <belegdol@fedoraproject.org> - 2.1.2-3
- Rebuilt for ffmpeg-3.1.1

* Wed Jun 22 2016 Nicolas Chauvet <kwizart@gmail.com> - 2.1.2-2
- Backport fix for gcc6

* Thu Mar 03 2016 Sérgio Basto <sergio@serjux.com> - 2.1.2-1
- Update audacity to 2.1.2 final

* Sun Jul 19 2015 David Timms <iinet.net.au@dtimms> - 2.1.1-1
- Release of Audacity 2.1.1.

* Sun Jun 28 2015 David Timms <iinet.net.au@dtimms> - 2.1.1-0.2.dea351a
- remove Source1 reference to manual (available in Fedora audacity build).

* Wed Jun 24 2015 David Timms <iinet.net.au@dtimms> - 2.1.1-0.1.dea351a
- Update to 2.1.1 pre-release git snapshot to prepare for release.
- Conditionalize AppData out of EPEL <=7 release.
- Use better AppData screenshots.

* Mon Jan 12 2015 David Timms <iinet.net.au@dtimms> - 2.0.6-1
- update to upstream release 2.0.6
- update non-dl-ffmpeg.patch to match this version

* Sat Aug 30 2014 Sérgio Basto <sergio@serjux.com> - 2.0.4-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Mon Sep 30 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.0.4-3
- Rebuilt

* Sun Sep 22 2013 David Timms <iinet.net.au@dtimms> - 2.0.4-2
- Add upstream patch to avoid segfault when starting Effects|Equalization

* Sat Sep 14 2013 David Timms <iinet.net.au@dtimms> - 2.0.4-1
- update to upstream release 2.0.4
- rebase audacity-2.0.1-libmp3lame-default

* Sat May  4 2013 Hans de Goede <j.w.r.degoede@gmail.com> - 2.0.3-1
- New upstream release 2.0.3
- Fix FTBFS by using ffmpeg-compat (rf#2707)
- Disable dynamic loading to force proper Requires for the used libs

* Sun Mar 03 2013 Nicolas Chauvet <kwizart@gmail.com> - 2.0.1-2
- Mass rebuilt for Fedora 19 Features

* Tue Jul  3 2012 David Timms <iinet.net.au@dtimms> - 2.0.1-1
- update to 2.0.1 final
- rebase libmp3lame-default.patch
- rebase desktop.in.patch

* Tue Jun 26 2012 David Timms <iinet.net.au@dtimms> - 2.0.1-0.1.rc2
- update to 2.0.1 release candidate 2

* Wed Mar 14 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-1
- update to 2.0.0 final

* Sun Mar 11 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-0.9.rc9
- update to 2.0.0 release candidate 9
- drop upstreamed glib2 include patch

* Tue Mar  6 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-0.8.rc8
- update to 2.0.0 release candidate 8 for testing only

* Wed Feb 22 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-0.3.rc3
- update to 2.0.0 release candidate 3

* Sat Feb 18 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-0.2.rc1.20120218svn11513
- update to release candidate from svn snapshot

* Sun Feb  5 2012 David Timms <iinet.net.au@dtimms> - 2.0.0-0.1.alpha20120205svn11456
- update to 2.0.0 alpha svn snapshot
- delete accepted ffmpeg-0.8.y patch

* Tue Dec 13 2011 David Timms <iinet.net.au@dtimms> - 1.3.14-0.5
- fix Source1 help reference (again).

* Tue Dec 13 2011 David Timms <iinet.net.au@dtimms> - 1.3.14-0.4
- update to 1.3.14 beta release

* Thu Dec  8 2011 David Timms <iinet.net.au@dtimms> - 1.3.14-0.3.alpha20111101svn11296
- add ffmpeg-0.8 patch from Leland Lucius
- add test patch to workaround gtypes-include problem

* Tue Nov  1 2011 David Timms <iinet.net.au@dtimms> - 1.3.14-0.1.alpha20111101svn11296
- update to 1.3.14 alpha svn snapshot

* Sat Apr 30 2011 David Timms <iinet.net.au@dtimms> - 1.3.13-0.4.beta
- fix files and dir ownership including -manual files in the main package

* Tue Apr 26 2011 David Timms <iinet.net.au@dtimms> - 1.3.13-0.2.beta
- delete help file Source reference; will be done in Fedora instead.

* Sun Apr 24 2011 David Timms <iinet.net.au@dtimms> - 1.3.13-0.2.beta
- upgrade to 1.3.13-beta
- drop patches included in upstream release
- convert desktop file to a patch against new upstream .desktop file.

* Wed Nov 10 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.11.beta
- fix build failure compiling ffmpeg.cpp

* Wed Nov 10 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.10.beta
- fix build failure in portmixer due to "Missing support in pa_mac_core.h"
      Applied svn trunk portmixer configure changes.
- del previous patch attempt (unsuccessful)

* Sun Oct 31 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.9.beta
- fix build failure due to portmixer configure problems

* Sun Oct 31 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.8.beta
- fix hang when play at speed with ratio less than 0.09 is used (#637347)

* Sat Aug  7 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.7.beta
- patch to suit APIChange introduced in ffmpeg-0.6. Resolves rfbz #1356.
  fixes ffmpeg import/export.

* Thu Jul 15 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.6.beta
- drop vamp-plugin path patch to suit updated vamp-plugin-sdk-2.1

* Mon Jun 28 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.4.beta
- mods to ease diffs between builds for fedora and full

* Mon Jun 28 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.3.beta
- really package new icons found in icons/hicolor

* Mon Jun 28 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.2.beta
- mod tartopdir to use package version macro

* Mon Jun 28 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.1.3.beta
- fix icons glob to use realname
- add more supported mimetypes and categories to the desktop file

* Mon Jun 28 2010 David Timms <iinet.net.au@dtimms> - 1.3.12-0.1.2.beta
- upgrade to 1.3.12-beta
- package new icons found in icons/hicolor

* Sat Dec  5 2009 David Timms <iinet.net.au@dtimms> - 1.3.10-0.1.1.beta
- upgrade to 1.3.10-beta
- re-base spec to fedora devel and patches by mschwendt 

* Thu Dec  3 2009 David Timms <iinet.net.au@dtimms> - 1.3.9-0.4.2.beta
- continue with upgrade to f12 version

* Mon Nov 16 2009 David Timms <iinet.net.au@dtimms> - 1.3.9-0.4.1.beta
- upgrade to 1.3.9-beta to match Fedora version.
- resync to include new and updated patches from mschwendt 
- add conditional freeworld to allow minimal change from Fedora version

* Fri Oct 23 2009 Orcan Ogetbil <oged[DOT]fedora[AT]gmail[DOT]com> - 1.3.7-0.6.2.beta
- Update desktop file according to F-12 FedoraStudio feature

* Tue May 26 2009 David Timms <iinet.net.au@dtimms> - 1.3.7-0.6.1.beta
- match the 1.3.7.beta version in fedora proper
- include new and updated patches from mschwendt
- del no longer required patches

* Sun Mar 29 2009 Julian Sikorski <belegdol@fedoraproject.org> - 1.3.6-0.4.beta
- wxGTK no longer provides wxGTK2 in Fedora 11

* Sun Mar 29 2009 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info> - 1.3.6-0.3.beta
- rebuild for new F11 features
- revert to 1.3.6.beta for now

* Sat Feb  7 2009 David Timms <iinet.net.au@dtimms> - 1.3.7-0.1.beta
- update to new upstream beta release
- drop beta release 1.3.2 from package

* Sun Dec 14 2008 David Timms <iinet.net.au@dtimms> - 1.3.6-0.2.beta
- add Kevin Koflers portaudio patch to allow output via pulseaudio

* Sun Nov 23 2008 David Timms <iinet.net.au@dtimms> - 1.3.6-0.1.beta
- update to new upstream beta release
- drop libdir patch for now
- drop upstreamed fr.po patch
- add support for ffmpeg import and export via BR and --with-ffmpeg
- add patch to allow selection of ffmpeg library on unix.

* Fri Aug 22 2008 David Timms <iinet.net.au@dtimms> - 1.3.5-0.4.beta
- mod patch2 apply command

* Fri Aug 22 2008 David Timms <iinet.net.au@dtimms> - 1.3.5-0.3.beta
- add Requires lame-libs
- update 1.3.4-gcc43.patch to suit 1.3.5, since patch mostly upstreamed.

* Mon Aug 18 2008 David Timms <iinet.net.au@dtimms> - 1.3.5-0.2.beta
- rename spec and Name to audacity-freeworld.
- add provides/obsoletes audacity-nonfree.
- import livna package into rpmfusion.

* Sun Jun  8 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.5-0.1.beta
- fix bad fr.po that makes Fichier>Open dialog too wide
- sync with F-9 updates-testing
- update to 1.3.5-beta
- tmp patch merged upstream
- expat2 patch merged upstream
- desktop-file: drop deprecated Encoding, drop Icon file extension

* Fri May  9 2008 Michael Schwendt <mschwendt@users.sf.net>
- scriptlets: run update-desktop-database without path
- drop scriptlet dependencies

* Sat May  3 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.4-0.7.20080123cvs
- check ownership of temporary files directory (#436260) (CVE-2007-6061)

* Sat Apr 12 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.4-0.6.20080123cvs
- set a default location for libmp3lame.so.0 again

* Fri Mar 21 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.4-0.5.20080123cvs
- package the old 1.3.2-beta and a post 1.3.4-beta snapshot in the
  same package -- users may stick to the older one, but please help
  with evaluating the newer one
- merge packaging changes from my 1.3.3/1.3.4 test packages:
- build newer release with wxGTK 2.8.x  
- BR soundtouch-devel  and  --with-soundtouch=system
- drop obsolete patches: resample, mp3 export, destdir, FLAC, fr

* Fri Mar 21 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.9.beta
- make soundtouch and allegro build with RPM optflags

* Sun Feb 10 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.8.beta
- rawhide: patch for JACK 0.109.0 API changes (jack_port_lock/unlock removal).
- rebuilt for GCC 4.3 as requested by Fedora Release Engineering
- subst _libdir in ladspa plugin loader

* Thu Jan  3 2008 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.7.beta
- Patch for GCC 4.3.0 C++.

* Fri Nov 16 2007 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.6.beta
- rebuilt for FLAC 1.1.4 -> 1.2.x upgrade, which broke FLAC import

* Mon Mar  5 2007 Michael Schwendt <mschwendt@users.sf.net>
- add umask 022 to scriptlets

* Sat Mar  3 2007 Michael Schwendt <mschwendt[ATusers.sf.net> - 1.3.2-0.5.beta
- build with wxGTK 2.6 compatibility package

* Sat Feb 24 2007 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.4.beta
- patch for FLAC 1.1.4 API compatibility
- patch ExportMP3.cpp (MPEG-2 Layer III bitrates resulted in
  broken/empty files)

* Tue Feb 20 2007 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.3.beta
- patch app init to set a default location for libmp3lame.so.0 
- fix the libmp3lame.so.0 subst
- subst _libdir in libmp3lame search 
- use sed instead of perl

* Sun Feb 18 2007 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.2.beta
- patch the source to use libsamplerate actually and fix Resample.cpp

* Thu Feb 15 2007 Michael Schwendt <mschwendt@users.sf.net> - 1.3.2-0.1.beta
- sync with Fedora Extras 6 upgrade to 1.3.2-beta
- add BR expat-devel jack-audio-connection-kit-devel alsa-lib-devel 
- built-in/patched: nyquist soundtouch
- built-in/patched, n/a: twolame
- adjust configure options accordingly
- patches 1-3 unnecessary, add gemi's audacity-1.3.2-destdir.patch
- make patch from iconv src/Languages.cpp conversion (ISO Latin-1 to UTF-8)
- make patch for locale/fr.po (MAC to ISO Latin-1)

* Wed Oct 18 2006 Michael Schwendt <mschwendt@users.sf.net> - 1.2.4-0.3.b.2
- rename to "audacity-nonfree" and "Conflicts: audacity"

* Fri Oct 06 2006 Thorsten Leemhuis <fedora [AT] leemhuis [DOT] info>
- rebuilt for unwind info generation, broken in gcc-4.1.1-21

* Sun Sep 24 2006 Michael Schwendt <mschwendt[At]users.sf.net>
- rebuild

* Sat Jun  3 2006 Michael Schwendt <mschwendt@users.sf.net> - 1.2.4-0.2.b
- bump and rebuild

* Fri Mar 17 2006 Michael Schwendt <mschwendt@users.sf.net> - 1.2.4-0.1.b
- Update to 1.2.4b (stable release).
- Follow upstream recommendation and use the GTK+ 1.x wxGTK.
  This is because of various issues with fonts/layout/behaviour.
- Build with compat-wxGTK-devel.
- Modify build section to find wx-2.4-config instead of wx-config.

* Thu Mar 09 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- switch to new release field

* Tue Feb 28 2006 Andreas Bierfert <andreas.bierfert[AT]lowlatency.de>
- add dist

* Wed Jul 20 2005 Michael Schwendt <mschwendt@users.sf.net> - 1.2.3-5.lvn.1
- Sync with minor changes in Fedora Extras 4 package.
- Drop Epoch and bump release so this is high enough for an upgrade.

* Fri May 20 2005 David Woodhouse <dwmw2@infradead.org> - 1.2.3-4
- Add more possible MIME types for ogg which may be seen even though
  they're not standard.

* Sun Jan 30 2005 Michael Schwendt <mschwendt@users.sf.net> - 0:1.2.3-1.lvn.1
- Build with mp3 and wxGTK2 by default,
- Make the libmp3lame perl substitution in %%prep more robust.
- s/Fedora/Livna/ in desktop file.

* Sat Nov 20 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.3-1
- New Version 1.2.3

* Sat Oct 30 2004 Michael Schwendt <mschwendt@users.sf.net> - 0:1.2.2-0.fdr.1
- Update to 1.2.2, patch aboutdialog to be readable with wxGTK.

* Mon May 10 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.1-0.fdr.1
- New Version 1.2.1

* Sun Apr 11 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-0.fdr.2
- Fix for Language.cpp restored

* Tue Mar  2 2004 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-0.fdr.1
- New Version 1.2.0

* Mon Nov 24 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-0.fdr.4.pre3
- Added icon
- Separated mp3 plugin

* Sun Nov 23 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-0.fdr.2.pre3
- Changes to specfile

* Sun Nov  2 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-0.fdr.1.pre3
- New upstream version 1.2.0-pre3

* Sat Oct 25 2003 Gerard Milmeister <gemi@bluewin.ch> - 0:1.2.0-pre2.fdr.1
- First Fedora release
