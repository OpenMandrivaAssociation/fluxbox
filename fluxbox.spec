%define name    fluxbox
%define version 1.0.0
%define beta 0
%define rel 3

%if %{beta}
%define sversion %{version}%{beta}
%define release %mkrel 0.%{beta}.%{rel}
%else
%define sversion %{version}
%define release %mkrel %{rel}
%endif

%define title     Fluxbox
%define summary   Windowmanager based on the original blackbox-code
%define style     Met-Anti-Flux-blue

# This is for the debug-flavor.
%define debug 0
%{?fluxbox_debug: %{expand: %%define debug 1}}
%if %debug
%define __os_install_post   %nil
%{expand: %%define optflags %optflags -g3}
%endif

Summary:          %summary
Name:             %name
Version:          %version
Release:          %release
Group:            Graphical desktop/Other
License:          MIT
URL:              http://fluxbox.sourceforge.net
Source:           http://prdownloads.sourceforge.net/%name/%name-%sversion.tar.bz2
Source3:          %name-icons.tar.bz2
Source4:          %name-%style.tar.bz2
Source6:          %name-artwiz-fonts.tar.bz2
Source10:         %name-splash.jpg
Source11:         %name-menu-xdg
Buildrequires:    X11-devel
Requires:         xmessage
Requires(post):   mkfontdir
Requires(post):   chkfontpath
BuildRoot:        %_tmppath/%{name}-%{version}-%{release}-buildroot

%description
Fluxbox is yet another windowmanager for X. It's a fork from the origi-
nal blackbox-0.61.1 code. Fluxbox looks like blackbox and handles
styles, colors, window placement and similar thing exactly like black-
box. So what's the difference between fluxbox and blackbox then? The
answer is: LOTS!

Have a look at the homepage for more info ;)


%prep

%setup -q -a3 -n %{name}-%{sversion}
%if %mdkversion < 200710
autoreconf
%endif

%build
%configure2_5x \
    --enable-kde \
    --enable-xinerama \
    --with-menu=%_sysconfdir/X11/fluxbox/menu \
    --with-style=%_datadir/%name/styles/%style \
    --with-keys=%_datadir/%name/keys \
    --with-init=%_datadir/%name/init
%make

%install
%__rm -rf %buildroot
%makeinstall_std

# icon
%__install -D -m 644 %{name}48.png %buildroot%_liconsdir/%name.png
%__install -D -m 644 %{name}32.png %buildroot%_iconsdir/%name.png
%__install -D -m 644 %{name}16.png %buildroot%_miconsdir/%name.png

# session file
%__install -d %buildroot%_sysconfdir/X11/wmsession.d
%__cat > %buildroot%_sysconfdir/X11/wmsession.d/16fluxbox << EOF
NAME=Fluxbox
ICON=fluxbox.png
EXEC=%_bindir/startfluxbox
DESC=%summary
SCRIPT:
exec %_bindir/startfluxbox
EOF

# menu
%__install -d %buildroot%_sysconfdir/menu.d
%__install -m 0755 %SOURCE11 %buildroot%_sysconfdir/menu.d/%name

# Artwiz fonts
%__install -d %buildroot%_datadir/fonts
%__tar xjf %SOURCE6 -C %buildroot%_datadir/fonts/

# mdk-style and background.
%__install -d %buildroot%_datadir/%name/{styles,backgrounds}
%__tar xjf %SOURCE4 -C %buildroot%_datadir/%name
# update background command for fluxbox >= 0.9.15
%__sed -i "s/^rootCommand:.*@WALLPAPER@/background: aspect\nbackground.pixmap: @WALLPAPER@/" %buildroot%_datadir/%name/styles/%style
%__sed -i "s,\@WALLPAPER@,%_datadir/%name/backgrounds/default.png," \
                                           %buildroot%_datadir/%name/styles/%style
%__sed -i "s,\@DATADIR\@,%_datadir/%name," %buildroot%_datadir/%name/styles/%style

cd %buildroot%_datadir/%name/backgrounds/
ln -s %_datadir/mdk/backgrounds/default.png default.png
cd -
%__install %SOURCE10 %buildroot%_datadir/%name/splash.jpg

# bzip2 manpages (should be automatic, dirty); lenny
%__bzip2 %buildroot%_mandir/man1/*.1

mkdir -p %{buildroot}%_sysconfdir/X11/fontpath.d/
ln -s ../../..%_datadir/fonts/fluxbox-artwiz-fonts \
    %{buildroot}%_sysconfdir/X11/fontpath.d/fluxbox-artwiz-fonts:unscaled:pri=50

%post
%update_menus
%make_session

#blackbox-alternatives
update-alternatives --install %_bindir/bsetroot bsetroot %_bindir/bsetroot-%name 20

#artwiz fontz
cd %_datadir/fonts/fluxbox-artwiz-fonts
%_bindir/mkfontdir
/usr/sbin/chkfontpath -q -a %_datadir/fonts/fluxbox-artwiz-fonts:unscaled


%postun
%clean_menus
%make_session

# Remove bsetroot-alternatives and artwizfonts from fontpath
if [ "$1" = 0 ]; then
    update-alternatives --remove bsetroot %_bindir/bsetroot-%name
fi


%clean
%__rm -rf %buildroot


%files
%defattr(0755,root,root,0755)
%_bindir/fbsetbg
%_bindir/fbrun
%_bindir/fbsetroot
%_bindir/fluxbox
%_bindir/fluxbox-generate_menu
%_bindir/fluxbox-update_configs
%_bindir/startfluxbox
%_bindir/fluxbox-remote

%config(noreplace) %_sysconfdir/X11/%name/menu
%config(noreplace) %_sysconfdir/X11/wmsession.d/16%name
%_sysconfdir/menu.d/%{name}

%defattr(0644,root,root,0755)

%doc AUTHORS COPYING ChangeLog INSTALL NEWS README TODO

%_mandir/man1/*

%dir %_datadir/fonts/fluxbox-artwiz-fonts
%_datadir/fonts/fluxbox-artwiz-fonts/*.gz

%{_liconsdir}/%{name}.png
%{_iconsdir}/%{name}.png
%{_miconsdir}/%{name}.png

%dir %_datadir/%name

%_datadir/%name/init
%_datadir/%name/keys
%_datadir/%name/splash.jpg
%_datadir/%name/backgrounds/default.png
%_datadir/%name/styles/*
%_datadir/%name/pixmaps/*
%_sysconfdir/X11/fontpath.d/fluxbox-artwiz-fonts:unscaled:pri=50

