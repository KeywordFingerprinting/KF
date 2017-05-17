import sys
import os
from sys import stdout
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.cross_validation import cross_val_score

import pandas as pd
import numpy as np
import csv
import time
from datetime import datetime
import shutil
import CVformat

HOME=os.path.expanduser('~')

def checkequal(lst):
    return lst[1:] == lst[:-1]

def eva_result(csvfile,exp): # exp='close' or 'open' 
    f=open(os.path.join(os.path.dirname(__file__), 'data',csvfile),'r')
    reader=csv.reader(f, delimiter = ',')
    total=0.0
    tp=0.0
    acc=0.0
    if exp == "close":
        
        for row in reader:
            if row[0] == "actual":
                continue
            #print row[0],row[1]
            if row[0]==row[1]:
                tp += 1
            total += 1
        acc=tp/total
        print "Accuracy=",acc
        return (acc,0,0,0)
    else:
        TN=0.0
        TP=0.0
        FP=0.0
        FN=0.0
        TTP=0.0
        total=0.0 # total samples in monitored set
        for row in reader:
            predicted=row[1]
            actual=row[0]
            if (predicted == actual):  
                if (predicted == '120900'):#true negative
                    TN += 1
                else:
                    TTP += 1
                    
                    TP += 1
                    total += 1
            else:
                if (predicted == '120900'):#false negative
                    FN += 1
                    total += 1
                elif (actual == '120900'):
                    FP += 1
                else:
                    #if it is twoclass eval, confusion between monitored set is TP
                    TP += 1
                    total += 1
        
        
        print ('Accuracy= '+str(TTP/total))
            #print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
        print TP,FP,TN,FN
        if(TP+FP == 0.0):
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= 0')
        else:
            print ('TPR= '+str(TP/(TP+FN))+', FPR= '+str(FP/(FP+TN))+', Precision= '+str(TP/(FP+TP)))
        
        
        return ((TP+TN)/TP+TN+FP+FN,TP/(FP+TP),TP/(FN+TP),FP/(FP+TN),TTP/total)
        
            
    


def RFrun(purpose,exp,file,n_est,n_fold,per_instance,tn_instance,n_monitored):
    
    result_path=os.path.join(os.path.dirname(__file__), 'data',file+'_result_'+time.strftime("%Y%m%d_%H%M")+'.csv')
    fw_result=open(result_path,'a+')
    
    time_train=[]
    time_test=[]
    for n_turn in range(10):
        print 'Preparing for Cross-validation'
        if purpose == 'classifier':
            if exp == 'close':
                (train_features,train_label,test_features,test_label)=CVformat.split_libsvm_close(file,n_fold,per_instance,n_turn+1)
            else:
                (train_features,train_label,test_features,test_label)=CVformat.split_libsvm_open(file, n_fold,per_instance, n_turn+1, tn_instance, n_monitored)
            #
        else:
            (train_features,train_label,test_features,test_label)=CVformat.split_libsvm_close(file,n_fold,per_instance,n_turn+1)
        print "Training the random forest (this may take a while)..."
    
        time1=datetime.now()
        # Initialize a Random Forest classifier with 100 trees
        forest = RandomForestClassifier(n_estimators = 100,n_jobs=-1,oob_score=True)
    
        # Fit the forest to the training set, using the bag of words as
        # features and the sentiment labels as the response variable
        #
        # This may take a few minutes to run
        ## (list_data, listlabel)
        
        forest = forest.fit(train_features, train_label)
        
    
        # Create an empty list and append the clean reviews one by one
    
        time2=datetime.now()
        # Use the random forest to make sentiment label predictions
        time_train.append(time2-time1)
        print "Predicting test labels...\n"
        result = forest.predict(test_features)
    
        # Copy the results to a pandas dataframe with an "id" column and
        # a "sentiment" column
        time3=datetime.now()
        time_test.append(time3-time2)
        output = pd.DataFrame( data={"actual":test_label, "predicted":result} )
    
        # Use pandas to write the comma-separated output file
        #output.to_csv(os.path.join(os.path.dirname(__file__), 'data', 'results'+str(n_turn)+'.csv'), index=False, quoting=3)
        output.to_csv(fw_result, index=False, quoting=3)
        print "Wrote results to csv"
            
    # Compute final result
    '''
    (acc,precision,recall,wm_acc)=eva_result(result_path,"close")
    print "Time for training:",sum(time_train)
    print "Time for testing:",sum(time_test)
    '''
    return (time_train,time_test,result_path)
    #writer.writerow([file,acc,precision,recall,wm_acc,sum(time_train),sum(time_test)])
    #return 

