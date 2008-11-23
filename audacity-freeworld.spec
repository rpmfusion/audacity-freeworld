%define realname audacity
Conflicts: %{realname}

Name: audacity-freeworld
Version: 1.3.6
Release: 0.1.beta%{?dist}
Summary: Multitrack audio editor
Group: Applications/Multimedia
License: GPLv2
URL: http://audacity.sourceforge.net

Source0: http://downloads.sf.net/sourceforge/audacity/audacity-src-1.3.6.tar.bz2
Source1: audacity.png
Source2: audacity.desktop

#Patch1: audacity-1.3.4-libdir.patch
Patch2: audacity-1.3.5-gcc43.patch
Patch3: audacity-1.3.4-libmp3lame-default.patch

# for 1.3.2-beta
Source100: http://downloads.sf.net/sourceforge/audacity/audacity-src-1.3.2.tar.gz
Source101: audacity13.desktop

# iconv on locale/fr.po (MAC to ISO Latin-1)
Patch102: audacity-1.3.2-fr.patch
Patch103: audacity-1.3.2-exportmp3.patch
Patch104: audacity-1.3.2-destdir.patch
Patch105: audacity-1.3.2-resample.patch
Patch106: audacity-1.3.2-FLAC.patch
Patch107: audacity-1.3.2-expat2.patch
Patch108: audacity-1.3.2-gcc43.patch
Patch109: audacity-1.3.2-libdir.patch
Patch110: audacity-1.3.2-jack-api-109.patch
Patch111: audacity-1.3.2-soundtouch-cxxflags.patch
Patch112: audacity-1.3.2-allegro-cflags.patch
Patch113: audacity-1.3.2-libmp3lame-default.patch
Patch114: audacity-1.3.2-CVE-2007-6061.patch

Provides: audacity-nonfree = %{version}-%{release}
Obsoletes: audacity-nonfree < %{version}-%{release}

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: alsa-lib-devel
BuildRequires: desktop-file-utils
BuildRequires: expat-devel
BuildRequires: flac-devel
BuildRequires: gettext
BuildRequires: jack-audio-connection-kit-devel
BuildRequires: ladspa-devel
BuildRequires: libid3tag-devel
BuildRequires: libogg-devel
BuildRequires: libsamplerate-devel
BuildRequires: libsndfile-devel
BuildRequires: libvorbis-devel
BuildRequires: soundtouch-devel
BuildRequires: zip
BuildRequires: zlib-devel
BuildRequires: libmad-devel

# for 1.3.5-beta
BuildRequires: wxGTK2-devel

# for 1.3.2-beta
BuildRequires: compat-wxGTK26-devel

Requires: lame-libs


