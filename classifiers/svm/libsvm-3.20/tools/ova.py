'''
Created on Apr 12, 2016

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

global labels,features,c,g,cExp,gExp


def count_labels(labels):
    _labels = []

    for i in range(len(labels)):
        for lab in labels[i]:
            if (lab not in _labels):
                _labels.append(lab)

    return _labels

def read_problem(file):
    assert os.path.exists(file), "%s not found." % (file)

    _labels = []
    _features = []

    in_file = open(file, "r")
    for line in in_file:
        _labels.append(line.split(' ')[0])
        _features.append(line.split(' ')[1:])
        '''
        spline = split(line)
        if spline[0].find(':') == -1:
            _labels.append(split(spline[0], ','))
            _features.append(join(spline[1:]))
        else:
            _labels.append([])
            _features.append(join(spline))'''
    in_file.close()

    return (_labels, _features)

def scale():
    train_pathname = 'tmp_binary'
    if testing: ###
    ###if len(sys.argv) > 2:
        print ('testing file exists')
         ###
        test_pathname = sys.argv[-1]
        ###test_pathname = sys.argv[2]
        file_name = os.path.split(test_pathname)[1]
        assert os.path.exists(test_pathname),"testing file not found"
        scaled_test_file = file_name + ".scale"
        predict_test_file = file_name + ".predict"
    
    cmd = '{0} -s "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, train_pathname, scaled_file)
    print('[########## ########] Scaling training data...')
    Popen(cmd, shell = True, stdout = PIPE).communicate()
    
def cross_validation():
    global time1, time2
    if output: ###
        cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" {3} "{4}"'.format(grid_py, svmtrain_exe, gnuplot_exe, grid_options, scaled_file) ###
    else: ###
        cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" {3} "{4}"'.format(grid_py, svmtrain_exe_q, gnuplot_exe, grid_options, scaled_file) ###
    ###cmd = 'python {0} -svmtrain "{1}" -gnuplot "{2}" "{3}"'.format(grid_py, svmtrain_exe_q, gnuplot_exe, scaled_file)
    # MODIFIED
    time1 = datetime.now()
    print('[' + str(time1).split('.')[0] + '] Cross validation...')
    # MODIFIED END
    f = Popen(cmd, shell = True, stdout = PIPE).stdout

    line = ''
    while True:
        last_line = line
        line = f.readline()
        if not line: break
    c,g,rate = map(float,last_line.split())
    
    print('[########## ########] Best c={0}, g={1} CV rate={2}'.format(c,g,rate))
    
    # MODIFIED
    time2 = datetime.now()
    cExp = int(math.log(c,2))
    gExp = int(math.log(g,2))
    

    return c,g,cExp,gExp
###Modified by seoh

## Added by seoh
# Build binary problem
def build_binary_problem(lab):
    problem = open("tmp_binary", "w+")
    #sub_instance=''
    for t in range(len(labels)):
        
        if lab in labels[t]: #if target label, give +1 
            sub_instance="+1"
            for i in features[t]:
                sub_instance +=' '+i
            #print labels[t]
            #problem.write("+1 %s\n" % features[t])
        else:#if not, give -1
            sub_instance="-1"
            for i in features[t]:
                sub_instance +=' '+i
            #problem.write("-1 %s\n" % features[t])
        #print sub_instance
        problem.write(sub_instance)
        #problem.write('\n')
    problem.close()
## Added by seoh
#if testing:
#    for i in range(len(all_labels)):
#        cmd = '{0} -c {1} -g {2} "{3}" "{4}"'.format(svmtrain_exe, c, g, scaled_file, file_name+str(i)+ ".model")
#    print
#else:
#    print

###Modified by seoh
def build_test(lab):
    global test_labels

    (test_labels, x) = read_problem(sys.argv[-1])
    out_test = open("tmp_test", "w+")
    #for i in range(len(test_labels)):
    #    out_test.write("+1 %s\n" % x[i])
    for t in range(len(test_labels)):
        if lab in test_labels[t]: #if target label, give +1 
            sub_instance="+1"
            for i in x[t]:
                sub_instance +=' '+i
            #print test_labels[t]
            #out_test.write("+1 %s\n" % x[t])
        else:#if not, give -1
            sub_instance="-1"
            for i in x[t]:
                sub_instance +=' '+i
            #out_test.write("-1 %s\n" % x[t])
        out_test.write(sub_instance)
        #out_test.write('\n')
    out_test.close()


def train(c,g,cExp,gExp):
    global time3
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
def test():
    #global s_tp, s_fp, s_fn, s_tn
    
    if testing: ###
    ###if len(sys.argv) > 2:
        # MODIFIED
        print('[########## ########] Output model: {0}'.format(model_file)) # move behind if len(sys.argv) > 2:
        # MODIFIED END
        cmd = '{0} -r "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, 'tmp_test', scaled_test_file)
        print('[########## ########] Scaling testing data...')
        Popen(cmd, shell = True, stdout = PIPE).communicate()
    
        cmd = '{0} "{1}" "{2}" "{3}"'.format(svmpredict_exe, scaled_test_file, model_file, predict_test_file)
        print('[' + str(datetime.now()).split('.')[0] + '] Testing...')
        Popen(cmd, shell = True).communicate()
        #Added by seoh# output_file: first column => predicted second column => actual label
        label=set()#training label set
        
        pred_f=open(predict_test_file,'r')
        #label_f=open('train_pathname','r')
        label_f=open('tmp_test','r')
        for l in label_f:
            label.add(l.split(' ')[0])
        tp=0.0
        fp=0.0
        fn=0.0
        tn=0.0
        for line in pred_f:
            predicted=line.split(',')[0]
            real=line.split(',')[1]
            if(predicted == '1') and (real == '1'):#real): #TP
                #print ('tp',predicted,real)
                tp += 1
                #print
            elif(predicted == '-1') and (real == '-1'):
                #print ('tn',predicted,real)
                tn += 1
            elif(predicted == '1') and (real == '-1'):
                #print ('fp',predicted,real)
                fp += 1
            else: #FP or FN
                #print ('fn',predicted,real)
                fn += 1
        if (tp == 0 and fp == 0) or (tp == 0 and fn == 0):
            print('[########## ########] Precision: {0}, Recall: {1}'.format(0,0))
        else:
            print('[########## ########] Precision: '+str(tp/(tp+fp))+', Recall: '+str(tp/(tp+fn)))
        #Added by seoh#
        print('[########## ########] Output prediction: {0}'.format(predict_test_file))
        #s_tp += tp
        #s_fp += fp
        #s_fn += fn
        #s_tn += tn
        print('[########## ########] tp:'+str(tp)+', fp:'+str(fp)+', tn:'+str(tn)+', fn: '+str(fn))
    # MODIFIED
    else: # below the print('Output prediction: {0}'.format(predict_test_file))
        print('[########## ########] Output evaluation: {0}'.format(scaled_file + '.c_'+ str(cExp) +'_g_' + str(gExp) + '.txt'))
    print('[' + str(datetime.now()).split('.')[0] + '] Time: Cross-Validation (' + str(time2-time1).split('.')[0] + '), Training (' + str(time3-time2).split('.')[0] + ')')
    
    return tp, fp, fn, tn
# MODIFIED END

def main():
    global labels, features, time1, time2,testing,test_pathname, scaled_test_file, predict_test_file
    #global s_tp, s_fp, s_fn, s_tn
    s_tp = 0.0
    s_fp = 0.0 
    s_fn = 0.0 
    s_tn = 0.0
    time0 = datetime.now()
    test_pathname = sys.argv[-1]
    (labels, features) = read_problem(train_pathname)
    _labels = set()
    #print labels
    #print features
    #all_labels = count_labels(labels)
    #print all_labels
    for l in labels:
        _labels.add(l)
    print _labels
    
    for lab in _labels:
    #for i in range(len(all_labels)):
        #lab=all_labels[i]
        #print lab
        #if(lab == '1209'):
            #continue
        print('[########## ########] For label {0}...'.format(lab))
        build_binary_problem(lab)
        #####scale()##############################
        if testing: ###
            ###if len(sys.argv) > 2:
            print ('testing file exists')
             ###
            test_pathname = sys.argv[-1]
            ###test_pathname = sys.argv[2]
            file_name = os.path.split(test_pathname)[1]
            assert os.path.exists(test_pathname),"testing file not found"
            scaled_test_file = file_name + ".scale"
            predict_test_file = file_name + ".predict"
    
        cmd = '{0} -s "{1}" "{2}" > "{3}"'.format(svmscale_exe, range_file, 'tmp_binary', scaled_file)
        print('[########## ########] Scaling training data...')
        Popen(cmd, shell = True, stdout = PIPE).communicate()
        #####scale()##############################
        
        (c,g,cExp,gExp)=cross_validation()
        train(c,g,cExp,gExp)
        build_test(lab)
        (tp, fp, fn, tn)=test()
        s_tp += tp
        s_fp += fp
        s_fn += fn
        s_tn += tn
    time4 = datetime.now()
    print('[########## ########] Overall tp: '+str(s_tp)+', fp: '+str(s_fp)+', tn: '+str(s_tn)+', fn: '+str(s_fn))
    print('[########## ########] Overall Precision: '+str(s_tp/(s_tp+s_fp))+', TPR: '+str(s_tp/(s_tp+s_fn))+', Recall: '+str(s_tp/(s_tp+s_fn))+', TNR: '+str(s_tn/(s_tn+s_fp)))
    print('[########## ########] Total running time: '+str(time4-time0).split('.')[0])
    #print('[########## ########] Overall Precision: {0}, Recall: {0}'.format(s_tp/(s_tp+s_fp),s_tp/(s_tp+s_fn)))
    #print('[########## ########] Overall TPR: {0}, TNR: {0}'.format(s_tp/(s_tp+s_fn),s_tn/(s_tn+s_fp)))
if len(sys.argv) <= 1:
    print('Usage: {0} [-log2c=begin,end,step] [-log2g=begin,end,step] [-o] [-worker=N ] [-v=N] training_file [testing_file]'.format(sys.argv[0])) ###
    ###print('Usage: {0} training_file [testing_file]'.format(sys.argv[0]))
    raise SystemExit

# svm, grid, and gnuplot executable files

is_win32 = (sys.platform == 'win32')
if not is_win32:
    svmscale_exe = "../svm-scale"
    svmtrain_exe = "../svm-train"
    # MODIFIED
    svmtrain_exe_q = "../svm-train-q" # to "if not is_win32:"
    # MODIFIED END
    svmpredict_exe = "../svm-predict"
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

main()