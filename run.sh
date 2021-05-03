#!/bin/bash


#scs=$1
#out=$2
#fn=$3
#bulk=$4

time=/usr/bin/time

declare -a sizes=(10 20 40 100)
declare -a fracs=(0 0.125 0.25 0.5)
rep=10

indata=sim2b

for s in ${sizes[@]}; do
        for f in ${fracs[@]}; do
                for i in $(seq 1 $rep); do
                        echo -e "On n=$s, $f ambiguous signal, rep $i"
                        path=/home/chengzes/Desktop/Classes/CS598MEB/data/$indata/SCS/n=$s/$f/rep$i.tsv
                        outdir=${indata}_output/n=$s/$f/rep$i
                        if [ ! -e $outdir ]; then
                                mkdir -p $outdir
                        fi
                        
                        # not violating ISA
                        { $time -v python PhISCS-I -SCFile $path \
                                -o $outdir -fn 0.000001 -fp 0.000001 \
                                --drawTree --threads 8 -p 1 ; } \
                                > $outdir/runtime.txt 2>&1

                done
        done
done

#if [[ $bulk == "" ]]; then
#        python PhISCS-I -SCFile $scs -o $out -fn $fn \
#                -fp 0.0001 --drawTree --threads 8
#else
#        python PhISCS-I -bulkFile $bulk -SCFile $scs -o $out \
#                -fn $fn -fp 0.0001 --drawTree --threads 8
#fi
