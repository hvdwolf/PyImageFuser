#!/bin/bash

# Script to make a bundle for PyImageFuser
# version 0.1, 2022-06-06, hvdw

# Requirements:
# Necessary python3 modules

# Some Constants
AppName="PyImageFuser"
BundleDir="PyImageFuser.app"
EA="enfuse_ais"
DMG="PyImageFuser-x86_64"

if [ "$1" = "" ]
then
        printf "\n\nYou have to provide the version\n\n"
        exit
fi

VERSION="$1"
WORKDIR=$(pwd)
printf "\n\nWorkdir = $WORKDIR\n\n"

printf "\n\nGo back to root folder of souce code\n"
cd ../..
ROOTDIR=$(pwd)
printf "\nRootDir = $ROOTDIR\n\n"

printf "\nRemove possible previous build and dist folders and recreate binary\n\n"
rm -rf dist build *.spec
pyinstaller PyImageFuser.py


printf "\nCopy resources\n"
cp -r $EA images docs dist/PyImageFuser

printf "\n\nMove back to our macos folder\n\n"
cd $WORKDIR
#
printf "Remove, create and step into our bundle\n\n"
#
rm -rf ${BundleDir}
cp -r "${BundleDir}.base" ./$BundleDir

printf "\nUpdate Version string to $VERSION\n"
sed  -i '' "s+Version_String+$VERSION+" ${BundleDir}/Contents/Info.plist
#
printf "copy the our PyImageFuser pyinstaller binary into this AppDir folder\n\n"
mv $ROOTDIR/dist/PyImageFuser/* $BundleDir/Contents/MacOS

printf "\nCreate dmg folder and make dmg of it\n"
rm -rf $DMG $DMG_$VERSION.dmg
mkdir -p $DMG
cd $DMG
ln -s /Applications
cp ${ROOTDIR}/LICENSE .
mv ../PyImageFuser.app .
cd ..
hdiutil create -fs HFS+ -srcfolder $DMG -volname "$DMG_$VERSION" "$DMG_$VERSION.dmg"
