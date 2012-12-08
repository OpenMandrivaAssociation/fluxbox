%define title     Fluxbox
%define style     Met-Anti-Flux-blue

# This is for the debug-flavor.
%define debug 0
%{?fluxbox_debug: %{expand: %%define debug 1}}
%if %{debug}
%define __os_install_post   %nil
%{expand: %%define optflags %optflags -g3}
%endif

Summary:	Windowmanager based on the original blackbox-code
Name:		fluxbox
Version:	1.3.2
Release:	2
Group:		Graphical desktop/Other
License:	MIT
URL:		http://fluxbox.sourceforge.net
Source:		http://prdownloads.sourceforge.net/%{name}/%{name}-%{version}.tar.gz
Source3:	%{name}-icons.tar.bz2
Source4:	%{name}-%{style}.tar.bz2
Source6:	%{name}-artwiz-fonts.tar.bz2
Source10:	%{name}-splash.jpg
Source11:	%{name}-menu-xdg
Patch0:		fluxbox-startfluxbox-pulseaudio.patch
Patch2:		fluxbox-gcc43.patch
BuildRequires:	pkgconfig(imlib2)
BuildRequires:	zlib-devel
BuildRequires:	pkgconfig(ice)
BuildRequires:	pkgconfig(sm)
BuildRequires:	pkgconfig(x11)
BuildRequires:	pkgconfig(xext)
BuildRequires:	pkgconfig(xft)
BuildRequires:	pkgconfig(xinerama)
BuildRequires:	pkgconfig(xpm)
BuildRequires:	pkgconfig(xrandr)
BuildRequires:	pkgconfig(xrender)
BuildRequires:	pkgconfig(fontconfig)
BuildRequires:	mkfontdir

# Make sure these exist
BuildRequires:	alsa-plugins-pulseaudio
BuildRequires:	pulseaudio
BuildRequires:	pulseaudio-module-x11
BuildRequires:	pulseaudio-utils

Requires:	xmessage
Requires:	xdg-compliance-menu

%description
Fluxbox is yet another windowmanager for X. It's a fork from the origi-
nal blackbox-0.61.1 code. Fluxbox looks like blackbox and handles
styles, colors, window placement and similar thing exactly like black-
box. So what's the difference between fluxbox and blackbox then? The
answer is: LOTS!

Have a look at the homepage for more info ;)

%package pulseaudio
Group:		Graphical desktop/Other
Summary:	Enable pulseaudio support
Requires:	%{name} = %{version}-%{release}
Requires:	alsa-plugins-pulseaudio
Requires:	pulseaudio
Requires:	pulseaudio-module-x11
Requires:	pulseaudio-utils

%description pulseaudio
Enable pulseaudio support.

%prep
%setup -q -a3
%patch0 -p0 -b .pulseaudio
%patch2 -p1 -b .gcc43

%build
%configure2_5x \
    --enable-xft \
    --enable-xinerama \
    --enable-imlib2 \
    --enable-nls \
    --with-menu=%{_sysconfdir}/X11/fluxbox/menu \
    --with-style=%{_datadir}/%{name}/styles/%{style} \
    --with-keys=%{_datadir}/%{name}/keys \
    --with-init=%{_datadir}/%{name}/init

%make

%install
%makeinstall_std

# icon
%__install -D -m 644 %{name}48.png %{buildroot}%{_liconsdir}/%{name}.png
%__install -D -m 644 %{name}32.png %{buildroot}%{_iconsdir}/%{name}.png
%__install -D -m 644 %{name}16.png %{buildroot}%{_miconsdir}/%{name}.png

# session file
%__install -d %{buildroot}%{_sysconfdir}/X11/wmsession.d
%__cat > %{buildroot}%{_sysconfdir}/X11/wmsession.d/16fluxbox << EOF
NAME=Fluxbox
ICON=fluxbox.png
EXEC=%{_bindir}/startfluxbox
DESC=%{summary}
SCRIPT:
exec %{_bindir}/startfluxbox
EOF

# menu
%__install -d %{buildroot}%{_sysconfdir}/menu.d
%__install -m 0755 %{SOURCE11} %{buildroot}%{_sysconfdir}/menu.d/%{name}

