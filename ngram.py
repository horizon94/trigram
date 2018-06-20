#coding=utf-8

'''
'''

import sys
import cPickle as pickle
import argparse

# functions
def word2id(word):
    if word in w2id:
        return w2id[word]
    else:
        return w2id[unkWord]

def updGramBsSent(sent):
    sent = sntHead + sent + sntTail
    ws = sent.split()
    wids = [word2id(w) for w in ws]
    for i in range(len(ws)-3):
        bgKey = (wids[i], wids[i+1])
        tgKey = (wids[i], wids[i+1], wids[i+2])
        if bgKey in bg2f:
            bg2f[bgKey] += 1.0
            if tgKey in tg2f: tg2f[tgKey] += 1.0
            else: tg2f[tgKey] = 1.0
        else:
            bg2f[bgKey] = 1.0
            tg2f[tgKey] = 1.0
    
        # static unk combination
        if w2id[unkWord] in bgKey:
            wsCmbBg = (ws[i], ws[i+1])
            if bgKey in unkCmb2NumBg:
                if not wsCmbBg in unkCmb2NumBg[bgKey]: 
                    unkCmb2NumBg[bgKey].add(wsCmbBg)
            else:
                tpSet1 = set()
                tpSet1.add(wsCmbBg)
                unkCmb2NumBg[bgKey] = tpSet1
        if w2id[unkWord] in tgKey:
            wsCmbTg = (ws[i], ws[i+1], ws[i+2])
            if tgKey in unkCmb2NumTg:
                if not wsCmbTg in unkCmb2NumTg[tgKey]: unkCmb2NumTg[tgKey].add(wsCmbTg)
            else:
                tpSet2 = set()
                tpSet2.add(wsCmbTg)
                unkCmb2NumTg[tgKey] = tpSet2
               
            
# main
print '\n\nN-GRAM.'
## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-vocPath', type=str, dest='vocPath', help='vocabulary file path.')
args.add_argument('-triGramPath', type=str, dest='triGramPath', help='tri-gram dump path.')
args.add_argument('-debug', type=int, dest='debug', help='run as debugging.')
args.add_argument('-debug_num', type=int, dest='debug_num', help='corpus lines num when debugging.')
args.add_argument('-com_num_cut', type=int, dest='com_num_cut', help='filter out those titles whose comment num less than this.')
args = args.parse_args()

w2id = {} # id start from 0
bg2f = {} # bigram,  as the form of ((w1id, w2id): freq)
tg2f = {}
unkCmb2NumTg = {}
unkCmb2NumBg = {}
unkWord = '<unk>'
frtWord = '<s1>'
scdWord = '<s2>'
lstWord = '</tail>'
sntHead = frtWord + ' ' + scdWord + ' '
sntTail =  ' ' + lstWord

## load vocabulary
vocFile = open(args.vocPath, 'r')
idx = 0
for line in vocFile:
    w,_ = line.strip().split('\t')
    w2id[w] = idx
    idx += 1
helpWords = [frtWord, scdWord, lstWord]
for w in helpWords:
    w2id[w] = idx
    idx += 1

## statistic uni-gram and bi-gram
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
        if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
            for sent in [nowTitl]+nowComs:
                updGramBsSent(sent)
        nowTitl = titl
        nowComs = [comm]
    idx += 1
    if 0 == idx % 10000:
        sys.stdout.write('%dw lines processed\r' % (idx/10000))
        sys.stdout.flush()
    if 1 == args.debug and idx > args.debug_num: break # debug
if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
    for sent in [nowTitl]+nowComs:
        updGramBsSent(sent)
print
crpFile.close()
### average unk combination
for tgK in unkCmb2NumTg:
    tg2f[tgK] = float(tg2f[tgK]) / len(unkCmb2NumTg[tgK])
print 'tg2f averaged.'
for bgK in unkCmb2NumBg:
    bg2f[bgK] = float(bg2f[bgK]) / len(unkCmb2NumBg[bgK])
print 'bg2f averaged.'


## dump to disk
triGramFile = open(args.triGramPath, 'wb')
pickle.dump((bg2f, tg2f), triGramFile, pickle.HIGHEST_PROTOCOL)
triGramFile.close()
print 'trigram dumped.'

## debug print
if 1 == args.debug:
    print 'uni-gram examples:'
    idx = 0
    for tg in tg2f:
        if w2id[unkWord] in tg:
            print('(%d,%d,%d) : %f' % (tg[0],tg[1],tg[2], tg2f[tg]))
        idx += 1
        if idx > 100: break
    idx = 0
    for bg in bg2f:
        if w2id[unkWord] in bg:
            print('(%d,%d) : %f' % (bg[0], bg[1], bg2f[bg]))
        idx += 1
        if idx > 100: break
