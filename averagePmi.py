#coding=utf-8
import argparse

print '\nAVERAGE.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='pmi sorted comments file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='output file path.')
args.add_argument('-cmFreqPath', type=str, dest='cmFreqPath', help='comments with frequency file path.')
args = args.parse_args()

ipFile = open(args.iPath, 'r')
opFile = open(args.oPath, 'w')
cFreqFile = open(args.cmFreqPath, 'r')

## get frequency of all comments
c2f = {}
for line in cFreqFile:
    line = line.lstrip()
    freq = int(line[ : line.find(' ')])
    comm = line[line.find(' ')+1 : -1] # remove '\n' at tail
    c2f[comm] = freq
cFreqFile.close()
print 'comment frequency loaded.'


nowCom = ''
comCnt = 0
sumPmi = 0.0
for line in ipFile:
    [pmi, com] = line[:-1].split('\t')
    pmi = float(pmi)
    if com == nowCom:
        comCnt += 1
        sumPmi += pmi
    else: # new comment: 1) compute avarage pmi; 2) reset data struct.
        if not '' == nowCom:
            avrPmi = sumPmi / comCnt
            try:
                opFile.write('%.6f\t%d\t%s\n'%(avrPmi, c2f[nowCom], nowCom))
            except KeyError, e:
                print 'KeyError.'
                print 'comment: ' + str(nowCom)
                exit()
        nowCom = com
        comCnt = 1
        sumPmi = pmi

ipFile.close()
opFile.close()
