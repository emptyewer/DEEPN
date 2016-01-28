
Text File for comments
>>>GENECOUNT
<b>Gene Count</b> will process the mapped <b>.sam</b> files present in the following folder: <u>mapped_sam_files</u>
<br><br>
<b>Gene Count</b> will generate two folders for its output data:
<br><br>
1. <u>gene_count_summary</u> contains a summary files of genes and their count frequency. 
<br><br>
2. <u>chromosome_files</u> contains more granular data for each gene. 
<br><br>
Be patient....This program is slow but will keep you posted.
>>>END

>>>JUNCTIONMAKE
Make sure all <b>.sam</b> files from your UNmapped reads are in the folder: <u>unmapped_sam_files</u>
<br><br>
<b>Junction Make</b> will scan for junction sequences that span the Gal4 activation domain and the prey.
<br><br>
The <u>junction tag</u> sequence used will be the one entered in the <i>Junction Sequence</i> text box.
<br><br>
Output files will be placed in the <u>junction_files</u> folder as <u>.junctions.txt</u> files. 
>>>END

>>>Comment2
The primary, secondary, and tertiary sequences that will be searched for are:
>>>END

>>>Comment3
Junction_Make is searching .sam files for the junctions that span the GAL4-AD and library insert
The next step converts files to a FASTA file format used for blastn search
The FASTA files are temporary  _TEMP.fa files are located in the blastResults folder

_TEMP.fa files are being converted into "blast.txt" files that contain the blastn results for each junction.
This is done by searching each sequence against the reference cDNA database using blastn.
This takes a while...
>>>END

>>>Comment4
- This program allows you to assess the fusion point between the Gal4AD and each gene/cDNA in question.
- This program queries the blast searches done previously in blast_results_query folder
- Once loaded, you simply type in the NCBI reference number (NM_***)
- The fusion points and their frequency in ppm are displayed
>>>END

Chromosome List for mm10
>>>mm10_Chr_List
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
X
Y_random
Y
Un_random
X_random
1_random
3_random
17_random
M
8_random
7_random
13_random
4_random
9_random
5_random
16_random
1_GL456210_random
1_GL456211_random
1_GL456212_random
1_GL456213_random
1_GL456221_random
4_GL456216_random
4_GL456350_random
4_JH584292_random
4_JH584293_random
4_JH584294_random
4_JH584295_random
5_GL456354_random
5_JH584296_random
5_JH584297_random
5_JH584298_random
5_JH584299_random
7_GL456219_random
Un_GL456239
Un_GL456359
Un_GL456360
Un_GL456366
Un_GL456367
Un_GL456368
Un_GL456370
Un_GL456372
Un_GL456378
Un_GL456379
Un_GL456381
Un_GL456382
Un_GL456383
Un_GL456385
Un_GL456387
Un_GL456389           
Un_GL456390
Un_GL456392
Un_GL456393
Un_GL456394
Un_GL456396
Un_JH584304           
X_GL456233_random
Y_JH584300_random
Y_JH584301_random
Y_JH584302_random
Y_JH584303_random
>>>END

Chromosome List for sacCer3
>>>sacCer3_Chr_List
M
I
II
III
IV
V
VI
VII
VIII
IX
X
XI
XII
XIII
XIV
XV
XVI
>>>END
