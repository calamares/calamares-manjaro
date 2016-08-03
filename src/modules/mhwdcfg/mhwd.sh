#!/bin/sh
kernel_cmdline ()
{
    for param in $(/bin/cat /proc/cmdline); do
        case "${param}" in
            $1=*) echo "${param##*=}"; return 0 ;;
            $1) return 0 ;;
            *) continue ;;
        esac
    done
    [ -n "${2}" ] && echo "${2}"
    return 1
}

USENONFREE="$(kernel_cmdline nonfree no)"
VIDEO="$(kernel_cmdline xdriver no)"
DESTDIR="$1"

echo "MHWD-Driver: ${USENONFREE}"
echo "MHWD-Video: ${VIDEO}"

# Video driver
if  [ "${USENONFREE}" == "yes" ] || [ "${USENONFREE}" == "true" ]; then
	if  [ "${VIDEO}" == "vesa" ]; then
		chroot ${DESTDIR} mhwd --install pci video-vesa
	else
		chroot ${DESTDIR} mhwd --auto pci nonfree 0300
	fi
else
	if  [ "${VIDEO}" == "vesa" ]; then
		chroot ${DESTDIR} mhwd --install pci video-vesa
	else
		chroot ${DESTDIR} mhwd --auto pci free 0300
	fi
fi

# Network driver
chroot ${DESTDIR} mhwd --auto pci free 0200
chroot ${DESTDIR} mhwd --auto pci free 0280
