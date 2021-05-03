#!/bin/bash


#scs=$1
#out=$2
#fn=$3
#bulk=$4

time=/usr/bin/time

declare -a sizes=(10 20 40 100)
declare -a fracs=(0 0.125 0.25 0.5)
declare -a fns=(0 0.2 0.4)
rep=6
indata=isa_violations

for s in ${sizes[@]}; do
        for f in ${fracs[@]}; do
                for fn in ${fns[@]}; do
                        for i in $(seq 1 $rep); do
                                echo -e "On n=$s, $f ambiguous signal, fn=$fn, rep $i"
                                path=/home/chengzes/Desktop/Classes/CS598MEB/CS598FinalProject/$indata/SCS/n=$s/b=$fn/$f/rep$i.tsv
                                outdir=${indata}_output/n=$s/b=$fn/$f/rep$i
                                if [ ! -e $outdir ]; then
                                        mkdir -p $outdir
                                fi
                                
                                gfn=$(bc <<< "$fn + 0.000001")
                                # data violating ISA
                                { $time -v python PhISCS-I -SCFile $path \
                                        -o $outdir -fn $gfn -fp 0.000001 \
                                        --drawTree --threads 8 -p 1 ; } \
                                        > $outdir/runtime.txt 2>&1
                        done
                done
        done
done
