# Earth Virome Pipeline - Documentation

#### Original paper (please cite if used): 
Paez-Espino *et al.* (2017). *Nature Protocol*. https://doi.org/10.1038/nprot.2017.063

#### Adapted pipeline code and documentation by: 

Chengzhen Dai (chengdai@mit.edu), Sepideh Pakpour (sepideh.pakpour@ubc.ca)

---

### Getting Started

This pipeline consists a set of command-line scripts provided for Linux and written in Python (2.7) and Java. To use, simply clone the repository:
```
git clone https://github.com/chengdai/earth-virome-pipeline.git
```

#### Software Requirements
The pipeline requires a set of dependency softwares:
- **[MEGAHIT](https://github.com/voutcn/megahit)**: For fast, high-quality metagenomic assembly from raw reads
- **[Prodigal](https://github.com/hyattpd/Prodigal)**: For predicting protein-coding genes in genomes.
- **[HMMER 3.2](http://hmmer.org/)**: For detection of protein families based off of a reference HMM model
- **[blastn](https://blast.ncbi.nlm.nih.gov/Blast.cgi?CMD=Web&PAGE_TYPE=BlastDocs&DOC_TYPE=Download)**: For detection of homologs in reads based on reference genomes
- **[seqtk](https://github.com/lh3/seqtk)**: For filtering fastq/fasta files

To install all of the required softwares, please first ensure you have **sudo** permission and then run:

```
cd src/
bash download_dependencies.sh
cd ..
```

#### Database Requirements
The pipeline also requires a set of reference database:
- **[Viral protein families](http://portal.nersc.gov/dna/microbial/prokpubs/EarthVirome_DP/final_list.hmms)**: HMM model consisting of 25,281 viral proteins, from ref. 20 of Paez-Espino et al. 2017 (Nature Protocol)
- **[Metagenomic viral contigs](http://portal.nersc.gov/dna/microbial/prokpubs/EarthVirome_DP/Nature_Protocols/reference_metagenomic_virus_database/mVCs_PaezEspino_Nature.fna)**: A reference database consisting of 125,842 metagenomic viral contigs (fasta file to be converted to a blast database).
- **[Pfam](large collection of protein families)**: A large collection of protein families

To install all of the required databases, please run:

```
cd src/
bash get_reference_files.sh
cd ..
```

---
### Running the Pipeline

All of the scripts should be run from the __src__ folder

#### --- Step 1. Genome Assembly with MEGAHIT ---

To begin, we start with a pair of forward and reverse reads from a metagenomic sample. Here, we run: **assemble_reads.py**. The arguments are:

```
usage: assemble_reads.py [-h] [--megahit MEGAHIT] [--read_1 READ_1]
                         [--read_2 READ_2] [--out_folder OUT_FOLDER]

Specify arguments for MEGAHIT assembly

optional arguments:
  -h, --help            show this help message and exit
  --megahit MEGAHIT     path to megahit tool
  --read_1 READ_1       path to forward reads (raw, unassembled reads)
  --read_2 READ_2       path to backwards reads (raw, unassembled reads)
  --out_folder OUT_FOLDER
                        path to output folder (Default: ../assembled/)
```

Note that the default output folder is the **assembled** folder in the parent folder. The output will be named similar to: **final.contigs.fa** (It is recommended that you rename the file to be something more specific to the sample.)


An example use of this script is:

```
python assemble_reads.py \
    --megahit ../tools/megahit \
    --read_1 ../example_reads/example_1.fastq \
    --read_2 ../example_reads/example_2.fastq \
    --out_folder ../assembled/
```

#### --- Step 2. Filter and Annotate Assembled Contigs ---

We first filter the assembly results, keeping only contigs of length 5+ kb. Then, we use **prodigal** to predict potential proteins and use **Pfam** to identify homologs of protein families in the predicted proteins. Note that this step in the original paper is done by the [IMG/M System](https://img.jgi.doe.gov/m/doc/MGAandDI_SOP.pdf), which is an online system that requires manual uploading/downloading. Here, we use the offline method as implemented in the script: **annotate_assembled_contigs.py**. The arguments are:

```
usage: annotate_assembled_contigs.py [-h]
                                     [--assembled_contigs ASSEMBLED_CONTIGS]
                                     [--pfam_db PFAM_DB]
                                     [--viral_hmm VIRAL_HMM]
                                     [--out_folder OUT_FOLDER]

Specify arguments for predicting genes with prodigal and finding protein
families using Pfam.

optional arguments:
  -h, --help            show this help message and exit
  --assembled_contigs ASSEMBLED_CONTIGS
                        path to fasta file containing the filtered contigs of
                        length 5kb or more
  --pfam_db PFAM_DB     path to Pfam-A.hmm file
  --viral_hmm VIRAL_HMM
                        path to viral_reference_model.hmm file
  --out_folder OUT_FOLDER
                        path to output folder (Default: ../annotated_contigs/)
```

Note that the default output folder is the **annotated_contigs** folder in the parent folder. The exact path of the output files will be printed in the terminal.

An example use of this script is:

```
python annotate_assembled_contigs.py \
    --assembled_contigs ../assembled/example/example_contigs.fa \
    --pfam_db ../reference_files/Pfam-A.hmm \
    --viral_hmm ../reference_files/viral_reference_model.hmm \
    --out_folder ../annotated_contigs/
```

#### --- Step 3. Build Master Table and Filter Contigs ---

We first create a master table and filter out sequences with hits to viral proteins. Next, we apply a set of filters to extract viral contigs from metagenomic tables. Here, we run: **filter_viral_contigs_master_table.py**. The arguments are:
```
usage: filter_viral_contigs_master_table.py [-h] [--hmmout_file HMMOUT_FILE]
                                            [--genes_fasta GENES_FASTA]
                                            [--assembly_fasta ASSEMBLY_FASTA]
                                            [--pfam_file PFAM_FILE]
                                            [--out_folder OUT_FOLDER]

Specify arguments for building a master table and filtering contigs.

optional arguments:
  -h, --help            show this help message and exit
  --hmmout_file HMMOUT_FILE
                        path to hmmsearch tab output
  --genes_fasta GENES_FASTA
                        path to FASTA file containing Scaffold ID and Gene ID
  --assembly_fasta ASSEMBLY_FASTA
                        path to assembly FASTA file containing contigs > 5kb
  --pfam_file PFAM_FILE
                        path to pfam output file in data frame form
  --out_folder OUT_FOLDER
                        name for output folder (Default: ../filter_contigs/)
```

Note that the default output folder is the **filter_contigs** folder in the parent folder. The exact path of the output files will be printed in the terminal.

An example use of this script is:
```
python build_master_table.py \
    --hmmout_file ../annotated_contigs/example_contigs_5kb_genes_in_scafs_formatted_hits_to_vHMMs.hmmout \
    --genes_fasta ../annotated_contigs/example_contigs_5kb_genes_in_scafs_formatted.fa \
    --assembly_fasta ../assembled/example/example_contigs.fa \
    --pfam ../annotated_contigs/example_contigs_5kb_genes_in_scafs.pfam.txt \
    --out ../filter_contigs/
```

#### --- Step 4. Viral Genome Clustering ---

Here, we group viruses detected in public metagenomes with viral contigs from our specific sample. This step involves 1) a blastn operation to identify homolog hits against a metagenomic viral contigs database; 2) removal of self-hits; 3) parsing of the outputs to keep only those that meet a specific cutoff; and 4) single linkage clustering. Here, we run: **viral_contig_clustering.py**. The arguments are:

```
usage: viral_contig_clustering.py [-h] [--viral_contigs VIRAL_CONTIGS]
                                  [--ref_db REF_DB] [--out_folder OUT_FOLDER]

Specify arguments for clustering contigs.

optional arguments:
  -h, --help            show this help message and exit
  --viral_contigs VIRAL_CONTIGS
                        path to fasta file containing the filtered viral
                        contigs from the HMM search
  --ref_db REF_DB       path including the prefix of viral contig db (must be
                        indexed using makeblastdb)
  --out_folder OUT_FOLDER
                        path to output folder (Default: ../cluster_contigs/)
```

Note that the default output folder is the **cluster_contigs** folder in the parent folder. The exact path of the output files will be printed in the terminal.

An example use of this script is:
```
python viral_contig_clustering.py \
    --viral_contigs ../filter_contigs/example_contigs_filtered_viral_contigs.fa \
    --ref_db ../reference_files/mVCs_PaezEspino_Nature.fna \
    --out_folder ../cluster_contigs/
```

#### --- Step 5. Hinting at Viruses with Low Abundance ---
In parallel to assemblying and filtering for viral contigs, we also use blastn to hint at viruses with low abundance and filter for viral sequences with at least 10% of their length covered by unassembled reads. Here, we run: **detect_low_abundant_virus.py**. The arguments are:
```
usage: detect_low_abundant_virus.py [-h]
                                    [--unassembled_reads UNASSEMBLED_READS]
                                    [--ref_db REF_DB]
                                    [--out_folder OUT_FOLDER]

Specify arguments for hinting at the presence of viruses with low abundance.

optional arguments:
  -h, --help            show this help message and exit
  --unassembled_reads UNASSEMBLED_READS
                        path to fasta file containing the unassembled raw
                        reads
  --ref_db REF_DB       path including the prefix of viral contig db (must be
                        indexed using makeblastdb)
  --out_folder OUT_FOLDER
                        path to output folder (Default: ../low_abundance/)
```

Note that the default output folder is the **low_abundance** folder in the parent folder. The exact path of the output files will be printed in the terminal.

An example use of this script is:
```
python detect_low_abundant_virus.py \
    --unassembled_reads ../example_reads/example_1.fastq \
    --ref_db ../reference_files/mVCs_PaezEspino_Nature.fna \
    --out_folder ../low_abundance/
```

Note: this step does not take into consideration pair-end reads so each read (forward or reverse) must be processed separately

---

### Questions? 
For questions regarding this code and implementation, please contact Cheng (chengdai@mit.edu). For methodology specific questions, please consider contacting David Paez-Espino (author of the original paper).
