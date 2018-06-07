#!/bin/bash

VOCSIZE=400000
#CORPUSPATH=/home/tiwe/t-chtian/dataClean/data/data.sort.txt
#CORPUSPATH=/home/tiwe/t-chtian/dataClean/data/scored/data.scrd.fltd.sort.txt
#CORPUSPATH=/home/tiwe/t-chtian/dataClean/data/gene_test/gene.test
CORPUSPATH=/home/tiwe/t-chtian/dataClean/data/gene_test/gene.test.lm
VOCPATH=./statistics/vocab.txt
TRIGRAMPATH=./statistics/trigram.pkl
DEBUG=0
DEBUG_NUM=10000
COMMENT_NUM_CUT=10
AVR_ABS=1
LAMDA=2.0

#time python vocab.py -iPath $CORPUSPATH -oPath $VOCPATH  -vocSize $VOCSIZE -debug $DEBUG -debug_num $DEBUG_NUM -com_num_cut $COMMENT_NUM_CUT
#time python ngram.py -iPath $CORPUSPATH -vocPath $VOCPATH -triGramPath $TRIGRAMPATH -debug $DEBUG -debug_num $DEBUG_NUM -com_num_cut $COMMENT_NUM_CUT 
#time python computePmi.py -iPath $CORPUSPATH -oPath data.withPmi.txt -vocPath $VOCPATH -triGramPath $TRIGRAMPATH -debug $DEBUG -debug_num $DEBUG_NUM -com_num_cut $COMMENT_NUM_CUT
time python computePmiUsLm.py -iPath $CORPUSPATH -oPath data.withPmi.txt -vocPath $VOCPATH -triGramPath $TRIGRAMPATH -debug $DEBUG -debug_num $DEBUG_NUM -lamda $LAMDA

sort -t $'\t' -k4,4 -k1n,1 data.withPmi.txt > data.withPmi.titlGrouped.txt

sort -n data.withPmi.txt > data.withPmi.pmiSort.txt
if [[ $? -eq 0 ]]; then 
    rm data.withPmi.txt
fi

cat data.withPmi.pmiSort.txt | awk -F "\t" -v OFS="\t" '{print $1, $5}' > comments.withPmi.txt

sort -t $'\t' -k2,2  comments.withPmi.txt > comments.withPmi.sort.txt
if [[ $? -eq 0 ]]; then 
    rm comments.withPmi.txt
fi

python averagePmi.py -iPath comments.withPmi.sort.txt -oPath comments.avrPmi.txt -abs $AVR_ABS
if [[ $? -eq 0 ]]; then 
    rm comments.withPmi.sort.txt
fi

sort -n comments.avrPmi.txt > comments.avrPmi.sort.txt
if [[ $? -eq 0 ]]; then 
    rm comments.avrPmi.txt
fi

echo
echo finish.
