# Running Classifiers

# 1.SVM: 
	-Use 10-fold cross validation for both testing and parameters selection for RBF
	-Run instuction:
	 python svm/libsvm-3.20/tools/easy_patched_closed.py -log2c=-7,7,1 -log2g=-5,2,1 
	 -worker=8 -v=10 'dataset' (testing_data)
	
	-Except related searches analysis, we did not input (testing_data) 
	-For evaluation, use python metrics.py result_file is_multi(True or False)


# 2.kFP:
	-We used codes provided by Hayes[2]
	-We additionally 10-fold approach to split the training and testing dataset
	-Run instruction: 
	python kFP/RandomForest2.py num-iter num-data num-back 'exp' n_est_rf n_fold n_ins_mon n_mon knn data1 ... dataN n_back1 ... n_backN
	 
	  num-iter: number of iterations to derive the final metrics
      num-data: # of data files (length of [data1,...,dataN])
      num-back: #  of number of instances in background set (legnth of [n_back1,...,n_backN])
      exp: 'close' or 'open'
      n_est_rf: number of estimators for Ramdom Forest
      n_fold: number of folds (we used 10)
      n_ins_mon: number of instances in monitored traces
      n_mon: number of classes in monitored traces
      knn: k for k-fingerprinting
      [data1,...,dataN]: list of data file (use libsvm file)
      [n_back1,...,n_backN]: list of number of instances in background set
