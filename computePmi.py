#coding=utf-8

'''
'''

import sys
import math
import pickle
import argparse
import numpy as np

# functions
def word2id(word, wordDict):
    if word in wordDict:
        return wordDict[word]
    else:
        return wordDict[unkWord]

def logProbWord(wordId):
    return math.log(float(id2f[wordId]) / wordFrqSum)
    #return math.log(float(ug2f[word2id(word, w2id)]) / biGramFrqSum)

def logProbWordGivenWord(wordId, givenWordId):
    xij = bg2f[(givenWordId,wordId)]
    xi_ = ug2f[givenWordId]
    return math.log(float(xij) / xi_)

def logProbWordGivenTwoWords(wIdl, wIdm, wIdr):
    xijk = tg2f[(wIdl, wIdm, wIdr)]
    xij_ = bg2f[(wIdl, wIdm)]
    return math.log(float(xijk) / xij_)

def logProbSentBiGram(sent):
    words = sent.split()
    assert 0 < len(words)
    ids = [word2id(w, w2id) for w in words ]
    res = 0.0
    res += logProbWord(ids[0])
    for i in range(len(ids)-1):
        res += logProbWordGivenWord(ids[1], ids[0])
    return res/len(ids)

def logProbSentTriGram(sent):
    words = sent.split()
    assert 0 < len(words)
    ids = [word2id(w, w2id) for w in words ]
    res = 0.0
    res += logProbWord(ids[0])
    if 1 < len(words):
        res += logProbWordGivenWord(ids[1], ids[0])
    for i in range(len(ids)-2):
        res += logProbWordGivenTwoWords(ids[i], ids[i+1], ids[i+2])
    return res/len(ids)

def logProbCommGivenTitlBiGram(w2idL, id2fL, wFrqSumL, xij, xi_, comIdsL):
    assert 0 < len(comIdsL)
    res = 0.0
    res += math.log(float(id2fL[comIdsL[0]]) / wFrqSumL)
    for i in range(len(comIdsL)-1):
        res += math.log(float(xij[ comIdsL[0] ][ comIdsL[1] ]) / xi_[comIdsL[0]])
    return res/len(comIdsL)

def logProbCommGivenTitlTriGram(w2idL, id2fL, wFrqSumL, xij, xi_, comIdsL, tgL):
    assert 0 < len(comIdsL)
    res = 0.0
    res += math.log(float(id2fL[comIdsL[0]]) / wFrqSumL)
    if 1 < len(comIdsL):
        res += math.log(float(xij[ comIdsL[0] ][ comIdsL[1] ]) / xi_[comIdsL[0]])
    for i in range(len(comIdsL)-2):
        res += math.log(float(tgL[(comIdsL[i], comIdsL[i+1], comIdsL[i+2])]) / xij[ comIdsL[i] ][ comIdsL[i+1] ] )
    return res/len(comIdsL)

def staticLittle(corpus):
    # get vocab
    w2idL = {unkWord:0}
    id2fL = {0:0}
    wFrqSumL = 0
    corpusIds = []
    idx = 1
    unkWords = set()
    unkWordsCnt = 0
    for line in corpus:
        lineIds = []
        words = line.split()
        for w in words:
            if w in w2id: # in vocabulary
                if w in w2idL:
                    id2fL[w2idL[w]] += 1
                    lineIds.append(w2idL[w])
                else:
                    w2idL[w] = idx
                    id2fL[idx] = 1
                    lineIds.append(idx)
                    idx += 1
            else:
                #id2fL[w2idL[unkWord]] += 1
                unkWords.add(w)
                unkWordsCnt += 1
                lineIds.append(w2idL[unkWord])
        corpusIds.append(lineIds)
    if len(unkWords) > 0:
        id2fL[w2idL[unkWord]] += unkWordsCnt / len(unkWords) # use average frequency as <unk> frequency
    for i in id2fL: wFrqSumL += id2fL[i] 

    wNum = len(w2idL)
    xij = np.array([[0]*wNum]*wNum)
    tgL = {}
    for ids in corpusIds:
        for i in range(len(ids)-2):
            xij[ ids[i] ][ ids[i+1] ] += 1
            tgKey = (ids[i], ids[i+1], ids[i+2])
            if tgKey in tgL: tgL[tgKey] +=  1
            else: tgL[tgKey] = 1
        if len(ids) >= 2:
            xij[ ids[len(ids)-2] ][ ids[len(ids)-1] ] += 1
    xi_ = xij.sum(axis=1)
    return w2idL, id2fL, wFrqSumL, xij, xi_, corpusIds, tgL


# main
print '\nCOMPUTE PMI.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='corpus file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='output file path.')
args.add_argument('-vocPath', type=str, dest='vocPath', help='vocabulary file path.')
args.add_argument('-biGramPath', type=str, dest='biGramPath', help='bi-gram dump path.')
args.add_argument('-uniGramPath', type=str, dest='uniGramPath', help='uni-gram dump path.')
args.add_argument('-triGramPath', type=str, dest='triGramPath', help='tri-gram dump path.')
args = args.parse_args()

wordFrqSum = 0
w2id = {}
id2f = {}
ug2f = {} # unigram, as the form of (wid: freq)
bg2f = {} # bigram,  as the form of ((w1id, w2id): freq)
tg2f = {} # trigram,  as the form of ((w1id, w2id, w3id): freq)
unkWord = '<unk>'

## load vocabulary, get word to id dict
vocFile = open(args.vocPath, 'r')
idx = 0
for line in vocFile:
    w,f = line.strip().split('\t')
    f = int(f)
    w2id[w] = idx
    wordFrqSum += f
    id2f[idx] = f
    idx += 1
print('%d words loaded.' % len(id2f))

## load uni-gram, bi-gram, tri-gram
uniGramFile = open(args.uniGramPath, 'r')
ug2f = pickle.load(uniGramFile)
uniGramFile.close()
print 'uni-gram loaded.'
biGramFile = open(args.biGramPath, 'r')
bg2f = pickle.load(biGramFile)
biGramFile.close()
print 'bi-gram loaded.'
triGramFile = open(args.triGramPath, 'r')
tg2f = pickle.load(triGramFile)
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
        ### compute cooccurrence times and occurrence times based on little corpus
        ### compute and output PMI for every comment
        ### update struct
        if not '' == nowTitl:
            w2idL, id2fL, wFrqSumL, xij, xi_, corpusIdsL, tgL  = staticLittle(nowComs + [nowTitl])
            for i in range(len(nowComs)):
                comIdsL = corpusIdsL[i]
                #logPrCmGnTi = logProbCommGivenTitlBiGram(w2idL, id2fL, wFrqSumL, xij, xi_, comIdsL)
                logPrCmGnTi = logProbCommGivenTitlTriGram(w2idL, id2fL, wFrqSumL, xij, xi_, comIdsL, tgL)

                com = nowComs[i]
                logPrCm = logProbSentTriGram(com)

                pmi = logPrCmGnTi - logPrCm
                oFile.write('%.6f\t%.6f\t%.6f\t%s\t%s\n'%(pmi, logPrCmGnTi, logPrCm, nowTitl, com))
        nowTitl = titl
        nowComs = [comm]
    idxLine += 1
    if 0 == idxLine % 10000:
        sys.stdout.write('%dw lines processed\r' % (idxLine/10000))
        sys.stdout.flush()
    if idxLine > 1000000: break # debug

iFile.close()
oFile.close()
