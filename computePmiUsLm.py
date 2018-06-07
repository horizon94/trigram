#coding=utf-8

'''
'''

import sys
import math
import cPickle as pickle
import argparse
import numpy as np

# functions
def word2id(word, wordDict):
    if word in wordDict:
        return wordDict[word]
    else:
        return wordDict[unkWord]

def ngramDiv(up, bl):
    up = float(up)
    bl = float(bl)
    if 0.0 == up:
        if 0.0 == bl: return 1.0
        else: return zeroAppr
    else: return up / bl

def logProbWordGivenTwoWords(wIdl, wIdm, wIdr):
    xijk = 0.0
    xij_ = 0.0
    if (wIdl, wIdm, wIdr) in tg2f:
        xijk = tg2f[(wIdl, wIdm, wIdr)]
    if (wIdl, wIdm) in bg2f:
        xij_ = bg2f[(wIdl, wIdm)]
    return math.log(ngramDiv(xijk,xij_))

def logProbSentTriGram(sent):
    sent = sntHead + sent + sntTail
    words = sent.split()
    ids = [word2id(w, w2id) for w in words]
    res = 0.0
    for i in range(len(ids)-3):
        res += logProbWordGivenTwoWords(ids[i], ids[i+1], ids[i+2])
    return res/(len(ids)-3)

def processOneTitle(nowTitl, nowComs, nowScrs, oFile):
    for i in range(len(nowComs)):
        logPrCmGnTi = -nowScrs[i]
        com = nowComs[i]
        logPrCm = logProbSentTriGram(com)
        
        pmi = logPrCmGnTi - args.lamda * logPrCm
        oFile.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'%(pmi, logPrCmGnTi, logPrCm, nowTitl, com))


# main
print '\n\nCOMPUTE PMI.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='output file path.')
args.add_argument('-vocPath', type=str, dest='vocPath', help='vocabulary file path.')
args.add_argument('-triGramPath', type=str, dest='triGramPath', help='tri-gram dump path.')
args.add_argument('-debug', type=int, dest='debug', help='run as debugging.')
args.add_argument('-debug_num', type=int, dest='debug_num', help='corpus lines num when debugging.')
args.add_argument('-lamda', type=float, dest='lamda', help='the weight of comment probability.')
args = args.parse_args()

w2id = {}
bg2f = {} # bigram,  as the form of ((w1id, w2id): freq)
tg2f = {} # trigram,  as the form of ((w1id, w2id, w3id): freq)
unkWord = '<unk>'
frtWord = '<s1>'
scdWord = '<s2>'
lstWord = '</tail>'
sntHead = frtWord + ' ' + scdWord + ' '
sntTail =  ' ' + lstWord
zeroAppr = 1.0 / 10000

## load vocabulary, get word to id dict
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
print('%d words loaded.' % len(w2id))

## tri-gram
triGramFile = open(args.triGramPath, 'rb')
bg2f,tg2f = pickle.load(triGramFile)
triGramFile.close()
print 'tri-gram loaded.'

## compute and output PMI for each <title, comment>
iFile = open(args.iPath, 'r')
oFile = open(args.oPath, 'w')
nowTitl = ''
nowComs = []
nowScrs = []
idxLine = 0
for line in iFile:
    [titl, comm, lmsc] = line.strip().split('\t')
    lmsc = float(lmsc)
    if nowTitl == titl:
        nowComs.append(comm)
        nowScrs.append(lmsc)
    else: # new title
        if not '' == nowTitl:
            processOneTitle(nowTitl, nowComs, nowScrs, oFile)
        nowTitl = titl
        nowComs = [comm]
        nowScrs = [lmsc]
    idxLine += 1
    if 0 == idxLine % 10000:
        sys.stdout.write('%dw lines processed\r' % (idxLine/10000))
        sys.stdout.flush()
    if 1 == args.debug and idxLine > args.debug_num: break # debug
if not '' == nowTitl:
    processOneTitle(nowTitl, nowComs, nowScrs, oFile)


iFile.close()
oFile.close()
