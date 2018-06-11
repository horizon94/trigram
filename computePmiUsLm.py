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

def probWordNKSM(wid):
    n_j = 0
    if wid in ug2nR:
        n_j = ug2nR[wid]
    res = float(n_j) / bgNum
    assert not 0.0 == res
    return res

def probWordGivenWordNKSM(widl, widr):
    xij = 0.0
    xi_ = 0.0
    ugKey = widl
    bgKey = widr
    if bgKey in bg2f:
        xij = bg2f[bgKey]
    if ugKey in ug2f:
        xi_ = ug2f[ugKey]
    ni_ = 0
    if ugKey in ug2n:
        ni_ = ug2n[ugKey]
    if   2.0 >  xij                : delta = bgD1
    elif 2.0 <= xij and 3.0 > xij  : delta = bgD2
    elif 3.0 <= xij                : delta = bgD3
    cndProbDisd = 0.0
    lmda = 1.0
    if not 0.0 == xi_:
        cndProbDisd = max(xij-delta, 0) / xi_
        lmda = delta * ni_ / xi_
    res = cndProbDisd + lmda * probWordNKSM(widr)
    return res

def logProbWordGivenTwoWordsNKSM(widl, widm, widr):
    xijk = 0.0
    xij_ = 0.0
    bgKey = (widl, widm)
    tgKey = (widl, widm, widr)
    if tgKey in tg2f:
        xijk = tg2f[tgKey]
    if bgKey in bg2f:
        xij_ = bg2f[bgKey]
    nij_ = 0
    if bgKey in bg2n:
        nij_ = bg2n[bgKey]
    if   2.0 >  xijk                : delta = tgD1
    elif 2.0 <= xijk and 3.0 > xijk : delta = tgD2
    elif 3.0 <= xijk                : delta = tgD3
    cndProbDisd = 0.0
    lmda = 1.0
    if not 0.0 == xij_: 
        cndProbDisd = max(xijk-delta, 0) / xij_
        lmda = delta * nij_ / xij_
    res = cndProbDisd + lmda * probWordGivenWordNKSM(widm, widr)
    assert not 0.0 == res
    return math.log(res)

def logProbSentTriGram(sent):
    sent = sntHead + sent + sntTail
    words = sent.split()
    ids = [word2id(w, w2id) for w in words]
    res = 0.0
    for i in range(len(ids)-2):
        res += logProbWordGivenTwoWordsNKSM(ids[i], ids[i+1], ids[i+2])
    return res/(len(ids)-2)

def processOneComment(titl, comm, score):
    logPrCmGnTi = -score
    logPrCm = logProbSentTriGram(comm)
    pmi = logPrCmGnTi - args.lamda * logPrCm
    oFile.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'%(pmi, logPrCmGnTi, logPrCm, titl, comm))

def defaultDelta(ng2f):
    n1 = 0
    n2 = 0
    n3 = 0
    n4 = 0
    for ng in ng2f:
        if 1.0 == ng2f[ng]:
            n1 += 1
        elif 2.0 == ng2f[ng]:
            n2 += 1
        elif 3.0 == ng2f[ng]:
            n3 += 1
        elif 4.0 == ng2f[ng]:
            n4 += 1
    Y = float(n1) / (n1 + 2*n2)
    D1 = 1 - 2*Y*(float(n2) / n1)
    D2 = 2 - 3*Y*(float(n3) / n2)
    D3 = 3 - 4*Y*(float(n4) / n3)
    return D1, D2, D3


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
ug2f = {}
bg2f = {} # bigram,  as the form of ((w1id, w2id): freq)
tg2f = {} # trigram,  as the form of ((w1id, w2id, w3id): freq)
ug2n = {}
bgNum = 0
ug2nR = {}
bg2n = {}
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
ug2f,bg2f,tg2f,ug2n,ug2nR,bg2n = pickle.load(triGramFile)
triGramFile.close()
#for ug in ug2n:
#    bgNum += ug2n[ug]
bgNum = len(bg2f)
bgD1, bgD2, bgD3 = defaultDelta(bg2f)
tgD1, tgD2, tgD3 = defaultDelta(tg2f)
print 'tri-gram loaded.'

## notification
print('lambda: %.2f' % args.lamda)
print 'Kneser-Ney smoothing used.'
print('discount for bi-gram,  D1: %.4f, D2: %.4f, D3: %.4f.' % (bgD1, bgD2, bgD3))
print('discount for tri-gram, D1: %.4f, D2: %.4f, D3: %.4f.' % (tgD1, tgD2, tgD3))

## compute and output PMI for each <title, comment>
iFile = open(args.iPath, 'r')
oFile = open(args.oPath, 'w')
idxLine = 0
for line in iFile:
    [titl, comm, lmsc] = line.strip().split('\t')
    lmsc = float(lmsc)
    processOneComment(titl, comm, lmsc)
    idxLine += 1
    if 0 == idxLine % 10000:
        sys.stdout.write('%dw lines processed\r' % (idxLine/10000))
        sys.stdout.flush()
    if 1 == args.debug and idxLine > args.debug_num: break # debug

iFile.close()
oFile.close()
