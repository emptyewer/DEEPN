#!/usr/bin/env bash
rm -rf dist/*
rm -rf build/*
unzip lists/mm10GeneList.prn.zip lists/mm10GeneList.prn
unzip lists/sacCer3GeneBordersIntrons.prn.zip lists/sacCer3GeneBordersIntrons.prn
/usr/bin/python setup_deepn.py py2app --includes sip
/usr/bin/python setup_genecount.py py2app --includes sip
/usr/bin/python setup_junctionmake.py py2app --includes sip
/usr/bin/python setup_gcjm.py py2app --includes sip
/usr/bin/python setup_queryblast.py py2app --includes sip
/usr/bin/python setup_readdepth.py py2app --includes sip
mv dist/Gene\ Count.app dist/DEEPN.app/Contents/Resources
mv dist/Junction\ Make.app dist/DEEPN.app/Contents/Resources
mv dist/GCJM.app dist/DEEPN.app/Contents/Resources
mv dist/Blast\ Query.app dist/DEEPN.app/Contents/Resources
mv dist/Read\ Depth.app dist/DEEPN.app/Contents/Resources

echo "Unzipping Template DMG..."
bunzip2 -c template_dmg/template.dmg.bz2 > dist/temp.dmg
echo "Mount template_dmg/temp.dmg file, copy the DEEPN.app file to the mounted DEEPN folder, unmount temp.dmg, compress temp.dmg (using Disk Utility) and delete temp .dmg and DEEPN.app file."