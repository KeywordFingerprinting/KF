import os
HOME=os.path.expanduser('~')
def split_libsvm(file):
    PATH=os.path.join(HOME,'Trace','part2','libsvm')
    
    f=open(os.path.join(PATH,file),'r')
    features=[]
    labels=[]
    
    i=0
    for line in f:
        feature=[]
        label=line.split(' ')[0]
        for item in line.split(' ')[1:]:
            feature.append(item.split(':')[1])
        features.append(feature)
        labels.append(label)
        i += 1            
    return (features,labels)

def split_libsvm_close(file,nFold,per_instance,n_turn):
    PATH=os.path.join(HOME,'Trace','part2','libsvm')
    
    f=open(os.path.join(PATH,file),'r')
    train_features=[]
    train_label=[]
    test_features=[]
    test_label=[]
    pre_label=''
    l_thres=(n_turn-1)*(per_instance/nFold) #0,8
    u_thres=n_turn*(per_instance/nFold) #8,16
    i=0
    for line in f:
        feature=[]
        label=line.split(' ')[0]
        for item in line.split(' ')[1:]:
            feature.append(item.split(':')[1])
        if ((i%per_instance) >= l_thres)and((i%per_instance)<u_thres): # test dataset
            
            test_label.append(label) # label
            test_features.append(feature)
        else:
            train_label.append(label) # label
            train_features.append(feature)
        i += 1            
    return (train_features,train_label,test_features,test_label)

def split_libsvm_open(file,nFold,per_instance,n_turn,tn_instance,n_monitored):
    PATH=os.path.join(HOME,'Trace','part2','libsvm')
    
    f=open(os.path.join(PATH,file),'r')
    train_features=[]
    train_label=[]
    test_features=[]
    test_label=[]
    pre_label=''
    l_thres=(n_turn-1)*(per_instance/nFold) #0,8,....,72
    u_thres=n_turn*(per_instance/nFold) #8,16,.....,80
    tn_l_thres=(n_monitored*per_instance)+(n_turn-1)*(tn_instance/nFold) # if tn_instance=40,000, 8000,
    tn_u_thres=(n_monitored*per_instance)+n_turn*(tn_instance/nFold) #12000,
    i=0
    for line in f:
        feature=[]
        label=line.split(' ')[0]
        for item in line.split(' ')[1:]:
            feature.append(item.split(':')[1])
            
        if label != '120900': #tps
            
            if ((i%per_instance) >= l_thres)and((i%per_instance)<u_thres): # test dataset
                
                test_label.append(label) # label
                test_features.append(feature)
            else:
                train_label.append(label) # label
                train_features.append(feature)
        else: #tns
            #print i
            #print tn_l_thres,tn_u_thres
            if (i >= tn_l_thres)and(i<tn_u_thres): # test dataset
                #print label
                test_label.append(label) # label
                test_features.append(feature)
            else:
                train_label.append(label) # label
                train_features.append(feature)
        
        
        i += 1            
    return (train_features,train_label,test_features,test_label)


if __name__ == '__main__':
    file='google100_2'
    for i in range(10):
        n_turn=i+1
        #(train_features,train_label,test_features,test_label)=split_libsvm_open(file, 10, 100, n_turn, 10000, 100)
        (train_features,train_label,test_features,test_label)=split_libsvm_close(file, 10, 100, n_turn)
        fw=open(os.path.join(HOME,'Trace','part2','libsvm',str(i)+'.txt'),'w+')
        j=0
        for line in test_features:
            
            fw.write(test_label[j]+' ')
            for tls in line:
                fw.write(tls+' ')
            
            j += 1

