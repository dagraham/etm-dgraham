#!/bin/bash
yes=$1
#tag=$1
home=`pwd`
plat=`uname`
#echo "home: $home; plat: $plat"
# etm's version numbering now uses the `major.minor.patch` format where each of the three components is an integer:

# - Major version numbers change whenever there is something significant, a large or potentially backward-incompatible change.

# - Minor version numbers change when a new, minor feature is introduced, when a set of smaller features is rolled out or, when the change is from zero to one, when the status of the version has changed from beta to stable.

# - Patch numbers change when a new build is released. This is normally for small bugfixes or the like.

# When the major version number is incremented, both the minor version number and patch number will be reset to zero. Similarly, when the minor version number is incremented, the patch number will be reset to zero. All increments are by one.

# The patch number is incremented by one whenever this script is run to completion. Changes in the major and minor numbers require editing etmQt/v.py.

#cxfreeze3 -OO etmTk/etmtk.py --target-dir ~/etm-tk/dist

asksure() {
echo -n " (Y/N)? "

while read -r -n 1 -s answer; do
  if [[ $answer = [YyNn] ]]; then
    [[ $answer = [Yy] ]] && retval=0
    [[ $answer = [Nn] ]] && retval=1
    break
  fi
done

echo # just a final linefeed, optics...

return $retval
}

#echo Tk/Tcl version information:
#otool -L $(arch -i386 python3 -c 'import _tkinter;\
#               print(_tkinter.__file__)')
#otool -L $(arch -x86_64 python3 -c 'import _tkinter;\
#               print(_tkinter.__file__)')

