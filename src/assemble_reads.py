import glob, argparse, subprocess, multiprocessing

def megahit_assembly(megahit, fastq_read_1, fastq_read_2, out_dir = None):
    if out_dir == None:
        out_dir = './'
    elif out_dir[-1] != '/':
        out_dir = out_dir + '/'
    
    print 'Assembling file: {0}'.format(fastq_read_1.split('/')[-1].split('_1')[0])
    out_folder = out_dir + fastq_read_1.split('/')[-1].split('_1')[0] + '/'

    command = '{0} -1 {1} -2 {2} -o {3} --kmin-1pass -m 0.75 --min-count 1 --presets meta-sensitive --min-contig-len 300 -t {4}'.format(megahit, fastq_read_1, fastq_read_2, out_folder, multiprocessing.cpu_count())
    print command
    print "Running MEGAHIT assembly on: {0} and {1}".format(fastq_read_1, fastq_read_2)
    final = subprocess.Popen(command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = final.communicate()
    print stdout, stderr
    
    print 'MEGAHIT assembly complete. Contigs can be found in {0}'.format(out_folder)

def main():
    parser = argparse.ArgumentParser(description='Specify arguments for MEGAHIT assembly')
    parser.add_argument('--megahit',
                        help ='path to megahit tool')
    parser.add_argument('--read_1',
                        help='path to forward reads (raw, unassembled reads)')
    parser.add_argument('--read_2',
                        help='path to backwards reads (raw, unassembled reads)')
    parser.add_argument('--out_folder', default = '../assembled/',
                        help = 'path to output folder (Default: ../assembled/)')
    args = parser.parse_args()
    
    megahit = args.megahit
    fastq_1 = args.read_1
    fastq_2 = args.read_2
    out_folder = args.out_folder

    megahit_assembly(megahit, fastq_1, fastq_2, out_folder)
    
main()
