#!/bin/bash

VOCSIZE=100
CORPUSPATH=/home/tiwe/t-chtian/dataClean/data/data.sort.txt.test
VOCPATH=./statistics/vocab.txt
BIGRAMPATH=./statistics/bigram.pkl
UNIGRAMPATH=./statistics/unigram.pkl
TRIGRAMPATH=./statistics/trigram.pkl

python vocab.py -iPath $CORPUSPATH -oPath $VOCPATH  -vocSize $VOCSIZE

python ngram.py -iPath $CORPUSPATH -vocPath $VOCPATH -uniGramPath $UNIGRAMPATH -biGramPath $BIGRAMPATH  -triGramPath $TRIGRAMPATH

python computePmi.py -iPath $CORPUSPATH -oPath data.withPmi.txt -vocPath $VOCPATH -uniGramPath $UNIGRAMPATH -biGramPath $BIGRAMPATH -triGramPath $TRIGRAMPATH

:<<!
sort -n data.withPmi.txt > data.withPmi.pmiSort.txt
#if [[ $? -eq 0 ]]; then 
#    rm data.withPmi.txt
#fi

cat data.withPmi.pmiSort.txt | awk -F "\t" -v OFS="\t" '{print $1, $5}' > comments.withPmi.txt

sort -t $'\t' -k2,2  comments.withPmi.txt > comments.withPmi.sort.txt
if [[ $? -eq 0 ]]; then 
    rm comments.withPmi.txt
fi

python averagePmi.py -iPath comments.withPmi.sort.txt -oPath comments.avrPmi.txt -cmFreqPath ../../data/comments.freq.sort.txt
if [[ $? -eq 0 ]]; then 
    rm comments.withPmi.sort.txt
fi

sort -n comments.avrPmi.txt > comments.avrPmi.sort.txt
if [[ $? -eq 0 ]]; then 
    rm comments.avrPmi.txt
fi

echo
echo finish.
!
