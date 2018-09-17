import pandas, subprocess, multiprocessing, argparse

def filter_contigs(assembled_contigs, out_folder = None):
    '''Calls a bash command to filter assembled contigs, keeping those greather than 5kb'''
    if out_folder == None:
        out_folder = '/'.join(filtered_contigs.split('/')[:-1]) + '/'
    elif out_folder[-1] != '/':
        out_folder = out_folder + '/'

    filtered_fasta = out_folder + assembled_contigs.split('/')[-1].split('.')[0] + '_5kb.fa'
    final_command = "awk 'BEGIN{RS=\">\"}{NR>1}{sub(\"\\n\",\"\\t\"); gsub(\"\\n\",\"\"); print RS$0}' " + assembled_contigs + "| awk '{if(length($2)>=5000) print}' | perl -p -e 's/\\t/\\n/g' | fold -w 60 > " + filtered_fasta

    print '(Step 1/5) Filtering assembled fasta to keep only those of at least length 5kb...'
    send = subprocess.Popen(final_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr
    print 'Done!\n'
    return filtered_fasta

def prodigal_pfam(filtered_contigs, pfam_db, out_folder = None):
    '''Calls prodigal on a filtered contig file to predict proteins and then runs hmmsearch on those predicted proteins'''
    if out_folder == None:
        out_folder = '/'.join(filtered_contigs.split('/')[:-1]) + '/'
    elif out_folder[-1] != '/':
        out_folder = out_folder + '/'
    
    prodigal_ORF_out = out_folder + filtered_contigs.split('/')[-1].split('.')[0] + '_genes_in_scafs.fa'
    pfam_out = out_folder + prodigal_ORF_out.split('/')[-1].split('.')[0] + '.pfam.hmmout'
    num_cpu = multiprocessing.cpu_count()
    final_command = "prodigal -i {0} -a {1} && hmmsearch --cpu {2} --cut_tc --domtblout {3} {4} {1}".format(filtered_contigs, prodigal_ORF_out, num_cpu, pfam_out, pfam_db)

    print '(Step 2/5) Finding predicted proteins using prodigals and annotating them...'
    send = subprocess.Popen(final_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr
    print 'Done! Prodigal and Pfam complete, output can be found at: {0} and {1}\n'.format(prodigal_ORF_out, pfam_out)
    return prodigal_ORF_out, pfam_out

def format_prodigal_out_headers(prodigal_out):
    '''Takes a prodigal predicted protein fasta file and renames the headers such that the format is ">CONTIG|GENE" 
    where CONTIG is the contig ID and GENE is the gene ID for a gene in the CONTIG'''
    reformatted_file = prodigal_out.split('.fa')[0] + '_formatted.fa'
    print '(Step 3/5) Refomatting prodigal out headers...'
    with open(prodigal_out) as prodigal:
        with open(reformatted_file, 'w') as formatted:
            for line in prodigal:
                if line[0] == '>':
                    gene = line[1:].split()[0]
                    contig = '_'.join(gene.split('_')[:-1])
                    formatted.write('>' + contig + '|' + gene + '\n')
                else:
                    formatted.write(line)
    print 'Done! Formatted prodigal output at: {0}\n'.format(reformatted_file)
    return reformatted_file

def parse_pfam_out(pfam_out):
    '''Takes in pfam_out file in domtblout format and returns a custom trimmed version as outlined in the Earth Virome pipeline'''
    print '(Step 4/5) Parsing Pfam output...'
    df = pandas.read_table(pfam_out, skiprows=[0,1,2], sep = '\s+', header = None).dropna()
    important_col = [0, 4, 21, 15, 16, 17, 18, 6, 7, 19, 20]
    out = df.iloc[:, important_col].copy()
    out.columns = ['GeneID', 'pfamID','%Identity','query_start','query_end','subject_start','subject_end','e-value','bit_score','align_start','align_end']
    out['Alignment_Length'] = out['align_end'] - out['align_start'] + 1
    out['%Identity'] = (out['%Identity']*100).apply(int)
    out = out.drop(columns=['align_start','align_end'])
    
    pfam_final = pfam_out.split('.hmmout')[0] + '.txt'
    out.to_csv(pfam_final, index = None, sep = '\t')
    print 'Done! Parsed Pfam out at: {0}\n'.format(pfam_final)
    return pfam_final

def calc_viral_family(prodigal_formatted, viral_hmm):
    hmm_out = prodigal_formatted.split('.fa')[0] + '_hits_to_vHMMs.hmmout'
    num_cpu = multiprocessing.cpu_count()
    
    final_command = 'hmmsearch --cpu {0} -E 1.0e-05 --tblout {1} {2} {3}'.format(num_cpu, hmm_out, viral_hmm, prodigal_formatted)
    print '(Step 5/5) Identifying viral proteins using hmmsearch...'
    send = subprocess.Popen(final_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stderr
    print 'Done! Hits to viral protein can be found at: {0}\n'.format(hmm_out)
    return hmm_out

    

def main():
    parser = argparse.ArgumentParser(description='Specify arguments for predicting genes with prodigal and finding protein families using Pfam.')
    parser.add_argument('--assembled_contigs',
                        help='path to fasta file containing the filtered contigs of length 5kb or more')
    parser.add_argument('--pfam_db',
                        help ='path to Pfam-A.hmm file')
    parser.add_argument('--viral_hmm',
                        help ='path to viral_reference_model.hmm file')
    parser.add_argument('--out_folder', default = '../annotated_contigs/',
                        help = 'path to output folder (Default: ../annotated_contigs/)')
    args = parser.parse_args()
    
    assembled_contigs = args.assembled_contigs
    pfam_db = args.pfam_db
    viral_hmm = args.viral_hmm
    out_folder = args.out_folder
    
    filtered_contigs = filter_contigs(assembled_contigs, out_folder = out_folder)
    prodigal_out, pfam_out = prodigal_pfam(filtered_contigs, pfam_db, out_folder = out_folder)
    prodigal_formatted_out = format_prodigal_out_headers(prodigal_out)
    pfam_final_out = parse_pfam_out(pfam_out)
    viral_hmm_out = calc_viral_family(prodigal_formatted_out, viral_hmm)
    print 'final predicted genes are at {0}, pfam annotations are at {1}, and viral hits are at {2}'.format(prodigal_formatted_out, pfam_final_out, viral_hmm_out)
    
main()