def KFPrun(exp,file,n_est,n_fold,per_instance,tn_instance,n_monitored):
    result_path=os.path.join(os.path.dirname(__file__), 'data',file+'_result_'+time.strftime("%Y%m%d_%H%M")+'.csv')
    fw_result=open(result_path,'a+')
    keep_top=80
    time_train=[]
    time_test=[]
    for n_turn in range(10):
        print 'Preparing for Cross-validation'
        if exp == 'close':
            (train_features,train_label,test_features,test_label)=CVformat.split_libsvm_close(file,n_fold,per_instance,n_turn+1)
        else:
            (train_features,train_label,test_features,test_label)=CVformat.split_libsvm_open(file, n_fold,per_instance, n_turn+1, tn_instance, n_monitored)
        #
        print "Training the random forest (this may take a while)..."
    
        time1=datetime.now()
        # Initialize a Random Forest classifier with 100 trees
        forest = RandomForestClassifier(n_estimators = 100,n_jobs=-1,oob_score=True)
    
        # Fit the forest to the training set, using the bag of words as
        # features and the sentiment labels as the response variable
        #
        # This may take a few minutes to run
        ## (list_data, listlabel)
        
        forest = forest.fit(train_features, train_label)
        train_leaf = zip(forest.apply(train_features), train_label)
        test_leaf = zip(forest.apply(test_features), test_label)
                        
        
        #print 'train_leaf:',len(train_leaf)
        #print 'test_leaf:',len(test_leaf)
        
        ## distance function
        print "Compute distance..."
        direc = HOME
        if not os.path.exists(direc):
            os.mkdir(direc)
        monitored_directory = os.path.join(os.path.dirname(__file__), 'data','monitored-distances')#rootdir + "/" + mon_type + "-monitored-distances/"
        if not os.path.exists(monitored_directory):
            os.mkdir(monitored_directory)
        unmonitored_directory =  os.path.join(os.path.dirname(__file__), 'data','unmonitored-distances')
        if not os.path.exists(unmonitored_directory):
            os.mkdir(unmonitored_directory)
    
        # Make into numpy arrays
        train_leaf = [(np.array(l, dtype=int), v) for l, v in train_leaf] #l:feature vector, v:label
        test_leaf = [(np.array(l, dtype=int), v) for l, v in test_leaf]
        #print test_leaf
        t=0
        for (feature,label) in test_leaf:
           if label == '120900':
               break 
           t += 1
        for i, instance in enumerate(test_leaf[:(t+1)]):
            if i%100==0:
                stdout.write("\r%d fold: %d out of %d" %(n_turn,i, t+1))
                stdout.flush()
    
            temp = []
            for item in train_leaf:
                # vectorize the average distance computation
                d = np.sum(item[0] != instance[0]) / float(item[0].size)
                if d == 1.0:
                    continue
                temp.append((d, instance[1], item[1]))
            tops = sorted(temp)[:keep_top]
            myfile = open(os.path.join(monitored_directory,'%d_%d_%s.txt' %(n_turn,int(instance[1]), i)), 'w')
            for item in tops:
                myfile.write("%s\n" % str(item))
            myfile.close()
    
        for i, instance in enumerate(test_leaf[(t+1):]):
            if i%100==0:
                stdout.write("\r%d fold: %d out of %d" %(n_turn,i, len(test_leaf)-(t+1)))
                stdout.flush()
    
            temp = []
            for item in train_leaf:
                # vectorize the average hamming distance computation
                d = np.sum(item[0] != instance[0]) / float(item[0].size)
                if d == 1.0:
                    continue
                temp.append((d, instance[1], item[1]))
            tops = sorted(temp)[:keep_top]
            myfile = open(os.path.join(unmonitored_directory,'%d_%d_%s.txt' %(n_turn,int(instance[1]), i)), 'w')
            for item in tops:
                myfile.write("%s\n" % str(item))
            myfile.close()
            
