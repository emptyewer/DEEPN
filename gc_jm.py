import sys
import subprocess

main_directory = sys.argv[1]
gene_dictionary = sys.argv[2]
chromosomes_list_name = sys.argv[3]

junction_sequence = sys.argv[4]
exclusion_sequence = sys.argv[5]
blast_db_name = sys.argv[6]

gene_count_exe = sys.argv[7]
junction_make_exe = sys.argv[8]

combined = sys.argv[9]

subprocess.call([gene_count_exe,  main_directory, gene_dictionary, chromosomes_list_name, combined], shell=False)
subprocess.call([junction_make_exe, main_directory, junction_sequence, exclusion_sequence, blast_db_name, combined], shell=False)
