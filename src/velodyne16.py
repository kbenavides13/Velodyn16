# To change this license header, choose License Headers in Project Properties.
# To change this template file, choose Tools | Templates
# and open the template in the editor.

__author__ = "kenneth"
__date__ = "$Mar 12, 2018 10:38:39 PM$"

import os 
import matplotlib.pyplot as plt
import numpy as np
import struct
from scapy.all import *

class Velo16_PointCloud():
    
    def __init__(self):
        self.layer1=[]
        self.layer2=[]
        self.packets=[]
        self.matrix1=np.array(0)
        self.matrix2=np.array(0)
        self.viewCompleted=False;
        
    def readBlock(self, frame, idBlock):
        layerPoint1 = []; #initialize layer
        layerPoint2 = []
        azimuth = frame[2+idBlock*100]+256*frame[3+idBlock*100] #42 bytes header 100 bytes each block
        layerPoint1+=[azimuth]
        layerPoint2+=[0] #fill with 0. interpolate later
        for i in range(16):
            distance1=frame[4+idBlock*100+3*i]+256*frame[5+idBlock*100+3*i]
            distance2=frame[52+idBlock*100+3*i]+256*frame[53+idBlock*100+3*i]
            if (distance1==0):
                distance1=np.nan
            if (distance2==0):
                distance2=np.nan
            layerPoint1+=[distance1]
            layerPoint2+=[distance2]
        return [layerPoint1,layerPoint2]
        
    def readFrame(self, frame, mode_dual=False):
        if (mode_dual):
            for idBlock in range(12):
                layerPoints=self.readBlock(frame,idBlock)
                if idBlock%2==0:
                    self.layer1+=layerPoints
                else:
                    self.layer2+=layerPoints
                #test.layer2matrix()
                #test.plotChannel(1,test.matrix1)
                if len(self.layer1)>3 and self.layer1[-2][0]<self.layer1[-4][0]:
                    print(self.layer1[-4][0],self.layer1[-3][0],self.layer1[-2][0],self.layer1[-1][0])
                    self.viewCompleted=True
        else:
            for idBlock in range(12):
                layerPoints=self.readBlock(frame,idBlock)
                self.layer1+=layerPoints
                if len(self.layer1)>3 and self.layer1[-2][0]<self.layer1[-4][0]:
                    print(self.layer1[-4][0],self.layer1[-3][0],self.layer1[-2][0],self.layer1[-1][0])
                    self.viewCompleted=True
        
    
    def interpolateMissingAzimuths(self):
        if self.layer1!=[]:
            for i in range(int(len(self.layer1)/2)):
                if i>0 and (self.layer1[2*i][0]<self.layer1[2*i-2][0]):
                    self.layer1[2*i-1][0]=(self.layer1[2*i][0]/2+self.layer1[2*i-2][0]/2+18000)%36000
                else:
                    self.layer1[2*i-1][0]=self.layer1[2*i][0]/2+self.layer1[2*i-2][0]/2
                    
    def interpolaterMissingPoints(self):
        print("building...")
        
    def readView(self, mode_dual=False):
        #read all packets until azimuth does a completely round
        i=0
        n=len(self.packets)
        self.viewCompleted=False
        self.layer1=[]
        self.layer2=[]
        while (i<n and not (self.viewCompleted)):
            packet = self.packets[i]
            packetBytes = bytes(packet[Raw])
            total=len(packetBytes)
            if (total==1206):
                self.readFrame(packetBytes, mode_dual)
            i+=1
        print(len(self.layer1))
        self.interpolateMissingAzimuths()
        self.packets = self.packets[i:]
            
    def readFile(self,filename='ex_sample_10.pcap'):
        self.packets = rdpcap(filename)
        
    def layer2matrix(self):
        self.matrix1=np.matrix(self.layer1)
        self.matrix2=np.matrix(self.layer2)
        
    def plotChannel(self,n, matrix):
        #plt.plot(matrix[2:,n]-matrix[:-2,n])
        if n==0:
            plt.plot(matrix[:,n])
        else:
            plt.plot(matrix[:,n])
            plt.plot(matrix[:,n+1])
            plt.plot(matrix[:,n+2])
            plt.plot(matrix[:,n+3])
        plt.show()
        
    def plotChannel2(self,n,k, matrix):
        #plt.plot(matrix[2:,n]-matrix[:-2,n])
        if n==0:
            plt.plot(matrix[:,n])
        else:
            for i in range(k):
                plt.plot(np.multiply(matrix[:,n],np.cos(np.divide(matrix[:,0],18000/np.pi))),np.multiply(matrix[:,n],np.sin(np.divide(matrix[:,0],18000/np.pi))))
                n+=1
                #plt.plot(np.divide(matrix[:,0],18000/np.pi))
                #plt.plot(np.cos(np.divide(matrix[:,0],18000/np.pi)))
        plt.show()
        
def testingChannelsCartesian(test):
    while(len(test.layer1)>0):
        test.layer2matrix()
        test.plotChannel(0,test.matrix1)
        test.plotChannel(1,test.matrix1)
        test.plotChannel(5,test.matrix1)
        test.plotChannel(9,test.matrix1)
        test.plotChannel(13,test.matrix1)
        test.readView(True)
        
def testingChannelsCylindrical(test,n,k):
    while(len(test.layer1)>0):
        test.layer2matrix()
        test.plotChannel2(n,k,test.matrix1)
        test.readView(True)

    

if __name__ == "__main__":
    print ("Hello World")
    test= Velo16_PointCloud()
    test.readFile("06.pcap")
    len(test.layer1)
    test.readView()
    #testingChannelsCartesian(test)
    testingChannelsCylindrical(test,1,4)
    
    
    
    
    print("Bye World")
    #file_in = "C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\example.pcap"
    #file_out = "C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\example.txt"
    #file_cal = "C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\cal.json"
    #script="C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\velodyneLibZimpha\\Velodyne_16"
    #os.system('python C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\velodyneLib\\read_cal.py '+file_in+' '+file_out)
    #os.system('python C:\\Users\\kenneth\\Documents\\NetBeansProjects\\Velodyne16\\velodyneLib\\read_points.py '+file_in+' '+file_out+' '+file_cal)
    #print("end")
    
