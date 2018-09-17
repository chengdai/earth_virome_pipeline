cd ..

if [ ! -d ./tools ]; then
    mkdir ./tools/
fi

if [ ! -d ./assembled ]; then
    mkdir ./assembled/
fi

if [ ! -d ./annotated_contigs ]; then
    mkdir ./annotated_contigs/
fi

if [ ! -d ./filter_contigs ]; then
    mkdir ./filter_contigs/
fi

if [ ! -d ./cluster_contigs ]; then
    mkdir ./cluster_contigs/
fi

if [ ! -d ./low_abundance ]; then
    mkdir ./low_abundance/
fi


wget http://eddylab.org/software/hmmer/hmmer-3.2.1.tar.gz -P ./tools/
cd tools
tar -xzvf hmmer-3.2.1.tar.gz
rm hmmer-3.2.1.tar.gz
cd hmmer-3.2.1/
./configure; make; sudo make install
cd ..

git clone https://github.com/hyattpd/Prodigal.git
cd Prodigal
make; sudo make install
cd ..

git clone https://github.com/lh3/seqtk.git
cd seqtk; make
sudo make install
cd ..

git clone https://github.com/voutcn/megahit.git
cd megahit
make
cd ..

wget ftp://ftp.ncbi.nlm.nih.gov/blast/executables/blast+/LATEST/ncbi-blast-2.7.1+-src.tar.gz
tar -xzvf ncbi-blast-2.7.1+-src.tar.gz
cd ncbi-blast-2.7.1+-src/c++/
./configure
make
sudo make install
cd ../../
