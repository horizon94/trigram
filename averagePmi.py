#coding=utf-8
import argparse

print '\n\nAVERAGE.'

## params
args = argparse.ArgumentParser('Input Parameters.')
args.add_argument('-iPath', type=str, dest='iPath', help='pmi sorted comments file path.')
args.add_argument('-oPath', type=str, dest='oPath', help='output file path.')
args.add_argument('-abs', type=int, dest='abs', help='whether or not use absolute PMI.')
args = args.parse_args()

ipFile = open(args.iPath, 'r')
opFile = open(args.oPath, 'w')

nowCom = ''
comCnt = 0
sumPmi = 0.0
for line in ipFile:
    [pmi, com] = line[:-1].split('\t')
    pmi = float(pmi)
    if 1 == args.abs: pmi = abs(pmi)
    if com == nowCom:
        comCnt += 1
        sumPmi += pmi
    else: # new comment: 1) compute avarage pmi; 2) reset data struct.
        if not '' == nowCom:
            avrPmi = sumPmi / comCnt
            opFile.write('%.4f\t%s\n'%(avrPmi,  nowCom))
        nowCom = com
        comCnt = 1
        sumPmi = pmi
if not '' == nowCom:
    avrPmi = sumPmi / comCnt
    opFile.write('%.6f\t%s\n'%(avrPmi, nowCom))


ipFile.close()
opFile.close()
