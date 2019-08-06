#!/bin/sh

DISTRO=`lsb_release -i | tr -s '\t' ' ' | cut -d' ' -f3`
PKG_MGR=""
PKGS="python3 python3-pip python3-matplotlib"

case $DISTRO in
	Debian|Ubuntu)
		PKG_MGR=apt
		;;
	CentOS)
		PKG_MGR=yum
		;;
	Fedora)
		PKG_MGR=dnf
		;;
	*)
		;;
esac

echo "Using $PKG_MGR package manager on ($DISTRO) distro"
echo "This script will install packages required by COSMOS:\n$DEPS\nContinue? (Y/n)"

read line
case $line in
	Y|y)
		echo "Continuing with the installation"
		;;
	N|n)
		echo "Exiting"
		exit 0
		;;
	*)
		echo "Unknown option. Choose Y or N."
		exit 1
		;;
esac

sudo $PKG_MGR install -y $PKGS