def distance_stats(knn=10):
    """
        For each test instance this picks out the minimum training instance distance, checks (for mon) if it is the right label and checks if it's knn are the same label
    """

    monitored_directory = os.path.join(os.path.dirname(__file__), 'data','monitored-distances')
    unmonitored_directory = os.path.join(os.path.dirname(__file__), 'data','unmonitored-distances')

    TP=0.0
    TTP=0.0
    FP =0.0
    for file in os.listdir(monitored_directory):
        fn = os.path.join(monitored_directory, file)
        data = open(str(fn)).readlines()
        internal_count = 0
        external_count = 0
        for i in data[:knn]:
            distance = float(eval(i)[0])
            true_label = float(eval(i)[1])
            predicted_label = float(eval(i)[2])
            if true_label == predicted_label:
                internal_count += 1
            else:
                if predicted_label != 120900:
                    external_count += 1 # if predicted label is still monitored
        if internal_count == knn: # if all k-closest neighbors have the same labels, that is TP
            TTP+=1
        if (external_count+internal_count) == knn:
            TP+=1
    path, dirs, files = os.walk(monitored_directory).next()
    file_count1 = len(files)
    print "TP = ", TP

    
    for file in os.listdir(unmonitored_directory):
        fn = os.path.join(unmonitored_directory, file)
            
        data = open(str(fn)).readlines()
        internal_count = 0
        test_list = []
        internal_test = []
        for i in data[:knn]:
            distance = float(eval(i)[0])
            true_label = float(eval(i)[1])
            predicted_label = float(eval(i)[2])
            internal_test.append(predicted_label)
        if checkequal(internal_test) == True and internal_test[0] <= 100: # predicted is monitored but actual is unmonitored.
            FP+=1

    path, dirs, files = os.walk(unmonitored_directory).next()
    file_count2 = len(files)
    print "TP,FP = ",TP,FP
    print "Precision=",TP/(TP+FP)
    print "WM-accuracy=",TTP/float(file_count1)
    return TP/float(file_count1), FP/float(file_count2),TP/(TP+FP),TTP/float(file_count1)
if __name__ == '__main__':
    if len(sys.argv) == 1:
        print "Input Valid Arguments: python RandomForest2.py num-iter '[data1,...,dataN]' '[n_back1,...,n_backN]' 'exp' n_est_rf n_fold n_ins_mon n_mon knn"
        print "num-iter: number of iterations to derive the final metrics"
        print "[data1,...,dataN]: list of data file (use libsvm file)"
        print "[n_back1,...,n_backN]: list of number of instances in background set"
        print "exp: 'close' or 'open'"
        print "n_est_rf: number of estimators for Ramdom Forest"
        print "n_fold: number of folds (we used 10)"
        print "n_ins_mon: number of instances in monitored traces"
        print "n_mon: number of classes in monitored traces"
        print "knn: k for k-fingerprinting"
    f_result=open(os.path.join(os.path.dirname(__file__), 'data','metrics.csv'),'a')
    writer=csv.writer(f_result, delimiter = ',') # result file
    
    for i in range(sys.argv[1]): # number of iterations to derive the final metrics
        
        files=[]#['google100_2'] # data file (use libsvm file)
        for file in sys.argv[9:9+sys.argv[2]]:
            files.append(file)
        tn_instances=[]#[10000] # number of instances in background set
        for tn_instance in sys.argv[9+sys.argv[2]:9+sys.argv[2]+sys.argv[3]]:
            tn_instances.append(tn_instance)
        k=0 
        for file in files:
            #file='google100_new_google12000_new'
            
            exp=sys.argv[4]#'close' # closed or open-world experiment
            n_est=sys.argv[5]#100 # number of estimators for Ramdom Forest
            n_fold=sys.argv[6]#10 # number of folds (we used 10)
            per_instance=sys.argv[7]#100 # number of instances in monitored traces
            tn_instance=tn_instances[k]
            n_monitored=sys.argv[8]#100 # number of classes in monitored traces
            
            ## 1.Run Random Forest
            KFPrun(exp,file,n_est,n_fold,per_instance,tn_instance,n_monitored)
            ## 2.Use distance metrics based on hamming distance (Hayes et al.)
            (tpr,fpr,precision,wm_acc)=distance_stats(knn=sys.argv[9]) # set 'k'
            ## 3.Added our metrics evaluation for both binary and multiclass classification
            print "TPR:",tpr
            print "FPR:",fpr
            print "Precision:",precision
            print "WM-acc:",wm_acc
            
            
            ## 4.Write results in metrics.csv
            writer.writerow([file,0,precision,tpr,fpr,wm_acc,0,0])#int(str(time3-time2).split('.')[0].split(':')[2])
            k += 1
            '''
            (time_train,time_test,result_path)=RFrun(exp,file,n_est,n_fold,per_instance,tn_instance,n_monitored)
            (acc,precision,recall,fpr,wm_acc)=eva_result(result_path, exp)
            print "Time for training:",sum(time_train)
            print "Time for testing:",sum(time_test)
            if exp == 'close':
                print "Accuracy:",acc
            else:
                print "Accuracy:",wm_acc
            writer.writerow([file,acc,precision,recall,fpr,wm_acc,str(sum(time_train)).split('.')[0],str(sum(time_test)).split('.')[0]])#int(str(time3-time2).split('.')[0].split(':')[2])
            k += 1
           '''
           
