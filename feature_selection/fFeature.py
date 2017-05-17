'''
Created on Jan 20, 2016
fine-grained feature extraction: number of incoming packets, number of outgoing packets, number of incoming tor cells, number of outgoing tor cells, total sum of incoming tls, total sum of outgoing tls

'''
#import dpkt
import csv
#import pcapy
import os
import math
import sys
#from decimal import Decimal
from collections import defaultdict
#Setting
#rFILEPATH: pcap, wFILEPATH: csv, sIPADDR:source IP, dIPADDR:destination IP(google.com)
def round_down(num, divisor):
    value=abs(num) - (abs(num)%divisor)
    if num<0:
        return -value
    else:
        return value

def extractFeatures(root_gb,csvfolders):
    #folders=['143youtube_80','18244youtube_child_1']#torset_021716'# Target csv folder
    for folder in csvfolders:
        print folder
        HOME=os.path.expanduser('~')
        if not os.path.exists(os.path.join(HOME,'Trace',root_gb)):
            os.makedirs(os.path.join(HOME,'Trace',root_gb))
        if not os.path.exists(os.path.join(HOME,'Trace',root_gb,'feature')):
            os.makedirs(os.path.join(HOME,'Trace',root_gb,'feature'))
        if not os.path.exists(os.path.join(HOME,'Trace',root_gb,'feature',folder)):
            os.makedirs(os.path.join(HOME,'Trace',root_gb,'feature',folder))
        TRACE=os.path.join(HOME,'Trace')
        wFILEPATH=os.path.join(TRACE,root_gb,'csv',folder)
        fFILEPATH=os.path.join(TRACE,root_gb,'feature',folder)
        
        NOISE=[]
        
        
        
        
        
        
        #ssl_noise = [line.strip() for line in open("/Volumes/Macintosh HD 1/ssl_noise2.txt",'r')]
        #tcp_noise = [line.strip() for line in open("/Volumes/Macintosh HD 1/tcp_noise2.txt",'r')]
        
            #writer.writeheader()
            #writer2.writeheader()
            
        for file in os.listdir(wFILEPATH):
            if '~lock' in file:
                continue
            
            tlsVec=[]
            tCell=[]
            totVec=[]
            r_tlsVec=[]
            r_tcpVec=[]
            
            burstVec=[]
            contVec=[]
            
            cumulContVec=[]
            CumulContTCellVec=[]
            cont=[]
            contTC=[]
            reqVec=[]
            cumulTLSVec=[]
            cumulTCellVec=[]
            
            if file == "noise" or file == "noise2":
                continue
            label = file.split('_')
            name = label[1]
            #print name
            columns = defaultdict(list)
            
            
            r_tcpVec=[]
            r_tlsVec=[]
            
            
            
            
            
            
            if(file == 'txt'or file == 'csv' or file == '.DS_Store' or file == '.test.swp'):
                continue
            #print wFILEPATH+"/"+file
            f = open(wFILEPATH+"/"+file,'rU')
            print wFILEPATH+"/"+file
            reader = csv.reader(f)
            reader.next()
            row=[]
            
            burstVec.append(name)
            
            reqVec.append(name)
            cumulTLSVec.append(name)
            cumulTCellVec.append(name)
            
            for row in reader:
                
                for (i,v) in enumerate(row):
                    
                    
                    
                    columns[i].append(v)
            
            #print columns[1]
            
            #print(columns[6])
            #print("\n")
            
            r_tcpVec.append(name)
            totVec.append(name)
            
            tot=0.0
            numTCP=0
            for bytes in columns[6]: #TCP
                bytes = float(bytes)
                
                #add for contents analysis
                vcell2=math.ceil(abs(bytes)/600)
                vcell=math.floor(abs(bytes)/512)
                #if bytes in NOISE:
                 #   continue
                #add
                numTCP=numTCP+1
                tot=tot+bytes
                r_tcpVec.append(-600*vcell2)
                
            #totVec.append(tot)
            totVec.append(numTCP)# total number of packets
            #print(columns[7])
            #print("\n")
            contVec.append(name)
            cumulContVec.append(name)
            CumulContTCellVec.append(name)
            cont.append(name)
            contTC.append(name)
            tlsVec.append(name)
            r_tlsVec.append(name)
            tCell.append(name)
            upCell=0
            downCell=0
            
            pre=0
            tot=0.0
            numTLS=0
            torCell=0
            burstSize=[]
            burstGNum=[]
            burstTotNum=0
            burstNum=0
            init=0
            checkCont=0
            tempCont=[]
            tempContGroup=[]
            nInp=0
            nOutp=0
            for bytes in columns[7]:#TLS
                
                bytes = float(bytes)
                
                numTLS=numTLS+1
                tot=tot+bytes
                tlsVec.append(bytes)
                     
                #rounding
                
                vcell2=math.ceil(abs(bytes)/600)
                vcell=math.floor(abs(bytes)/512)
                
                if bytes<0: #downstream (incoming packets)
                    #print bytes
                    r_tlsVec.append(-600*vcell2)
                    
                    
                    downCell=downCell+vcell
                    torCell=torCell+vcell
                    nInp=nInp+1
                    
                    
                else: #upstream (outgoing packets)
                    #print bytes
                    r_tlsVec.append(600*vcell2)
                    
                    
                    upCell=upCell+vcell
                    nOutp=nOutp+1
                    
                    
            
                #rounding
                pre=float(pre)
               
                if pre*bytes >= 0: # same direction
                                
                    if bytes<0: #downstream
                        
                        
                        checkCont=checkCont+1
                        tempCont.append(-abs(bytes))
                            
                        burstTotNum=burstTotNum+1
                        if init != 0:
                            burstNum=burstNum+1
                        burstSize.append(abs(bytes))
                    
                        #upCell=upCell+vcell
                        
                else: # different direction    
                    #print "negative, burstNum="+str(burstNum)
                    
                    
                    if bytes<0: #downstream
                        
                        tCell.append(upCell)
                        upCell=0
                        #downCell=0
                    else: # upstream
                        checkCont=checkCont-1
                        tempContGroup.append(tempCont)
                        tempCont=[]
                       
                        tCell.append(-downCell)
                        if burstNum != 0:
                            
                            burstGNum.append(burstNum+1)
                        
                        downCell=0
                        burstNum=0
                
             
                pre=bytes
                init= init+1
            
            tempContGroup.append(tempCont)    
            max_group=0
            max_list=[]
            for group in tempContGroup:
                if (len(group)>max_group):
                    max_group=len(group) 
                    max_list=group
                    
        
            tempCont=max_list
            
            if(burstNum>0):
                burstGNum.append(burstNum)
            if upCell>0:
                tCell.append(upCell)
            if downCell>0:
                tCell.append(-downCell)
           
            
            temp=0.0
            tc_temp=0.0
            
                
            #print file
            burstVec.append(burstTotNum)
            if len(burstSize) != 0:
                burstVec.append(-min(burstSize))
                
                burstVec.append(-sum(burstSize))
                burstVec.append(max(burstGNum))
                burstVec.append(math.ceil(sum(burstGNum)/len(burstGNum)))
                
            if len(tempCont) != 0:
                contVec.append(len(tempCont))
                contVec.append(sum(tempCont))
                contVec.append(max(tempCont))
                contVec.append(sum(tempCont)/len(tempCont))
            for bytes in tempCont:
                temp=temp+bytes
                cumulContVec.append(temp)
                cont.append(bytes)
                contTC.append(math.floor(abs(bytes)/512))
                
                tc_temp=tc_temp+math.floor(abs(bytes)/512)
                CumulContTCellVec.append(tc_temp)
            temp=0.0
            cnt=0
            for bytes in tlsVec:
                if cnt==0:
                    cnt += 1
                    continue
                temp += float(bytes)
                if temp!=0.0:
                    cumulTLSVec.append(temp)
                    cumulTCellVec.append(round_down(temp,512)/512)
                    cnt += 1
            
            
            contlist=tempCont
            reqVec=tlsVec
            contlist.reverse()
            reqVec.reverse()
            pre1=0
            cnt=0
            for bytes in contlist:
                reqVec.remove(bytes)
            reqVec.reverse()
                
            totVec.append(nInp)
            totVec.append(nOutp)
            totVec.append(tot)# total bytes of TLS record tranmitted
           
            totVec.append(torCell)# total number of tor cells
            feature_data={
                "/torCell_"+folder: tCell,
                "/Total_"+folder: totVec,
                "/roundedTCP_"+folder: r_tlsVec,
                "/roundedTLS_"+folder: r_tcpVec,
                "/burstTotal_"+folder: burstVec,
                "/contentsTotal_"+folder: contVec,
                "/cumulatedCont_"+folder: cumulContVec,
                "/cumulatedContTCell_"+folder: CumulContTCellVec,
                "/Resp_"+folder: cont,
                "/RespTCell_"+folder: contTC,
                "/Reqest_"+folder: reqVec,
                "/cumulatedTLS_"+folder: cumulTLSVec,
                "/cumulatedTCell2_"+folder: cumulTCellVec
                          }
            for eachfilename, eachlist in feature_data.items():
                target_path=os.path.join(HOME,'Trace',root_gb,'feature',folder,eachfilename+'.csv')
                print fFILEPATH+target_path
                
                with open(fFILEPATH+target_path, 'a+') as csvfile:
                    writer = csv.writer(csvfile) 
                    writer.writerow(eachlist)
        
            
            
if __name__ == "__main__":
    
    if len(sys.argv) == 1:
        print "Input Valid Arguments: python fFeature.py '[csv-folder1,...,csv-folderN]'"
    folders=[]
    for folder in sys.argv[1:]:
        folders.append(folder)
    root_gb='part2'
    extractFeatures(root_gb, folders)
            
        

