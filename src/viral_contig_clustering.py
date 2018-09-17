import subprocess, glob, multiprocessing, argparse

def blastn(viral_contigs, reference_database, out_folder = None):
    if out_folder == None:
        out_folder = '/'.join(viral_contigs.split('/')[:-1]) + '/'
    elif out_folder[-1] != '/':
        out_folder = out_folder + '/'
    
    blastn_out = out_folder + viral_contigs.split('/')[-1].split('.')[0] + '_blastn_mVCs.blout'
    num_cpu = multiprocessing.cpu_count()
    blastn_command = "blastn -query {0} -db {1} -outfmt '6 std qlen slen' -out {2} -evalue 1.0e-50 -perc_identity 80 -num_threads {3}".format(viral_contigs, reference_database, blastn_out, num_cpu)

    print 'Performing blastn on viral contigs'
    send = subprocess.Popen(blastn_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr
    print 'blastn complete, output can be found at: {0}'.format(blastn_out)
    return blastn_out

def parse_cluster_blast(blastn_out, out_folder = None):
    if out_folder == None:
        out_folder = '/'.join(blastn_out.split('/')[:-1]) + '/'
    elif out_folder[-1] != '/':
        out_folder = out_folder + '/'
    
    # Remove self hits
    self_hits_out = out_folder + blastn_out.split('/')[-1].split('.')[0] + '_noSelfHits.blout'
    rm_self_hits = "cat {0} | awk '$1 != $2' > {1}".format(blastn_out, self_hits_out)
    
    # Parse unique BLAST results:
    parsed_out = out_folder + self_hits_out.split('/')[-1].split('.')[0] + '_parsed.blout'
    parse_blast = "java Parse_BLAST {0} > {1}".format(self_hits_out, parsed_out)
    
    # Single linkage clustering
    slc_out = out_folder + parsed_out.split('/')[-1].split('.')[0] + '.slc'
    slc = "perl SLC.pl {0} {1}".format(parsed_out, slc_out)
    
    merged_command = ' && '.join([rm_self_hits, parse_blast, slc])

    print 'Removing self hits, parsing blastn output and performing single linkage clustering'
    send = subprocess.Popen(rm_self_hits, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr

    print 'Operations complete! Output for single linkage clustering can be found at: {0}'.format(slc_out)
    return slc


def main():
    parser = argparse.ArgumentParser(description='Specify arguments for clustering contigs.')
    parser.add_argument('--viral_contigs',
                        help='path to fasta file containing the filtered viral contigs from the HMM search')
    parser.add_argument('--ref_db',
                        help ='path including the prefix of viral contig db (must be indexed using makeblastdb)')
    parser.add_argument('--out_folder', default = '../cluster_contigs/',
                        help = 'path to output folder (Default: ../cluster_contigs/)')
    args = parser.parse_args()
    
    viral_contigs = args.viral_contigs
    viral_contigs_db = args.ref_db
    out_folder = args.out_folder
    
    blast_out = blastn(viral_contigs, viral_contigs_db, out_folder)
    parse_cluster_blast(blast_out, out_folder)
    
main()
