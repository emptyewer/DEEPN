import sys
import signal
import functions.fileio_gui as f
import functions.junctionf_gui as j
import functions.printio_gui as p

input_data_folder = 'unmapped_sam_files'     #Manage name of input folder here
junction_folder = 'junction_files'            #Manage name of junction reads output folder here
blast_results_folder = 'blast_results'            #Manage name of blast results output folder here
blast_results_query = 'blast_results_query'     #Manage name of blast results dictionary output folder here

main_directory = sys.argv[1]
junction_sequence = sys.argv[2]
exclusion_sequence = sys.argv[3]
blast_db_name = sys.argv[4]

def initialize_folders(directory):
    fileio.create_new_folder(directory, junction_folder)
    # Creates the folder that will hold the Genecounts summaries
    fileio.create_new_folder(directory, blast_results_folder)
    # Creates the folder that will hold more granualar data on exon counts per chromosome
    fileio.create_new_folder(directory, blast_results_query)
    # printio.show_message("Files will be processed and saved to the following directories\n\n"
    #                      "1. Input Files : %s\n\n"
    #                      "2. Output Directory: %s\n\n" % (os.path.join(main_directory, input_folder),
    #                                                       os.path.join(main_directory, summary_folder)))


if __name__ == '__main__':
    printio = p.printio()
    fileio = f.fileio()
    junctionf = j.junctionf(fileio, printio)
    sys.stdout.write("\n*** Junction Search ***\n\n")
    sys.stdout.flush()
    signal.signal(signal.SIGTERM, junctionf.sigterm_handler)

    # printio.print_comment("Comment1")
    # fileio.input_data_check(main_directory, input_data_folder, '.sam',
    #                         [junction_folder, blast_results_folder, blast_results_query])
    initialize_folders(main_directory)
    junctionf.junction_search(main_directory, junction_folder, input_data_folder, blast_results_folder,
                              junction_sequence, exclusion_sequence)
    # printio.print_comment("Comment3")
    junctionf.blast_search(main_directory, blast_db_name, blast_results_folder)
    junctionf.generate_tabulated_blast_results(main_directory, blast_results_folder, blast_results_query)
