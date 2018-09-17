from Bio import SearchIO
import pandas, argparse, subprocess

def get_hits_to_VPFs(hmmout_file):
    '''Takes a HMMER3 hmmsearch tab output file as an input and 
    returns a dictionary mapping each scaffold with the number of unique genes that match a protein family
    
    Input:
        - hmmout_file (str): path to HMMER3 hmmsearch out file in tab format
    
    Returns:
        - hots_to_VPFs (dict): dictionary where key are scaffold IDs and values are number of unique genes that matched a protein family
    '''
    hits_to_VPFs = {}
    with open(hmmout_file, 'rU') as input:
        for qresult in SearchIO.parse(input, 'hmmer3-tab'):
            hits = qresult.hits
            num_hits = len(hits)
            if num_hits > 0:
                for i in range(0,num_hits): 
                    query_seq_id = hits[i].id
                    scaffold, gene = query_seq_id.split('|')
                    hits_to_VPFs[scaffold] = hits_to_VPFs.get(scaffold, set([])).union([gene])

    for key, value in hits_to_VPFs.iteritems():
        hits_to_VPFs[key] = len(value)
    return hits_to_VPFs

def get_num_of_genes(fasta_file):
    '''Takes a FASTA file as an input where each FASTA header is defined as: Scaffold_ID|Gene_ID
    and returns a dictionary mapping each scaffold with the number of unique genes in that scaffold
    
    Input:
        - fasta_file (str): path to fasta file in which headers are formatted Scaffold_ID|Gene_ID
    
    Returns:
        - gene_count (dict): dictionary where key are scaffold IDs and values are number of unique genes that are part of the scaffold
        - gene_scaffold_map (dict): dictionary that maps each gene ID back to its respective scaffold ID
    '''

    gene_count = {}
    gene_scaffold_map = {}
    with open(fasta_file) as fasta:
        for line in fasta:
            if line[0] == '>':
                scaffold, gene = line[1:].strip().split('|')
                gene_count[scaffold] = gene_count.get(scaffold, set([])).union([gene])
                gene_scaffold_map[gene] = scaffold
    for key, value in gene_count.iteritems():
        gene_count[key] = len(value)
    return gene_count, gene_scaffold_map

def get_pfam_genes(pfam_file, gene_scaffold_map):
    '''Takes a pfam file as an input and returns a dictionary mapping each scaffold with the number of unique genes that matched a pfam gene
    
    Input:
        - pfam_file (str): path to pfam out file
    
    Returns:
        - scaffold_pfam_count (dict): dictionary where key are scaffold IDs and values are number of pfam genes for the scaffold
    '''
    
    pfam = pandas.read_table(pfam_file)
    scaffold_pfam_count = {}
    for gene in pfam['GeneID'].values:
        if gene_scaffold_map.get(gene, None) != None:
            scaffold_pfam_count[gene_scaffold_map[gene]] = scaffold_pfam_count.get(gene_scaffold_map[gene], 0) + 1
    return scaffold_pfam_count

def write_master_table(master_table_file, VPF_hits, num_gene, pfam_gene_count):
    with open(master_table_file, 'w') as master:
        master.write('\t'.join(['Scaffold_ID', 'hits_to_VPFs', '#_of_genes', '%covered_VPFs', 'genes_with_pfams', '%genesPfams']) + '\n')
        for scaffold in VPF_hits.keys():
            out = []
            out.append(scaffold)
            out.append(VPF_hits.get(scaffold, 0))
            out.append(num_gene.get(scaffold, 0))
            out.append(VPF_hits.get(scaffold, 0) * 100.0 / float(num_gene.get(scaffold, 0)))
            out.append(pfam_gene_count.get(scaffold, 0))
            out.append(pfam_gene_count.get(scaffold, 0) * 100.0 / float(num_gene.get(scaffold, 0)))
            master.write('\t'.join([str(col) for col in out]) + '\n')
    return master_table_file

def filter_and_extract_sequences(out_folder, master_table, gene_fasta_file, assembly_fasta_file):
    '''Takes a master table as an input and filters sequences, keeping only those that are inferred as viral'''
    filter1 = out_folder + 'Filter1.out'
    filter2 = out_folder + 'Filter2.out'
    filter3 = out_folder + 'Filter3.out'
    out_filtered_contigs = out_folder + gene_fasta_file.split('/')[-1].split('genes')[0] + 'filtered_viral_contigs.txt'
    out_filtered_contigs_fa = out_folder + gene_fasta_file.split('/')[-1].split('genes')[0] + 'filtered_viral_contigs.fa'
    
    filter_command_1 = "cat {0} | awk '$2 >= 5' | awk '$6 <= 40' | awk '$4 >= 10' | cut -f 1 > {1}".format(master_table, filter1)
    filter_command_2 = "cat {0} | awk '$2 >= 5' | awk '$2 >= $5' | cut -f 1 > {1}".format(master_table, filter2)
    filter_command_3 = "cat {0} | awk '$2 >= 5' | awk '$4 >= 60' | cut -f 1 > {1}".format(master_table, filter3)
    merge_command = "cat {0} {1} {2} | sort | uniq > {3}".format(filter1, filter2, filter3, out_filtered_contigs)
    extract_command = "seqtk subseq {0} {1} > {2}".format(assembly_fasta_file, out_filtered_contigs, out_filtered_contigs_fa)
    
    final_command = " && ".join([filter_command_1, filter_command_2, filter_command_3, merge_command, extract_command])
    send = subprocess.Popen(final_command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=True)
    (stdout, stderr) = send.communicate()
    print stdout
    print stderr
    
    return out_filtered_contigs_fa
    

def main():    
    parser = argparse.ArgumentParser(description='Specify arguments for building a master table and filtering contigs.')
    parser.add_argument('--hmmout_file',
                        help='path to hmmsearch tab output')
    parser.add_argument('--genes_fasta',
                        help='path to FASTA file containing Scaffold ID and Gene ID')
    parser.add_argument('--assembly_fasta',
                        help='path to assembly FASTA file containing contigs > 5kb')
    parser.add_argument('--pfam_file',
                        help='path to pfam output file in data frame form')
    parser.add_argument('--out_folder', default = '../filter_contigs/',
                        help='name for output folder (Default: ../filter_contigs/)')
    args = parser.parse_args()
    
    hmmout_file = args.hmmout_file
    gene_fasta_file = args.genes_fasta
    pfam_file = args.pfam_file
    output_folder = args.out_folder
    master_table_file = output_folder + hmmout_file.split('/')[-1].split('_hits_to_vHMMs')[0] + '_master_table.txt'
    assembly_fasta = args.assembly_fasta
    
    VPF_hits = get_hits_to_VPFs(hmmout_file)
    num_gene, gene2scaffold = get_num_of_genes(gene_fasta_file)
    pfam_gene_count = get_pfam_genes(pfam_file, gene2scaffold)    
    
    write_master_table(master_table_file, VPF_hits, num_gene, pfam_gene_count)
    print 'Final master table can be found at: {0}'.format(master_table_file)
    
    viral_contigs = filter_and_extract_sequences(output_folder, master_table_file, gene_fasta_file, assembly_fasta)
    print 'Final list of viral contigs can be found at: {0}'.format(viral_contigs)
    
main()
