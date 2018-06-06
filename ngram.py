#coding=utf-8

'''
'''

import sys
import pickle
import argparse

# functions
def word2id(word):
    if word in w2id:
        return w2id[word]
    else:
        return w2id[unkWord]

def updGramBsSent(sent):
    ws = sent.split()
    assert 0 < len(ws)
    #global biGramFrqSum
    #biGramFrqSum += len(ws)-1
    wids = [word2id(w) for w in ws]
    for i in range(len(ws)-1):
        wlid = wids[i]
        wrid = wids[i+1]
        ug2f[wlid] += 1 # update uni-gram
        bgKey = (wlid, wrid) # update bi-gram
        if bgKey in bg2f:
            bg2f[bgKey] += 1
        else:
            bg2f[bgKey] = 1

        if i<= len(ws)-3: # update tri-gram
            tgKey = (wlid, wrid, wids[i+2])
            if tgKey in tg2f:
                tg2f[tgKey] += 1
            else:
                tg2f[tgKey] = 1
            

# main
print '\nN-GRAM.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-vocPath', type=str, dest='vocPath', help='vocabulary file path.')
args.add_argument('-biGramPath', type=str, dest='biGramPath', help='bi-gram dump path.')
args.add_argument('-uniGramPath', type=str, dest='uniGramPath', help='uni-gram dump path.')
args.add_argument('-triGramPath', type=str, dest='triGramPath', help='tri-gram dump path.')
args = args.parse_args()

#crpPath = '/home/tiwe/t-chtian/dataClean/data/data.sort.txt'
#vocPath = './statistics/vocab.txt'
#biGramPath = './statistics/bigram.pkl'
#uniGramPath = './statistics/unigram.pkl'
w2id = {} # id start from 0
id2w = {}
ug2f = {} # unigram, as the form of (wid: freq)
bg2f = {} # bigram,  as the form of ((w1id, w2id): freq)
tg2f = {}
unkWord = '<unk>'

## load vocabulary
vocFile = open(args.vocPath, 'r')
idx = 0
for line in vocFile:
    w,_ = line.strip().split('\t')
    w2id[w] = idx
    id2w[idx] = w
    idx += 1

## statistic uni-gram and bi-gram
### initialize bi-gram
ug2f = {idx:0 for idx in id2w}

### statistic uni-gram and bi-gram
crpFile = open(args.iPath, 'r')
nowTitl = ''
nowComs = []
idx = 0
for line in crpFile:
    [titl, comm] = line.strip().split('\t')
    if titl == nowTitl:
        nowComs.append(comm)
    else: # new title, 1) update uni-gram and bi-gram; 2) update struct.
        if not '' == nowTitl:
            for sent in [nowTitl]+nowComs:
                updGramBsSent(sent)
        nowTitl = titl
        nowComs = [comm]
    idx += 1
    if 0 == idx % 10000:
        sys.stdout.write('%dw lines processed\r' % (idx/10000))
        sys.stdout.flush()
    #if idx > 100000: break # debug

crpFile.close()

## dump to disk
uniGramFile = open(args.uniGramPath, 'w')
pickle.dump(ug2f, uniGramFile)
uniGramFile.close()
print 'unigram dumped.'
biGramFile = open(args.biGramPath, 'w')
pickle.dump(bg2f, biGramFile)
biGramFile.close()
print 'bigram dumped.'
triGramFile = open(args.triGramPath, 'w')
pickle.dump(tg2f, triGramFile)
triGramFile.close()
print 'trigram dumped.'

## debug print
'''
print 'uni-gram examples:'
idx = 0
for ug in ug2f:
    print('%d : %d' % (ug, ug2f[ug]))
    idx += 1
    if idx > 10: break
idx = 0
for bg in bg2f:
    print('(%d,%d) : %d' % (bg[0], bg[1], bg2f[bg]))
    idx += 1
    if idx > 10: break
'''
