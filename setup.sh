#!/usr/bin/env bash
export DEEPN_VERSION=3.3
rm -rf dist/*
rm -rf build/*
unzip lists/mm10GeneList.prn.zip ./lists/mm10GeneList.prn
unzip lists/sacCer3GeneBordersIntrons.prn.zip ./lists/sacCer3GeneBordersIntrons.prn
unzip lists/hg38GeneList.prn.zip ./lists/hg38GeneList.prn
python setup_deepn.py py2app --includes sip --packages PyQt4
python setup_genecount.py py2app --includes sip --packages PyQt4
python setup_junctionmake.py py2app --includes sip --packages PyQt4
python setup_gcjm.py py2app --includes sip --packages PyQt4
python setup_queryblast.py py2app --includes sip --packages PyQt4
python setup_readdepth.py py2app --includes sip --packages PyQt4
python setup_statistics.py py2app --includes sip --packages PyQt4

mv dist/Gene\ Count.app dist/DEEPN.app/Contents/Resources
mv dist/Junction\ Make.app dist/DEEPN.app/Contents/Resources
mv dist/GCJM.app dist/DEEPN.app/Contents/Resources
mv dist/Blast\ Query.app dist/DEEPN.app/Contents/Resources
mv dist/Read\ Depth.app dist/DEEPN.app/Contents/Resources
# bunzip2 -c template_dmg/template.dmg.bz2 > dist/temp.dmg
cd dist
mv DEEPN.app DEEPN_${DEEPN_VERSION}.app
mv Stat\ Maker.app Stat\ Maker_${DEEPN_VERSION}.app
tar cvfj DEEPN_${DEEPN_VERSION}_macOS.tar.bz2 DEEPN_${DEEPN_VERSION}.app
tar cvfj Stat_Maker_${DEEPN_VERSION}_macOS.tar.bz2 Stat\ Maker.app
