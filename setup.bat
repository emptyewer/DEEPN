rd /s /q ".\dist"
python setup_deepn.py py2exe
python setup_genecount.py py2exe
python setup_junctionmake.py py2exe
python setup_queryblast.py py2exe
python setup_gcjm.py py2exe
python setup_readdepth.py py2exe
rem move ".\dist\Gene Count\dictionaries" ".\dist"
rem move ".\dist\Gene Count\libraries" ".\dist\"
rem move ".\dist\Gene Count\Y2Hreadme.txt" ".\dist"
rem move ".\dist\Junction Make\ncbi_blast" ".\dist"
rem move ".\dist\Blast Query\libraries\xlsxwriter" ".\dist\libraries"
rem move ".\dist\Blast Query\lists" ".\dist"
rem rd /s /q ".\dist\Junction Make\libraries"
rem rd /s /q ".\dist\Gene Count\functions"
rem rd /s /q ".\dist\Junction Make\functions"
rem rd /s /q ".\dist\Blast Query\functions"
rem rd /s /q ".\dist\Read Depth\libraries"
rem rd /s /q ".\dist\Read Depth\functions"
rem rd /s /q ".\dist\Read Depth\lists"