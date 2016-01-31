rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist"
python setup_deepn.py py2exe
python setup_genecount.py py2exe
python setup_junctionmake.py py2exe
python setup_queryblast.py py2exe
python setup_gcjm.py py2exe
python setup_readdepth.py py2exe
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Gene Count\dictionaries" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist"
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Gene Count\libraries" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\"
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Gene Count\Y2Hreadme.txt" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist"
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Junction Make\ncbi_blast" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist"
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Blast Query\libraries\xlsxwriter" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\libraries"
move "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist\Blast Query\lists" "C:\Users\%USERNAME%\Documents\GitHub\DEEPN\dist"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Junction Make\libraries"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Gene Count\functions"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Junction Make\functions"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Blast Query\functions"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Read Depth\libraries"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Read Depth\functions"
rd /s /q "C:\Users\Venky\Documents\GitHub\DEEPN\dist\Read Depth\lists"