### Pull reference files before starting ###
# 1. Generate folder to store all reference files
cd ..
if [! -d ./reference_files]; then
    mkdir ./reference_files
fi

# 2.1 pull viral HMM model from ref. 20 of Paez-Espino et al. 2017 (Nature Protocol);
# 2.2 rename as viral_reference_model.hmms
wget http://portal.nersc.gov/dna/microbial/prokpubs/EarthVirome_DP/final_list.hmms \
-P ./reference_files/
cd ./reference_files
mv final_list.hmms viral_reference_model.hmm
cd ..

# 3 Get metagenomic viral contigs BLAST database
wget http://portal.nersc.gov/dna/microbial/prokpubs/EarthVirome_DP/Nature_Protocols/reference_metagenomic_virus_database/mVCs_PaezEspino_Nature.fna \
-P ./reference_files/
makeblastdb -in ./reference_files/mVCs_PaezEspino_Nature.fna -dbtype nucl

# 4 Get Pfam HMM model
wget ftp://ftp.ebi.ac.uk/pub/databases/Pfam/current_release/Pfam-A.hmm.gz -P ./reference_files/
gunzip ./reference_files/Pfam-A.hmm.gz

cd src
