'''
Created on Apr 14, 2016

@author: seeunoh
'''
#!/usr/bin/env python

import sys
import os
# MODIFIED
import math # below import os
from datetime import datetime
# MODIFIED END
from subprocess import *
#from pandas_confusion import ConfusionMatrix


if len(sys.argv) <= 1:
    print('Usage: {0} [-log2c=begin,end,step] [-log2g=begin,end,step] [-o] [-worker=N ] [-v=N] training_file [testing_file]'.format(sys.argv[0])) ###
    ###print('Usage: {0} training_file [testing_file]'.format(sys.argv[0]))
    raise SystemExit

# svm, grid, and gnuplot executable files

is_win32 = (sys.platform == 'win32')
if not is_win32:
    svmscale_exe = "../svm-scale"
    svmtrain_exe = "../svm-train"
    #svmtrain_exe = "/home/hoppernj/seoh/libsvm-3.21/libsvm-3.21/svm-train"
    # MODIFIED
    svmtrain_exe_q = "../svm-train-q" # to "if not is_win32:"
    #svmtrain_exe_q = "/home/hoppernj/seoh/libsvm-3.21/libsvm-3.21/svm-train"
    # MODIFIED END
    svmpredict_exe = "../svm-predict"
    #svmpredict_exe = "/home/hoppernj/seoh/libsvm-3.21/libsvm-3.21/svm-predict"
    grid_py = "./grid_patched.py" ###
    ###grid_py = "./grid.py"
    gnuplot_exe = "/usr/bin/gnuplot"
else:
        # example for windows
    svmscale_exe = r"..\windows\svm-scale.exe"
    svmtrain_exe = r"..\windows\svm-train.exe"
    # MODIFIED
    svmtrain_exe_q = r"..\windows\svm-train-q.exe" # to else-case of "if not is_win32:"
    # MODIFIED END
    svmpredict_exe = r"..\windows\svm-predict.exe"
    gnuplot_exe = r"c:\tmp\gnuplot\binary\pgnuplot.exe"
    grid_py = r".\grid_patched.py" ###
    ###grid_py = r".\grid.py"

assert os.path.exists(svmscale_exe),"svm-scale executable not found"
assert os.path.exists(svmtrain_exe),"svm-train executable not found"
assert os.path.exists(svmpredict_exe),"svm-predict executable not found"
###assert os.path.exists(gnuplot_exe),"gnuplot executable not found"
###assert os.path.exists(grid_py),"grid.py not found"
if not os.path.exists(gnuplot_exe): ###
    gnuplot_exe = 'null' ###
assert os.path.exists(grid_py),"grid_patched.py not found" ###
# MODIFIED
assert os.path.exists(svmtrain_exe_q),"svm-train-q executable not found" # below the block of asserts
# MODIFIED END

# MODIFIED
folds = 10 # below the block of asserts
output = False ###
# MODIFIED END
for i in range(1, len(sys.argv)): ###
    if sys.argv[i].startswith('-v='): ###
        folds = int(sys.argv[i].lstrip('-v=')) ###
    elif sys.argv[i] == '-o': ###
        output = True ###

grid_options = '' ###
if sys.argv[-2].startswith('-') or sys.argv[0] == sys.argv[-2]: ###
    testing = False ###
    train_pathname = sys.argv[-1] ###
    grid_options = ' '.join(el for el in sys.argv[1:-1]).replace('=', ' ') ###
else: ###
    testing = True ###
    train_pathname = sys.argv[-2] ###
    grid_options = ' '.join(el for el in sys.argv[1:-2]).replace('=', ' ') ###
###train_pathname = sys.argv[1]
assert os.path.exists(train_pathname),"training file not found"
file_name = os.path.split(train_pathname)[1]
scaled_file = file_name + ".scale"
model_file = file_name + ".model"
range_file = file_name + ".range"
time0=datetime.now()
if testing: ###
###if len(sys.argv) > 2:
    test_pathname = sys.argv[-1] ###
    ###test_pathname = sys.argv[2]
    file_name = os.path.split(test_pathname)[1]
    assert os.path.exists(test_pathname),"testing file not found"
    scaled_test_file = file_name + ".scale"
    predict_test_file = file_name + ".predict"

