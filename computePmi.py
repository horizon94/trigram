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

def logProbWordGivenTwoWords(wIdl, wIdm, wIdr):
    xijk = tg2f[(wIdl, wIdm, wIdr)]
    xij_ = bg2f[(wIdl, wIdm)]
    return math.log(float(xijk) / xij_)

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
        tg2fEle = tg2fL[(comIdsL[i], comIdsL[i+1], comIdsL[i+2])]
        bg2fEle = bg2fL[(comIdsL[i], comIdsL[i+1])]
        res += math.log(float(tg2fEle) / bg2fEle )
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

    # statistic tri-gram
    wNum = len(w2idL)
    bg2fL = {}
    tg2fL = {}
    for ids in corpusIds:
        for i in range(len(ids)-3):
            bgKey = (ids[i], ids[i+1])
            tgKey = (ids[i], ids[i+1], ids[i+2])
            if bgKey in bg2fL:
                bg2fL[bgKey] += 1
                if tgKey in tg2fL: tg2fL[tgKey] += 1
                else: tg2fL[tgKey] = 1
            else:
                bg2fL[bgKey] = 1
                tg2fL[tgKey] = 1
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
triGramFile = open(args.triGramPath, 'r')
for line in triGramFile:
    w1id,w2id,w3id, f = line.strip().split('\t')
    tgK = (int(w1id), int(w2id), int(w3id))
    tg2f[tgK] = int(f)
triGramFile.close()
print 'tri-gram loaded.'
biGramFile = open(args.biGramPath, 'r')
for line in biGramFile:
    w1id,w2id, f = line.strip().split('\t')
    bgK = (int(w1id), int(w2id))
    bg2f[bgK] = int(f)
biGramFile.close()
print 'bi-gram loaded.'

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