# Artwiz fonts
%__install -d %{buildroot}%{_datadir}/fonts
%__tar xjf %{SOURCE6} -C %{buildroot}%{_datadir}/fonts/
pushd %{buildroot}%{_datadir}/fonts/fluxbox-artwiz-fonts
mkfontdir
popd

# mdk-style and background.
%__install -d %{buildroot}%{_datadir}/%{name}/{styles,backgrounds}
%__tar xjf %{SOURCE4} -C %{buildroot}%{_datadir}/%{name}
# update background command for fluxbox >= 0.9.15
%__sed -i "s/^rootCommand:.*@WALLPAPER@/background: aspect\nbackground.pixmap: @WALLPAPER@/" %{buildroot}%{_datadir}/%{name}/styles/%{style}
%__sed -i "s,\@WALLPAPER@,%{_datadir}/%{name}/backgrounds/default.png," \
                                           %{buildroot}%{_datadir}/%{name}/styles/%{style}
%__sed -i "s,\@DATADIR\@,%{_datadir}/%{name}," %{buildroot}%{_datadir}/%{name}/styles/%{style}

pushd %{buildroot}%{_datadir}/%{name}/backgrounds/
%__ln_s %{_datadir}/mdk/backgrounds/default.png default.png
popd
%__install %{SOURCE10} %{buildroot}%{_datadir}/%{name}/splash.jpg