logfile="prep_dist.txt"
# get the current major.minor.patch tag without trailing p*
#vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g' | sed 's/p.*$//g'`
vinfo=`cat etmTk/v.py | head -1 | sed 's/\"//g' | sed 's/^.*= *//g' `
pre=${vinfo%p*}
post=${vinfo##*p}
if [ "$pre" = "$post" ]; then
    post=0
fi

echo $vinfo $pre $post
patch=${pre#*.*.}
major=${pre%%.*.*}
mm=${pre#*.}
minor=${mm%.*}
if [ "$patch" == "x" ]; then
    patch=-1
fi
#vinfo=$major.$minor.$patch
now=`date`

#head=`git rev-parse --short HEAD`
#echo "'$head'"

# ignore version changes
git update-index --assume-unchanged etmTk/v.py etmTk/version.py
status=`git status -s`
# we want the new version files in the next commit
git update-index --no-assume-unchanged etmTk/v.py etmTk/version.py
if [ "$status" != "" ]; then
    echo "Uncommitted changes:"
    echo "$status"
#    echo "must be committed before running this script."
#    exit
fi

#version=`hg tip --template '{rev}'`
#versioninfo=`hg tip --template '{rev}: {date|isodate}'`
versioninfo=`git log --pretty=format:"%ai" -n 1`
echo "Started: $now" >> $logfile
#echo "Current version: $vinfo ($versioninfo)" >> $logfile

#otag=`git describe --tags --long | sed 's/-[^-]*$//g'`
# return 3.1.38p6 instead of 3.1.38-6-g203afbb
otag=`git describe  | sed 's/-[^-]*$//g' | sed 's/-/p/g'`
omsg=`git log --pretty="%s" -1`

echo "The current version number is $vinfo ($pre post $post $versioninfo)."
echo "The last commit message was:"
echo "    $omsg"
echo -n "Do you want to increment the patch number?"

# ignore changes in v.py and version.py as of 2015-07-26 using
# git update-index --assume-unchanged <file>
# don't ignore
# git update-index --no-assume-unchanged <file>

if asksure; then
    newpatch=$(($patch +1))
    tag=$major.$minor.$newpatch
    change="incremented patch level to $newpatch."
else
    newpost=$(($post +1))
    tag=${major}.${minor}.${patch}p${newpost}
    change="retained patch level $patch - incremented post level to $newpost."
fi
echo "    $tag [$versioninfo]: $change" >> $logfile
echo "version = \"$tag\"" > /Users/dag/etm-tk/etmTk/v.py
echo "version = \"$tag [$versioninfo]\"" > etmTk/version.py
echo "$tag [$versioninfo]" > version.txt
tmsg="Tagged version $tag [$versioninfo]."
echo "tmsg: $tmsg; omsg: $omsg"
git add etmTk/v.py etmTk/version.py
# commit and append the tag message to the last commit message
git commit -a --amend -m "$omsg $tmsg"
# This will be an annotated tag
git tag -a -f $tag -m "$versioninfo"

echo $tag > etmTk/v.txt

./mk_docs.sh

count=100
echo "# Recent changes as of $now:" > CHANGES.txt
     #Changes in the 4 weeks :
#git log --pretty=format:'- %ai %h%d: %an%n%w(70,4,4)%s' --since="$weeks weeks ago" >> "$home/CHANGES.txt"
git log --pretty=format:'- %ar%d %an%n    %h %ai%n%w(70,4,4)%B' --max-count=$count >> "$home/CHANGES.txt"
echo "" >> $home/CHANGES.txt
cp CHANGES.txt etmTk/CHANGES

echo "Creating $tag: $change"
echo "Edit etmTk/v.py to change the major and minor numbers."
echo

cd "$home"
pwd

echo "### processing $tag ###"

echo "Cleaning up build/ and dist/"
sudo rm -fR build/*
sudo rm -fR dist/*

ls build
ls dist

echo "Creating python sdist for $tag"
if [ "$plat" = 'Darwin' ]; then
    python3 -O setup.py sdist --formats=gztar,zip
else
    python -O setup.py sdist --formats=gztar,zip
fi

echo "Finished making sdist for $tag"

cd "$home/dist"
echo
echo "unpacking etmtk-${tag}.tar.gz"
tar -xzf "etmtk-${tag}.tar.gz"
echo

cd "$home"

echo
echo -n "Do system installation?"
if asksure; then
    echo "Building for $plat"
    echo
    echo "changing to etmtk-${tag} and running setup.py"
    cd "$home/dist/etmtk-${tag}"
    pwd
    if [ "$plat" = 'Darwin' ]; then
        echo
        echo "Installing etmtk for python 2" && sudo python2.7 setup.py install
        echo
        echo "Installing etmtk for python 3" && sudo python3 setup.py install
        echo "    Doing system installation" >> $logfile
    else
        echo "installing etmtk for python 2" && sudo python setup.py install
    fi
    echo "Finished system install of etmtk-${tag}"
    cd "$home"
else
    echo "Skipping system wide installaton"
fi

pwd

#echo
#echo Removing etm-tk/dist/etmtk-$tag
## cd /Users/dag/etm-qt/dist && sudo rm -fdR etm_qt-${tag}
#cd "$home"/dist
#rm -fdR etmtk-${tag}

cd "$home"

# # for new pyinstaller???
# pyinstaller  --runtime-hook rthook_pyqt4.py --clean -w --noupx etm_qt

echo
echo -n "Create $plat package?"
if asksure; then
    echo "Building for $plat"
    echo
    sudo rm -fR dist-$plat/*
    if [ "$plat" = 'Darwin' ]; then
        cxfreeze3 -s -c -OO etm --icon=etmTk/etmlogo.icns --target-dir dist-$plat/etmtk-${tag}-freeze-$plat
    else
        cxfreeze -OO etm --target-dir dist-$plat/etmtk-${tag}-freeze-$plat
    fi
    cd dist-$plat
    tar czf etmtk-${tag}-freeze-$plat.tar.gz etmtk-${tag}-freeze-$plat
#    zip -r etmtk-${tag}-freeze-UBUNTU.zip etmtk-${tag}-freeze-UBUNTU
    cd "$home"
    echo "Creating package" >> $logfile
else
    echo "Skipping etm.app creation."
fi
now=`date`
echo "Finished: $now"
echo "    Finished: $now" >> $logfile
