#coding=utf-8

'''
'''

import sys
import math
import cPickle as pickle
import argparse
import numpy as np

# functions
def ngramDiv(up, bl):
    up = float(up)
    bl = float(bl)
    if 0.0 == up:
        if 0.0 == bl: return 1.0
        else: return zeroAppr
    else: return up / bl

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
    assert not 0.0 == xi_
    # asset: 0.0 == xi_ will not happen
    #        because unkown words is seen as <unk>
    ni_ = 0
    if ugKey in ug2n:
        ni_ = ug2n[ugKey]
    cndProbDisd = max(xij-deltaBg, 0) / xi_
    lmda = args.deltaBg * ni_ / xi_
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
    assert not 0.0 == xij_
    # question: what about xij_ is 0.0
    #           which means no such combinaton <wi, wj>  occurs in the ngram.
    cndProbDisd = max(xijk-deltaTg, 0) / xij_
    lmda = deltaTg * nij_ / xij_
    res = cndProbDisd + lmda * probWordGivenWordNKSM(widm, widr)
    assert not 0.0 == res
    return math.log(res)

def logProbSentTriGram(sent):
    sent = sntHead + sent + sntTail
    words = sent.split()
    ids = [w2id[w] for w in words]
    res = 0.0
    for i in range(len(ids)-2):
        res += logProbWordGivenTwoWordsNKSM(ids[i], ids[i+1], ids[i+2])
    return res/(len(ids)-2)

def processOneComment(titl, comm, score):
    logPrCmGnTi = -score
    logPrCm = logProbSentTriGram(comm)
    pmi = logPrCmGnTi - args.lamda * logPrCm
    oFile.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'%(pmi, logPrCmGnTi, logPrCm, titl, comm))

def defaultDelta():
    tgn1 = 0
    tgn2 = 0
    bgn1 = 0
    bgn2 = 0
    for bg in bg2f:
        if 1.0 == bg2f[bg]:
            bgn1 += 1
        elif 2.0 == bg2f[bg]:
            bgn2 += 1
    for tg in tg2f:
        if 1.0 == tg2f[tg]:
            tgn1 += 1
        elif 2.0 == tg2f[tg]:
            tgn2 == 1
    deltaBg = float(bgn1) / (bgn1 + 2*bgn2)
    deltaTg = float(tgn1) / (tgn1 + 2*tgn2)
    return deltaBg, deltaTg

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
for ug in ug2n:
    bgNum += ug2n[ug]
deltaBg,deltaTg = defaultDelta()
print 'tri-gram loaded.'

## notification
print('lambda: %f' % args.lamda)
print('KN smoothing, delta of bi-gram: %f' % deltaBg)
print('KN smoothing, delta of tri-gram: %f' % deltaTg)

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
