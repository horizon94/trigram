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
print '\n\nVOCAB COUNT.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='vocabulary file output path.')
args.add_argument('-vocSize', type=int, dest='vocSize', help='the max size of the vocab.')
args.add_argument('-debug', type=int, dest='debug', help='run as debugging.')
args.add_argument('-debug_num', type=int, dest='debug_num', help='corpus lines num when debugging.')
args.add_argument('-com_num_cut', type=int, dest='com_num_cut', help='filter out those titles whose comment num less than this.')
args = args.parse_args()

unkWord = '<unk>'
w2f = {}
titlCnt = 0
commCnt = 0

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
            titlCnt += 1
            commCnt += len(nowComs)
        if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
            for sent in [nowTitl]+nowComs:
                updVocBsSent(sent)        
        nowTitl = titl
        nowComs = [comm]
    idx += 1
    if 0 == idx % 10000:
        sys.stdout.write('%dw lines processed\r' % (idx/10000))
        sys.stdout.flush()
    if 1 == args.debug and idx > args.debug_num: break # debug
if not '' == nowTitl:
    titlCnt += 1
    commCnt += len(nowComs)
if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
    for sent in [nowTitl]+nowComs:
        updVocBsSent(sent)        

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

'''
### sentence head/tail word
vocFile.write('%s\t%d\n' % ('<s1>', 0))
vocFile.write('%s\t%d\n' % ('<s2>', 0))
vocFile.write('%s\t%d\n' % ('</tail>', 0))
'''

#### about this corpus
if 1 == args.debug:
    print('title num: %d' % titlCnt)
    print('average comment num per title: %.2f' % (float(commCnt) / titlCnt))

vocFile.close()
iFile.close()
print('output %d words including <unk>.' % (min(args.vocSize, len(w2fLs)+1)))

