#coding=utf-8
'''
Extract vocabulary from a corpus.
Output the first N words and their frequency.
Other words are seen as unkown word as <unk>.
'''

import sys
import argparse


# functions
def updVocBsSent(sent):
    ws = sent.split()
    for w in ws:
        if w in w2f:
            w2f[w] += 1
        else:
            w2f[w] = 1

def w2fSortKey(elem):
    return elem[1]

# main
print '\nVOCAB COUNT.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='vocabulary file output path.')
args.add_argument('-vocSize', type=int, dest='vocSize', help='the max size of the vocab.')
args = args.parse_args()

#iPath = '/home/tiwe/t-chtian/dataClean/data/data.sort.txt'
#vocSize = 400000
#vocPath = './statistics/vocab.txt'

unkWord = '<unk>'
w2f = {}

iFile = open(args.iPath, 'r')

## extract words and frequency
nowTitl = ''
nowComs = []
idx = 0
for line in iFile:
    [titl,comm] = line.strip().split('\t')
    if titl == nowTitl:
        nowComs.append(comm)
    else: # new title, 1) update vocab; 2) update struct.
        if not '' == nowTitl:
            for sent in [nowTitl]+nowComs:
                updVocBsSent(sent)        
        nowTitl = titl
        nowComs = [comm]
    idx += 1
    if 0 == idx % 10000:
        sys.stdout.write('%dw lines processed\r' % (idx/10000))
        sys.stdout.flush()
    #if idx > 100000: break # debug

## output the first N words
### trans to list and sort
print('got %d words total.' % len(w2f))
w2fLs =  [(k,w2f[k]) for k in w2f]
w2fLs.sort(key=w2fSortKey, reverse=True)
vocFile = open(args.oPath, 'w')
for w,f in w2fLs[:min(args.vocSize, len(w2fLs))]:
    vocFile.write('%s\t%d\n' % (w,f))

### unkown word
assert (unkWord not in w2f)
if args.vocSize >= len(w2fLs):
    vocFile.write('%s\t%d\n' % (unkWord, 0))
else:
    unkCnt = sum([ele[1] for ele in w2fLs[args.vocSize:]])
    unkNum = len(w2fLs) - args.vocSize
    vocFile.write('%s\t%d\n' % (unkWord, unkCnt/unkNum)) # use average frequency as <unk> frequency

vocFile.close()
iFile.close()
print('output %d words including <unk>.' % (min(args.vocSize, len(w2fLs)+1)))