# bzip2 manpages (should be automatic, dirty); lenny
%__bzip2 %{buildroot}%{_mandir}/man1/*.1

%__mkdir_p %{buildroot}%{_sysconfdir}/X11/fontpath.d/
%__ln_s ../../..%{_datadir}/fonts/fluxbox-artwiz-fonts \
    %{buildroot}%{_sysconfdir}/X11/fontpath.d/fluxbox-artwiz-fonts:unscaled:pri=50

%__mkdir_p %{buildroot}%{_sysconfdir}
touch -r ChangeLog %{buildroot}%{_sysconfdir}/fluxbox-pulseaudio

%post
%make_session

#blackbox-alternatives
update-alternatives --install %{_bindir}/bsetroot bsetroot %{_bindir}/bsetroot-%{name} 20

%postun
%make_session

# Remove bsetroot-alternatives
if [ "$1" = 0 ]; then
    update-alternatives --remove bsetroot %{_bindir}/bsetroot-%{name}
fi

%files
%defattr(0755,root,root,0755)
%{_bindir}/fbsetbg
%{_bindir}/fbrun
%{_bindir}/fbsetroot
%{_bindir}/fluxbox
%{_bindir}/fluxbox-generate_menu
%{_bindir}/fluxbox-update_configs
%{_bindir}/startfluxbox
%{_bindir}/fluxbox-remote

%config(noreplace) %{_sysconfdir}/X11/%{name}/menu
%config(noreplace) %{_sysconfdir}/X11/wmsession.d/16%{name}
%{_sysconfdir}/menu.d/%{name}

%defattr(0644,root,root,0755)

%doc AUTHORS COPYING ChangeLog INSTALL NEWS README TODO

%{_mandir}/man1/*

%dir %{_datadir}/fonts/fluxbox-artwiz-fonts
%{_datadir}/fonts/fluxbox-artwiz-fonts/*.gz
%{_datadir}/fonts/fluxbox-artwiz-fonts/fonts.dir

%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

%dir %{_datadir}/%{name}
%{_datadir}/%{name}/init
%{_datadir}/%{name}/keys
%{_datadir}/%{name}/splash.jpg
%{_datadir}/%{name}/backgrounds/default.png
%{_datadir}/%{name}/styles/*
%{_datadir}/%{name}/pixmaps/*
%{_sysconfdir}/X11/fontpath.d/fluxbox-artwiz-fonts:unscaled:pri=50
%{_datadir}/%{name}/apps
%{_datadir}/%{name}/overlay
%{_datadir}/%{name}/windowmenu
%{_datadir}/%{name}/nls/*
%{_mandir}/man5/fluxbox-keys.5.*
%{_mandir}/man5/fluxbox-apps.5*
%{_mandir}/man5/fluxbox-menu.5*
%{_mandir}/man5/fluxbox-style.5*

%files pulseaudio
%defattr(-,root,root,755)
%{_sysconfdir}/fluxbox-pulseaudio


%changelog
* Thu Nov 10 2011 Andrey Bondrov <abondrov@mandriva.org> 1.3.2-1mdv2012.0
+ Revision: 729583
- Require xdg-compliance-menu only since 2011
- New version 1.3.2, spec cleanup

* Wed May 18 2011 Funda Wang <fwang@mandriva.org> 1.3.1-2
+ Revision: 675942
- fix build with gcc 4.6

  + Oden Eriksson <oeriksson@mandriva.com>
    - mass rebuild

* Mon Feb 28 2011 Funda Wang <fwang@mandriva.org> 1.3.1-1
+ Revision: 640700
- update to new version 1.3.1

* Sun Feb 27 2011 Funda Wang <fwang@mandriva.org> 1.3.0-2
+ Revision: 640333
- rebuild to obsolete old packages

* Sat Feb 19 2011 Oden Eriksson <oeriksson@mandriva.com> 1.3.0-1
+ Revision: 638783
- 1.3.0

* Mon Feb 14 2011 Paulo Ricardo Zanoni <pzanoni@mandriva.com> 1.1.1-6
+ Revision: 637759
- Require xdg-compliance-menu since the script that updates the menus was moved
  from desktop-common-data to it
- Fix build (patch0 was not applying)

* Fri Dec 03 2010 Funda Wang <fwang@mandriva.org> 1.1.1-5mdv2011.0
+ Revision: 605826
- update file list

  + Oden Eriksson <oeriksson@mandriva.com>
    - rebuild

* Wed Mar 17 2010 Oden Eriksson <oeriksson@mandriva.com> 1.1.1-4mdv2010.1
+ Revision: 522627
- rebuilt for 2010.1

* Wed Sep 02 2009 Christophe Fergeau <cfergeau@mandriva.com> 1.1.1-3mdv2010.0
+ Revision: 424456
- rebuild

* Sat Mar 07 2009 Antoine Ginies <aginies@mandriva.com> 1.1.1-2mdv2009.1
+ Revision: 351030
- rebuild

* Sat Sep 27 2008 Olivier Blin <blino@mandriva.org> 1.1.1-1mdv2009.0
+ Revision: 288880
- 1.1.1 (bugfix, like workspace switch sluggishness)

* Fri Sep 05 2008 Funda Wang <fwang@mandriva.org> 1.1.0.1-1mdv2009.0
+ Revision: 280988
- New version 1.1.0.1
- patch1 merged upstream

* Thu Sep 04 2008 Jérôme Soyer <saispo@mandriva.org> 1.1.0-1mdv2009.0
+ Revision: 280547
- New release

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas

* Wed May 21 2008 Oden Eriksson <oeriksson@mandriva.com> 1.0.0-5mdv2009.0
+ Revision: 209714
- added a gcc43 patch from fedora

* Wed Feb 27 2008 Ademar de Souza Reis Jr <ademar@mandriva.com.br> 1.0.0-5mdv2008.1
+ Revision: 175787
- fix fontpath addition (no more chkfontpath calls)
- improve build-requirments
- do not call mkfontdir in %%post, use %%install instead

* Mon Feb 25 2008 Olivier Blin <blino@mandriva.org> 1.0.0-4mdv2008.1
+ Revision: 174846
- require chkfontpath for post script (#35278)
- fix fonts path in post script (#35278)
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request
    - buildrequires X11-devel instead of XFree86-devel

* Wed Oct 24 2007 Jérôme Soyer <saispo@mandriva.org> 1.0.0-3mdv2008.1
+ Revision: 101693
- Add required files

  + Tomasz Pawel Gajc <tpg@mandriva.org>
    - update to final release

* Fri Jul 06 2007 Ademar de Souza Reis Jr <ademar@mandriva.com.br> 1.0-0.rc3.3mdv2008.0
+ Revision: 49186
- move fonts to standard fonts directory (/usr/share/fonts)
- fix broken fontpath.d symlink

* Fri Jul 06 2007 Ademar de Souza Reis Jr <ademar@mandriva.com.br> 1.0-0.rc3.2mdv2008.0
+ Revision: 49021
- fontpath.d conversion (#31756)


* Sat Apr 07 2007 Olivier Blin <oblin@mandriva.com> 1.0-0.rc3.1mdv2007.1
+ Revision: 150906
- 1.0-rc3
- run autoreconf on distro < 2007.1

* Tue Jan 30 2007 Olivier Blin <oblin@mandriva.com> 1.0-0.rc2.1mdv2007.1
+ Revision: 115284
- drop nls build hack
- remove old debian-style menu
- 1.0rc2

* Sat Dec 16 2006 Olivier Blin <oblin@mandriva.com> 0.9.15.1-5mdv2007.1
+ Revision: 98137
- clean menu macros
- fix background in default style

* Sat Dec 16 2006 Olivier Blin <oblin@mandriva.com> 0.9.15.1-4mdv2007.1
+ Revision: 98123
- generate full menu, not only subsection
- do not concatenate xdg_menu output to current menu, overwrite it instead
- bunzip sources

* Tue Nov 14 2006 Olivier Blin <oblin@mandriva.com> 0.9.15.1-3mdv2007.1
+ Revision: 84164
- bump release
- remove deprecated menu-method file
- require mkfondir for post script
- use Requires(post) instead of Prereq
- require xmessage instead of whole X11R6-contrib
- do not use /usr/X11R6 prefix anymore
- Import fluxbox

* Fri May 05 2006 Frederic Crozat <fcrozat@mandriva.com> 0.9.15.1-2mdk
- add support for XDG menu script
- fix menu-method, we are Mandriva Linux now

* Wed Apr 19 2006 UTUMI Hirosi <utuhiro78@yahoo.co.jp> 0.9.15.1-1mdk
- new release
- remove Patch0 (fluxbox-0.9.11-utf8-slow.patch.bz2)

* Sun Jan 08 2006 Mandriva Linux Team <http://www.mandrivaexpert.com/> 0.9.13-6mdk
- Rebuild

* Wed Aug 24 2005 Gwenole Beauchesne <gbeauchesne@mandriva.com> 0.9.13-5mdk
- varargs fixes

* Wed Jul 13 2005 Olivier Blin <oblin@mandriva.com> 0.9.13-4mdk
- default background is default.png in new mandriva-theme

* Wed Jul 06 2005 Olivier Blin <oblin@mandriva.com> 0.9.13-3mdk
- default background is again Mandrakelinux.png

* Fri Jun 17 2005 Olivier Blin <oblin@mandriva.com> 0.9.13-2mdk
- fix slow UTF-8 (patch from Gentoo)

* Sun May 15 2005 Oden Eriksson <oeriksson@mandriva.com> 0.9.13-1mdk
- 0.9.13

* Thu Mar 24 2005 Olivier Blin <oblin@mandrakesoft.com> 0.9.12-2mdk
- fix default style (use default.png instead of Mandrakelinux.png)

* Wed Jan 19 2005 Lenny Cartier <lenny@mandrakesoft.com> 0.9.12-1mdk
- 0.9.12

* Wed Dec 08 2004 Olivier Blin <blino@mandrake.org> 0.9.11-1mdk
- 0.9.11

* Thu Oct 07 2004 Olivier Blin <blino@mandrake.org> 0.9.10-2mdk
- use sans-10 instead of sans-8 in default style
  (or else the font looks crappy in 0.9.10)

* Wed Sep 15 2004 Michael Scherer <misc@mandrake.org> 0.9.10-1mdk
- New release 0.9.10
- remove patch 0
- remove old nls stuff

* Wed Aug 04 2004 Olivier Blin <blino@mandrake.org> 0.9.9-4mdk
- use the new path for Mandrakelinux wallpaper

* Thu Jul 15 2004 Michael Scherer <misc@mandrake.org> 0.9.9-3mdk 
- rebuild for new gcc, patch from upstream

* Wed May 05 2004 Michael Scherer <misc@mandrake.org> 0.9.9-2mdk 
- fixed #7766

* Sat May 01 2004 Michael Scherer <misc@mandrake.org> 0.9.9-1mdk
- New release 0.9.9

