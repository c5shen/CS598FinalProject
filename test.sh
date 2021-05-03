#!/bin/bash


#scs=$1
#out=$2
#fn=$3
#bulk=$4

time=/usr/bin/time
path=test/input.tsv
p=$1
if [[ $p == "" ]]; then
        echo -e "p not set"
        exit
fi
outdir=test_output/p=$p
if [ ! -e $outdir ]; then
        mkdir -p $outdir
fi
python PhISCS-I -SCFile $path \
        -o $outdir -fn 0.000001 -fp 0.000001 \
        --drawTree -p $p --threads 8 
