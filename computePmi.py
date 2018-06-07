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
    if (wIdl, wIdm, wIdr) in tg2f
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

def logProbCommGivenTitlTriGram(w2idL, ngram, comIdsL):
    bg2fL, tg2fL = ngram
    res = 0.0
    for i in range(len(comIdsL)-3):
        tg2fEle = 0.0
        bg2fEle = 0.0
        if (comIdsL[i], comIdsL[i+1], comIdsL[i+2]) in tg2fL:
            tg2fEle = tg2fL[(comIdsL[i], comIdsL[i+1], comIdsL[i+2])]
        if (comIdsL[i], comIdsL[i+1]) in bg2fL:
            bg2fEle = bg2fL[(comIdsL[i], comIdsL[i+1])]
        res += math.log(ngramDiv(tg2fEle,bg2fEle))
    return res/(len(comIdsL)-3)

def staticLittle(corpus):
    # init w2idL, add help words.
    w2idL = {unkWord:0}
    idx = 1
    helpWords = [frtWord, scdWord, lstWord]
    for w in helpWords:
        w2idL[w] = idx
        idx += 1

    # get w2idL, and trans text corpus to id corpus
    corpusIds = []
    corpusWds = []
    unkWords = set()
    unkWordsCnt = 0
    for line in corpus:
        lineIds = []
        words = line.split()
        for w in words:
            if w in w2id: # in vocabulary
                if w in w2idL:
                    lineIds.append(w2idL[w])
                else:
                    w2idL[w] = idx
                    lineIds.append(idx)
                    idx += 1
            else:
                unkWords.add(w)
                unkWordsCnt += 1
                lineIds.append(w2idL[unkWord])
        lineIds = [w2idL[frtWord], w2idL[scdWord]] + lineIds + [w2idL[lstWord]]
        corpusIds.append(lineIds)
        words = [frtWord, scdWord] + words + [lstWord]
        corpusWds.append(words)

    # statistic tri-gram
    wNum = len(w2idL)
    bg2fL = {}
    tg2fL = {}
    unkCmb2NumBg = {}
    unkCmb2NumTg = {}
    for lineId in range(len(corpusIds)):
        ids = corpusIds[lineId]
        ws = corpusWds[lineId]
        for i in range(len(ids)-3):
            bgKey = (ids[i], ids[i+1])
            tgKey = (ids[i], ids[i+1], ids[i+2])
            if bgKey in bg2fL:
                bg2fL[bgKey] += 1.0
                if tgKey in tg2fL: tg2fL[tgKey] += 1.0
                else: tg2fL[tgKey] = 1.0
            else:
                bg2fL[bgKey] = 1.0
                tg2fL[tgKey] = 1.0
            
            ## static unk combination
            if w2idL[unkWord] in bgKey:
                wsCmbBg = (ws[i], ws[i+1])
                if bgKey in unkCmb2NumBg:
                    if not wsCmbBg in unkCmb2NumBg[bgKey]: unkCmb2NumBg[bgKey].add(wsCmbBg)
                else:
                    tpSet1 = set()
                    tpSet1.add(wsCmbBg)
                    unkCmb2NumBg[bgKey] = tpSet1
            if w2idL[unkWord] in tgKey:
                wsCmbTg = (ws[i], ws[i+1], ws[i+2])
                if tgKey in unkCmb2NumTg:
                    if not wsCmbTg in unkCmb2NumTg[tgKey]: unkCmb2NumTg[tgKey].add(wsCmbTg)
                else:
                    tpSet2 = set()
                    tpSet2.add(wsCmbTg)
                    unkCmb2NumTg[tgKey] = tpSet2

    # average unk combination
    for tgK in unkCmb2NumTg:
        tg2fL[tgK] = float(tg2fL[tgK]) / len(unkCmb2NumTg[tgK])
    for bgK in unkCmb2NumBg:
        bg2fL[bgK] = float(bg2fL[bgK]) / len(unkCmb2NumBg[bgK])

    return w2idL, (bg2fL, tg2fL), corpusIds

def processOneTitle(nowTitl, nowComs, oFile):
    w2idL, ngram, corpusIdsL  = staticLittle(nowComs + [nowTitl])
    for i in range(len(nowComs)):
        comIdsL = corpusIdsL[i]
        logPrCmGnTi = logProbCommGivenTitlTriGram(w2idL, ngram, comIdsL)
        com = nowComs[i]
        logPrCm = logProbSentTriGram(com)
        
        pmi = logPrCmGnTi - logPrCm
        oFile.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'%(pmi, logPrCmGnTi, logPrCm, nowTitl, com))


# main
print '\n\nCOMPUTE PMI.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='output file path.')
args.add_argument('-vocPath', type=str, dest='vocPath', help='vocabulary file path.')
args.add_argument('-biGramPath', type=str, dest='biGramPath', help='bi-gram dump path.')
args.add_argument('-uniGramPath', type=str, dest='uniGramPath', help='uni-gram dump path.')
args.add_argument('-triGramPath', type=str, dest='triGramPath', help='tri-gram dump path.')
args.add_argument('-debug', type=int, dest='debug', help='run as debugging.')
args.add_argument('-debug_num', type=int, dest='debug_num', help='corpus lines num when debugging.')
args.add_argument('-com_num_cut', type=int, dest='com_num_cut', help='filter out those titles whose comment num less than this.')
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
idxLine = 0
for line in iFile:
    [titl, comm] = line.strip().split('\t')
    if nowTitl == titl:
        nowComs.append(comm)
    else: # new title
        if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
            processOneTitle(nowTitl, nowComs, oFile)
        nowTitl = titl
        nowComs = [comm]
    idxLine += 1
    if 0 == idxLine % 10000:
        sys.stdout.write('%dw lines processed\r' % (idxLine/10000))
        sys.stdout.flush()
    if 1 == args.debug and idxLine > args.debug_num: break # debug
if not '' == nowTitl and len(nowComs) >= args.com_num_cut:
    processOneTitle(nowTitl, nowComs, oFile)


iFile.close()
oFile.close()