cmd = '{0} -s "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, train_pathname, scaled_file)
print('[########## ########] Scaling training data...')
Popen(cmd, shell = True, stdout = PIPE).communicate()

if output: ###
    cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" {3} "{4}"'.format(grid_py, svmtrain_exe, gnuplot_exe, grid_options, scaled_file) ###
else: ###
    cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" {3} "{4}"'.format(grid_py, svmtrain_exe_q, gnuplot_exe, grid_options, scaled_file) ###
###cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" "{3}"'.format(grid_py, svmtrain_exe_q, gnuplot_exe, scaled_file)
# MODIFIED
time1 = datetime.now()
print(cmd)
print('[' + str(time1).split('.')[0] + '] Cross validation...')
# MODIFIED END
f = Popen(cmd, shell = True, stdout = PIPE).stdout

line = ''
while True:
    last_line = line
    line = f.readline()
    #print "line=",line
    if not line: break
print("last_line=",last_line)
c,g,rate = map(float,last_line.split())
print('[########## ########] Best c={0}, g={1} CV rate={2}'.format(c,g,rate))

# MODIFIED
time2 = datetime.now()
cExp = int(math.log(c,2))
gExp = int(math.log(g,2))
if testing: ###
###if len(sys.argv) > 2:
    cmd = '{0} -c {1} -g {2} "{3}" "{4}"'.format(svmtrain_exe, c, g, scaled_file, model_file)
    print('[' + str(time2).split('.')[0] + '] Training...')
else:
    cmd = '{0} -v {1} -c {2} -g {3} -x {4} -y {5} "{6}"'.format(svmtrain_exe, folds, c, g, cExp, gExp, scaled_file)
    print('[' + str(time2).split('.')[0] + '] Training - Cross validating...')
if not output: ###
    Popen(cmd, shell = True, stdout = PIPE).communicate()
time3 = datetime.now()
# MODIFIED END

