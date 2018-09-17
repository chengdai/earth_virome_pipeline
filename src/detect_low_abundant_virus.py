import subprocess, glob, multiprocessing, argparse

def blastn(unassembled_reads, reference_database, out_folder = None):
    if out_folder == None:
        out_folder = '/'.join(unassembled_reads.split('/')[:-1]) + '/'
    elif out_folder[-1] != '/':
        out_folder = out_folder + '/'

    blastn_out = out_folder + unassembled_reads.split('/')[-1].split('.')[0] + '_vs_mVCs.blout'
    num_cpu = multiprocessing.cpu_count()
    blastn_command = "blastn -task megablast -query {0} -db {1} -outfmt '6 std qlen slen' -out {2} -evalue 1.0e-50 -perc_identity 90 -num_threads {3}".format(unassembled_reads, reference_database, blastn_out, num_cpu)

    print 'Performing blastn on unassembled reads to capture low abundance virus'
    #send = subprocess.Popen(blastn_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    #(stdout, stderr) = send.communicate()
    #print stderr
    print 'blastn complete, output can be found at: {0}'.format(blastn_out)
    return blastn_out

def parse_blast(blastn_out):
    parsed_out = blastn_out + '.10percent.txt'
    
    parse_command = "java Coverage_VIRUSES_10Percent {0}".format(blastn_out)

    print "Parsing BLAST output"
    send = subprocess.Popen(parse_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr
    return parsed_out

def main():
    parser = argparse.ArgumentParser(description='Specify arguments for hinting at the presence of viruses with low abundance.')
    parser.add_argument('--unassembled_reads',
                        help='path to fasta file containing the unassembled raw reads')
    parser.add_argument('--ref_db',
                        help ='path including the prefix of viral contig db (must be indexed using makeblastdb)')
    parser.add_argument('--out_folder', default = "../low_abundance/",
                        help = 'path to output folder (Default: ../low_abundance/)')
    args = parser.parse_args()

    unassembled_reads = args.unassembled_reads
    virus_reference_database = args.ref_db
    out_folder = args.out_folder

    blast_out = blastn(unassembled_reads, virus_reference_database, out_folder = out_folder)
    parse_out = parse_blast(blast_out)
    print "parsed output of detected low abundant virus are at: {0}".format(parse_out)

main()