%description
Audacity is a cross-platform multitrack audio editor. It allows you to
record sounds directly or to import Ogg, WAV, AIFF, AU, IRCAM, or MP3
files. It features a few simple effects, all of the editing features
you should need, and unlimited undo. The GUI was built with wxWindows
and the audio I/O currently uses OSS under Linux. Audacity runs on
Linux/*BSD, MacOS, and Windows.

%prep
%setup -q -a 100 -c

###
### 1.3.6
###

cd audacity-src-1.3.6

# Substitute hardcoded library paths.
#%%patch1 -p1
%patch3 -p1
for i in src/effects/ladspa/LoadLadspa.cpp src/export/ExportMP3.cpp src/AudacityApp.cpp lib-src/libvamp/vamp-sdk/PluginHostAdapter.cpp
do
    sed -i -e 's!__RPM_LIBDIR__!%{_libdir}!g' $i
    sed -i -e 's!__RPM_LIB__!%{_lib}!g' $i
done
grep -q -s __RPM_LIB * -R && exit 1

%patch2 -p1 -b .gcc43
#%%patch4 -p1 -b .fr

# Substitute occurences of "libmp3lame.so" with "libmp3lame.so.0".
for i in locale/*.po src/export/ExportMP3.cpp
do
    sed -i -e 's!libmp3lame.so\([^.]\)!libmp3lame.so.0\1!g' $i
done

cd -


###
### 1.3.2-beta
###

cd audacity-src-1.3.2-beta
%patch102 -p1 -b .fr
%patch103 -p1 -b .exportmp3
%patch104 -p1 -b .destdir
%patch105 -p1 -b .resample
%patch106 -p1 -b .FLAC
%patch107 -p1 -b .expat2
%patch108 -p1 -b .gcc43

# Substitute hardcoded library paths.
%patch109 -p1
%patch113 -p1
for i in src/effects/ladspa/LoadLadspa.cpp src/export/ExportMP3.cpp src/AudacityApp.cpp
do
    sed -i -e 's!__RPM_LIBDIR__!%{_libdir}!g' $i
    sed -i -e 's!__RPM_LIB__!%{_lib}!g' $i
done
grep -q -s __RPM_LIB * -R && exit 1

# F9 devel only
%if 0%{?fedora} > 8
%patch110 -p1 -b .jack-api
%endif

%patch111 -p1 -b .soundtouch-cxxflags
%patch112 -p1 -b .allegro-cflags
%patch114 -p1 -b .CVE-2007-6061

# Substitute occurences of "libmp3lame.so" with "libmp3lame.so.0".
for i in help/wxhelp/audacity.hhk help/wxhelp/exportmp3.htm locale/*.po src/export/ExportMP3.cpp
do
    sed -i -e 's!libmp3lame.so\([^.]\)!libmp3lame.so.0\1!g' $i
done

%ifnarch %{ix86} x86_64
sed -i -e 's!-msse!!' lib-src/soundtouch/source/SoundTouch/Makefile.*
%endif

# for wxGTK26-compat
sed -i -e 's!wx-config!wx-2.6-config!g' configure

cd -


%build
cd audacity-src-1.3.6
%configure \
    --with-help \
    --with-libsndfile=system \
    --without-libresample \
    --with-libsamplerate=system \
    --with-libflac=system \
    --with-ladspa \
    --with-vorbis=system \
    --with-id3tag=system \
    --with-expat=system \
    --with-soundtouch=system \
    --with-libmad=system
# _smp_mflags cause problems
make
cd -

cd audacity-src-1.3.2-beta
%configure \
    --with-help \
    --with-libsndfile=system \
    --without-libresample \
    --with-libsamplerate=system \
    --with-libflac=system \
    --with-ladspa \
    --with-vorbis=system \
    --with-id3tag=system \
    --with-expat=system \
    --program-suffix=13 \
    --with-libmad=system
# _smp_mflags cause problems
make
cd -


%install
rm -rf ${RPM_BUILD_ROOT}

mkdir -p $RPM_BUILD_ROOT%{_datadir}/pixmaps
cp %{SOURCE1} $RPM_BUILD_ROOT%{_datadir}/pixmaps

cd audacity-src-1.3.6
make DESTDIR=${RPM_BUILD_ROOT} install
cd -
%{find_lang} %{realname}

cd audacity-src-1.3.2-beta
make DESTDIR=${RPM_BUILD_ROOT} install
cd -
%{find_lang} %{realname}13
cat %{realname}13.lang >> %{realname}.lang

rm -f $RPM_BUILD_ROOT%{_datadir}/applications/*.desktop
desktop-file-install \
    --vendor fedora \
    --dir $RPM_BUILD_ROOT%{_datadir}/applications \
    %{SOURCE2} %{SOURCE101}


%clean
rm -rf ${RPM_BUILD_ROOT}


%post
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :


%postun
umask 022
update-mime-database %{_datadir}/mime &> /dev/null || :
update-desktop-database &> /dev/null || :


%files -f %{realname}.lang
%defattr(-,root,root,-)
%{_bindir}/%{realname}
%{_bindir}/%{realname}13
%{_datadir}/%{realname}/
%{_datadir}/%{realname}13/
%{_mandir}/man*/*
%{_datadir}/applications/*
%{_datadir}/pixmaps/*
%{_datadir}/mime/packages/*
%doc %{_datadir}/doc/*


%changelog
* Sun Nov 23 2008 David Timms <iinet.net.au@dtimms> - 1.3.6-0.1.beta
- update to new upstream beta release
- drop libdir patch for now
- drop upstreamed fr.po patch

* Thu Aug 22 2008 David Timms <iinet.net.au@dtimms> - 1.3.5-0.4.beta
- mod patch2 apply command

* Thu Aug 22 2008 David Timms <iinet.net.au@dtimms> - 1.3.5-0.3.beta
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

