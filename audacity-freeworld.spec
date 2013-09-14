Name: audacity-freeworld

Version: 2.0.4
Release: 1%{?dist}
Summary: Multitrack audio editor
Group:   Applications/Multimedia
License: GPLv2
URL:     http://audacity.sourceforge.net

%define realname audacity
Conflicts: %{realname}

# use for upstream source releases:
#Source0: http://downloads.sf.net/sourceforge/audacity/audacity-minsrc-%#{version}-beta.tar.bz2
Source0: http://audacity.googlecode.com/files/audacity-minsrc-%{version}.tar.xz
%define tartopdir audacity-src-%{version}

Patch1: audacity-2.0.4-libmp3lame-default.patch
Patch2: audacity-1.3.9-libdir.patch
# add audio/x-flac
# remove audio/mpeg, audio/x-mp3
# enable startup notification
# add categories Sequencer X-Jack AudioVideoEditing for F-12 Studio feature
Patch3: audacity-2.0.2-desktop.in.patch
Patch4: audacity-2.0.3-non-dl-ffmpeg.patch

Provides: audacity-nonfree = %{version}-%{release}
Obsoletes: audacity-nonfree < %{version}-%{release}

BuildRequires: alsa-lib-devel
BuildRequires: desktop-file-utils
BuildRequires: expat-devel
BuildRequires: flac-devel
BuildRequires: gettext
BuildRequires: jack-audio-connection-kit-devel
BuildRequires: ladspa-devel
BuildRequires: libid3tag-devel
BuildRequires: taglib-devel
BuildRequires: libogg-devel
BuildRequires: libsndfile-devel
BuildRequires: libvorbis-devel
BuildRequires: portaudio-devel >= 19-16
BuildRequires: soundtouch-devel
BuildRequires: soxr-devel
BuildRequires: vamp-plugin-sdk-devel >= 2.0
BuildRequires: zip
BuildRequires: zlib-devel
BuildRequires: wxGTK-devel
BuildRequires: libmad-devel
BuildRequires: ffmpeg-compat-devel
BuildRequires: lame-devel
BuildRequires: twolame-devel
# For new symbols in portaudio
Requires:      portaudio%{?_isa} >= 19-16

%description
Audacity is a cross-platform multitrack audio editor. It allows you to
record sounds directly or to import files in various formats. It features
a few simple effects, all of the editing features you should need, and
unlimited undo. The GUI was built with wxWidgets and the audio I/O
supports PulseAudio, OSS and ALSA under Linux.
This build has support for mp3 and ffmpeg import/export.


%prep
%setup -q -n %{tartopdir}

# Substitute hardcoded library paths.
%patch1 -b .libmp3lame-default
%patch2 -p1 -b .libdir
for i in src/effects/ladspa/LoadLadspa.cpp src/AudacityApp.cpp src/export/ExportMP3.cpp
do
    sed -i -e 's!__RPM_LIBDIR__!%{_libdir}!g' $i
    sed -i -e 's!__RPM_LIB__!%{_lib}!g' $i
done
grep -q -s __RPM_LIB * -R && exit 1

# Substitute occurences of "libmp3lame.so" with "libmp3lame.so.0".
for i in locale/*.po src/export/ExportMP3.cpp
do
    sed -i -e 's!libmp3lame.so\([^.]\)!libmp3lame.so.0\1!g' $i
done

%patch3 -b .desktop.old
%patch4 -p1


%build
export PKG_CONFIG_PATH=%{_libdir}/ffmpeg-compat/pkgconfig/
%configure \
    --disable-dynamic-loading \
    --with-help \
    --with-libsndfile=system \
    --with-libsoxr=system \
    --without-libresample \
    --without-libsamplerate \
    --with-libflac=system \
    --with-ladspa \
    --with-vorbis=system \
    --with-id3tag=system \
    --with-expat=system \
    --with-soundtouch=system \
    --with-libvamp=system \
    --with-portaudio=system \
    --with-ffmpeg=system \
    --with-libmad=system \
    --with-libtwolame=system \
    --with-lame=system \
%ifnarch %{ix86} x86_64
    --disable-sse \
%else
    %{nil}
%endif

# ensure we use the system headers for these, note we do this after
# configure as it wants to run sub-configures in these dirs
for i in ffmpeg libresample libsoxr libvamp portaudio-v19; do
   rm -rf lib-src/$i
done

# _smp_mflags cause problems
make


%install
%make_install

# Audacity 1.3.8-beta complains if the help/manual directories
# don't exist.
mkdir -p $RPM_BUILD_ROOT%{_datadir}/%{name}/help/manual

%{find_lang} %{realname}

desktop-file-install --dir $RPM_BUILD_ROOT%{_datadir}/applications \
%if 0%{?fedora} && 0%{?fedora} < 19
        --vendor fedora --delete-original                          \
%endif
        $RPM_BUILD_ROOT%{_datadir}/applications/audacity.desktop


%post
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :
touch --no-create %{_datadir}/icons/hicolor &>/dev/null || :

%postun
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :
if [ $1 -eq 0 ] ; then
    touch --no-create %{_datadir}/icons/hicolor &>/dev/null
    gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :
fi

%posttrans
gtk-update-icon-cache %{_datadir}/icons/hicolor &>/dev/null || :


%files -f %{realname}.lang
%{_bindir}/%{realname}
%dir %{_datadir}/%{realname}
%{_datadir}/%{realname}/EQDefaultCurves.xml
%{_datadir}/%{realname}/nyquist/
%{_datadir}/%{realname}/plug-ins/
%{_mandir}/man*/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/icons/hicolor/*/apps/%{realname}.*
%{_datadir}/mime/packages/*
%doc %{_datadir}/doc/*


%changelog
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
