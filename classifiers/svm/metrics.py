import csv
import os
import time
import numpy as np
import itertools
import operator
import sys

from click.core import Command
HOME=os.path.expanduser('~')
keyword=set()
def evalOpenMetric(filename,multiClass):# when we have same training and testing file, do the 10 fold cross validation
    #pPATH=os.path.join(HOME,'ndss16','libsvm-3.20','tools',filename)
    pPATH=os.path.join(HOME,'SVM_result',filename)
    f=open(pPATH)
    TN=0.0
    TP=0.0
    FP=0.0
    FN=0.0
    TTP=0.0
    total=0.0 # total samples in monitored set
    for line in f:
        predicted=line.split(',')[1]
        actual=line.split(',')[2]
        if (predicted == actual):  
            if (predicted == '120900'):#true negative
                TN += 1
            else:
                TTP += 1
                keyword.add(actual)
                TP += 1
                total += 1
        else:
            if (predicted == '120900'):#false negative
                FN += 1
                total += 1
            elif (actual == '120900'):
                FP += 1
            else:
                if multiClass: #if it is multiclass eval, confusion between monitored set is FP
                    FP += 1
                else: #if it is twoclass eval, confusion between monitored set is TP
                    TP += 1
                total += 1
    
    
    #statistic(keyword)
    #print TP, FN, FP, TN
    if multiClass: # if multi-class, use accuracy within monitored set
        print ('Accuracy= '+str(TTP/total))
        #print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
    else: #if two class, use TPR, FPR, Precision
        if(TP+FP == 0.0):
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= 0')
        else:
            print TP,FN,FP,TN
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
def evalOpenMetric2(filename,multiClass):# when we have same training and testing file, do the 10 fold cross validation
    #pPATH=os.path.join(HOME,'ndss16','libsvm-3.20','tools',filename)
    pPATH=os.path.join(HOME,'SVM_result',filename)
    f=open(pPATH)
    TN=0.0
    TP=0.0
    FP=0.0
    FN=0.0
    TTP=0.0
    total=0.0 # total samples in monitored set
    for line in f:
        predicted=line.split(',')[0]
        actual=line.split(',')[1]
        if (predicted == actual):  
            if (predicted == '120900'):#true negative
                TN += 1
            else:
                TTP += 1
                keyword.add(actual)
                TP += 1
                total += 1
        else:
            if (predicted == '120900'):#false negative
                FN += 1
                total += 1
            elif (actual == '120900'):
                FP += 1
            else:
                if multiClass: #if it is multiclass eval, confusion between monitored set is FP
                    FP += 1
                else: #if it is twoclass eval, confusion between monitored set is TP
                    TP += 1
                total += 1
    
    
    #statistic(keyword)
    #print TP, FN, FP, TN
    if multiClass: # if multi-class, use accuracy within monitored set
        print ('Accuracy= '+str(TTP/total))
        #print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
    else: #if two class, use TPR, FPR, Precision
        if(TP+FP == 0.0):
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= 0')
        else:
            print TP,FN,FP,TN
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
            
if __name__ == "__main__":
    if len(sys.argv)==1:
        print "Please input valid arguments: python metrics.py file_name multi-or-binary"
        print "file_name: result file for evaluation"
        print "multi-or-binary: True for multiclass, False for binary classification"
    file=sys.argv[1]
    gb=sys.argv[2]
    evalOpenMetric(file,gb)
    # Please use evalOpenMetric2 for related search result file evaulation
    #evalOpenMetric2(file,gb)
    