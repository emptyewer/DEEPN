import os
import sys
import glob
import cPickle
import functions.structures as sts

directory = 'blast_results_query'
if not os.path.exists(directory):
    print (">>> No blast results found. Exiting.")
    sys.exit()

filelist = glob.glob(directory + "/*.bqp")
print "\nBQP files"
print "----------\n"
for count, file in enumerate(filelist):
    print "%5s. %-50s" % (count, os.path.basename(file))
print "\n"

sel = raw_input(">>> Select a file: ")
filename = filelist[int(sel)]
output_filename = os.path.join(directory, os.path.splitext(os.path.basename(filename))[0] + "_library_quality.csv")
output_handle = open(output_filename, 'w')
output_handle.write("Gene_Name,NM_Number,In_Frame,Out_of_Frame,Downstream,In_ORF,Upstream,Backwards,In_ORF_Frame,Upstream_Inframe\n,,\n")
bqp = cPickle.load(open(filename, 'rb'))
for gene_name in bqp:
    if gene_name != 'total':
        output_handle.write("%s," % gene_name)
        first_line_nm = True
        for nm_number in bqp[gene_name].keys():
            stats = {'not_in_frame': 0,
                     'in_frame': 0,
                     'in_orf': 0,
                     'upstream': 0,
                     'downstream': 0,
                     'backwards': 0,
                     'orf_frame': 0,
                     'up_frame': 0
                     }
            if nm_number != 'stats':
                if first_line_nm:
                    output_handle.write("%s," % nm_number)
                    first_line_nm = False
                else:
                    output_handle.write(",%s," % nm_number)
                first_line_junction = True
                junctions_property = []
                for j in bqp[gene_name][nm_number]:
                    key = "%d-%d" % (j.position, j.query_start)
                    if key not in junctions_property:
                        stats[j.frame] += 1
                        stats[j.orf] += 1
                        if j.frame == 'in_frame' and j.orf == 'in_orf':
                            stats['orf_frame'] += 1
                        if j.frame =='in_frame' and j.orf == 'upstream':
                            stats['up_frame'] += 1
                        # if first_line_junction:
                        #     output_handle.write("%d, %d, %s, %s\n" % (j.position, j.query_start, j.frame, j.orf))
                        #     first_line_junction = False
                        # else:
                        #     output_handle.write(",,%d, %d, %s, %s\n" % (j.position, j.query_start, j.frame, j.orf))
                    else:
                        pass
                if first_line_junction:
                    output_handle.write("%d,%d,%d,%d,%d,%d,%d,%d\n" % (stats['not_in_frame'],
                                                               stats['in_frame'],
                                                               stats['downstream'],
                                                               stats['in_orf'],
                                                               stats['upstream'],
                                                               stats['backwards'],
                                                               stats['orf_frame'],
                                                               stats['up_frame']))
                    first_line_junction = False
                else:
                    output_handle.write(",,%d,%d,%d,%d,%d,%d,%d,%d\n" % (stats['not_in_frame'],
                                                                 stats['in_frame'],
                                                                 stats['downstream'],
                                                                 stats['in_orf'],
                                                                 stats['upstream'],
                                                                 stats['backwards'],
                                                                 stats['orf_frame'],
                                                                 stats['up_frame']))
        output_handle.write(",,\n")
output_handle.close()