# MODIFIED
##print('Output model: {0}'.format(model_file))
# MODIFIED END
if testing: ###
###if len(sys.argv) > 2:
    # MODIFIED
    print('[########## ########] Output model: {0}'.format(model_file)) # move behind if len(sys.argv) > 2:
    # MODIFIED END
    cmd = '{0} -r "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, test_pathname, scaled_test_file)
    print('[########## ########] Scaling testing data...')
    Popen(cmd, shell = True, stdout = PIPE).communicate()

    cmd = '{0} "{1}" "{2}" "{3}"'.format(svmpredict_exe, scaled_test_file, model_file, predict_test_file)
    print('[' + str(datetime.now()).split('.')[0] + '] Testing...')
    Popen(cmd, shell = True).communicate()
        # added by seoh
        #Added by seoh# output_file: first column => predicted second column => actual label
    #training label set
    
    #pred_f=open(predict_test_file,'r')
    label_f=open(train_pathname,'r')
    labels = set()
    for j in label_f:
        if not (j.split(' ')[0] == '1209'):
            labels.add(j.split(' ')[0])
    
    
    
    s_tp=0.0
    s_fp=0.0
    s_fn=0.0
    s_tn=0.0
    acc=[]
    pre=[]
    tpr=[]
    pred_label=[]
    real_label=[]
    for label in labels:
        tp=0.0
        fp=0.0
        fn=0.0
        tn=0.0
        total=0.0
        pred_f=open(predict_test_file,'r')
        num_lines = sum(1 for line in open(predict_test_file))
        for line in pred_f:
                    #print line.split(',')
            total += 1
            predicted=''
            real=''
            predicted=line.split(',')[0]
            
            real=line.split(',')[1]
            if label == '0':
                pred_label.append(predicted)
                real_label.append(real)
            #print ('predicted: {:f},real: {:f}'.format(float(predicted), float(real)))
            #print ('predicted: '+predicted+',real: '+real)
            #print ('(predicted == real)=>',(predicted == real),'(real in labels)=>',(real in labels),'(real == 1209)=>',(real == '1209'))
            # 
            
                
            
            if (predicted == real) and (real == label): #TP
            #print ('predicted: {0},real: {0}'.format(predicted, real))
             #   print 'tp'
                tp += 1
            #print
            elif(predicted == real) and (real != label): #TN
              #  print 'tn'
                tn += 1
            #print label
            elif(predicted != real) and (real == label): #FP
               # print 'fn'
                fn += 1
            #print ('predicted: {0},real: {0}'.format(predicted, real))
            
            elif(predicted != real) and (predicted == label):
              #  print 'fp'
                fp += 1
            else:
                print('')
    #            if real in label:#FP
    #                fp += 1
    #            else:
    #                fn += 1
            print('[########## ########] For label '+label+":")
            print('[########## ########] TP: '+str(tp)+', FP: '+str(fp)+',FN: '+str(fn)+',TN: '+str(tn))
            #print('[########## ########] Precision: '+str(tp/(tp+fp)*100)+'TPR: '+str(format(tp/(tp+fn)*100)))
            #print('[########## ########] TPR: '+str(format(tp/(tp+fn)*100)+', TNR:'+str(tn/(tn+float(fp)))))
            s_tp += tp
            s_fp += fp
            s_fn += fn
            s_tn += tn
        
        if not ((tp+tn+fp+fn) == 0):
            #print('[########## ########] For label '+label+": Accuracy="+str((tp+tn)/total))   
            acc.append((tp+tn)/total) 
        else:
            #print('[########## ########] For label '+label+": Accuracy=0")   
            acc.append(0)
            # added by seoh
        if not ((tp+fp) == 0):
            #print('[########## ########] For label '+label+": Precision="+str(tp/(tp+fp)))
            pre.append(tp/(tp+fp))
        else:
            #print('[########## ########] For label '+label+": Precision=0")
            pre.append(0)
        if not ():
            #print('[########## ########] For label '+label+": Precision="+str(tp/(tp+fn)))
            tpr.append(tp/(tp+fn))
        else:
            #print('[########## ########] For label '+label+": TPR=0")
            tpr.append(0)
    print('[########## ########] Output prediction: {0}'.format(predict_test_file))
    #print('[########## ########] Overall Precision: '+str(s_tp/(s_tp+s_fp)*100)+', Overall TPR: '+str(format(s_tp/(s_tp+s_fn)*100)))
    print('[########## ########] Overall Precision: '+str(sum(pre)/len(pre)*100)+', Overall TPR: '+str(sum(tpr)/len(tpr)*100))
    print('[########## ########] Overall Accuracy: '+str((s_tp/len(pred_label))*100))
    print('[########## ########] OVerall TP: '+str(s_tp)+', FP: '+str(s_fp)+',FN: '+str(s_fn)+',TN: '+str(s_tn))
    
    #print('[########## ########] OVerall Accuracy: '+str(s_tp)+', FP: '+str(s_fp)+',FN: '+str(s_fn)+',TN: '+str(s_tn))
    #print acc
    #@cm = ConfusionMatrix(real_label, pred_label)
    #@cm.print_stats()
# MODIFIED
else: # below the print('Output prediction: {0}'.format(predict_test_file))
    print('[########## ########] Output evaluation: {0}'.format(scaled_file + '.c_'+ str(cExp) +'_g_' + str(gExp) + '.txt'))
time3 = datetime.now()
print('[' + str(datetime.now()).split('.')[0] + '] Time: Cross-Validation (' + str(time2-time1).split('.')[0] + '), Training (' + str(time3-time2).split('.')[0] + ')')
#print('[########## ########] Overall Accuracy: '+str(((s_tp+s_tn)/(s_tp+s_fn+s_tn+s_fp))*100))
#print('[########## ########] Overall Accuracy: '+str(sum(acc)/len(acc)))
print('[########## ########] Overall Runningtime:'+str(time3-time0).split('.')[0])

# MODIFIED END
