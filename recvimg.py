#coding=utf-8

import socket
import threading
import SocketServer
import time
import Queue
import thread
import json

import struct
import binascii
import uuid
import datetime
import os
import random  
import time


from io import BytesIO

DEVICE_IMGCACHE_DICT = dict()


class PkgParser:
    def __init__(self,data):
    
        self.MSG_CMD = 0
        self.MSG_ID = 0
        self.MSG_COUNT = 0
        self.MSG_SEQ = 0
        self.MSG_LEN = 0
        self.MSG_SUM = 0
        
        self.DEVID = ''
        self.DEVID_CODE = ''
        self.MSG_BODY = ''
        
        self.LAT = 0.0
        self.LON = 0.0
        
        self.LACID = 0
        self.CELLID = 0
        
        self.RESULT = False
        
        data_length = len(data)
        
        if (len >= 26):
        
            fmt = '!HHHHHHHHH8s'
            
            #rawdatalen = len - 26
            fmt = fmt+str(data_length-26)+'s'

            print fmt
            
            res = struct.unpack(fmt,data)

            #print res
            #print binascii.b2a_hex(res[9])
            
            self.MSG_CMD = res[0]
            self.MSG_ID = res[4]
            self.MSG_COUNT = res[5]
            self.MSG_SEQ = res[6]
            self.MSG_SUM = res[7]
            self.DEVID = binascii.b2a_hex(res[9])
            self.DEVID_CODE = res[9]
            self.MSG_BODY = res[10]
            
            if(self.MSG_SUM == self.uchar_checksum(self.MSG_BODY)):
                print 'CHECK SUM SUCCESS'
                self.RESULT = True
            else:
                print 'CHECK SUM ERROR'
                self.RESULT = False
            
    def uchar_checksum(self,data,byteorder='little'):
    
        data_length = len(data)
        checksum = 0

        for i in range(0, data_length):  
            checksum = checksum + ord(data[i])
        checksum &= 0xFFFF
        return checksum
        
    def getImgData(self):
        data_length = len(self.MSG_BODY)
        
        if (data_length > 5):
             fmt = '5s'
             fmt = fmt + str(data_length-5) + 's'
             
             res = struct.unpack(fmt,self.MSG_BODY)
             return res[1]
             
    def getAlarmData(self):
        data_length = len(self.MSG_BODY)
        if (data_length == 18):
            fmt = '!HIIII'
            res = struct.unpack(fmt,self.MSG_BODY)
            return res
        pass
        
    def parser_attach_data(self,data):
 
        f = BytesIO()
        f.write(data);
        f.seek(0)
        
        parser_result = dict()
        
        while True :
        
            attachid = 0
            attachlen = 0
            attachdata = ''
        
            #读取并解析ID
            tmpbuf = f.read(2)
            if (len(tmpbuf) < 2):
                break
            format = '!H'
            res = struct.unpack(format,tmpbuf)
            print 'ATTACH ID: ' + str(res[0])
            attachid = res[0];

            tmpbuf = f.read(2)
            if (len(tmpbuf) < 2):
                break
            format = '!H'
            res = struct.unpack(format,tmpbuf)
            print 'ATTACH LEN ' + str(res[0])
            attachlen = res[0]
            if (res[0] <= 4):
                break
            
            tmpbuf = f.read(attachlen - 4)
            if (len(tmpbuf) < (attachlen -4)):
                break
            print 'ATTACH LEN ' + str(len(tmpbuf))
            attachdata = tmpbuf;
            
            print 'SUCCESS PARSE ATTACH DATA'
            
            parser_result[attachid] = attachdata
            
        return parser_result
        
    def make2091(self):
    
        print '1091 BODY ' + binascii.b2a_hex(self.MSG_BODY)
        print '1091 BODY len ' + str(len(self.MSG_BODY))
        #read vol
        if len(self.MSG_BODY) >= 5 :
            fmt = '!HBH' + str(len(self.MSG_BODY)-5) + 'x'
            res = struct.unpack(fmt,self.MSG_BODY)
            print 'DIANYA :' + str(res[0])
            print 'XINHAO :' + str(res[1])
        
        
        curtim = time.localtime(time.time())
        tim1 = datetime.datetime(curtim[0], curtim[1], curtim[2], curtim[3], curtim[4], curtim[5], 0)
        #tim2 = datetime.datetime(curtim[0], curtim[1], curtim[2], dev['TAKE_PHOTO_TIM'], 00, 00, 0)

        
        #每4个小时拍照一次
        sec =  3600*4
    
        tim1 = sec
        tim2 = tim1 + 60
        sum = 0
        respid = 0x2091
        
        bodydata = struct.pack('!HIIHHBBHBH12x',0,tim1,tim2,0,0,0,0,0,0,0)
        sum = self.uchar_checksum(bodydata)
        hdrdata = struct.pack('!HHHHHHHHH8s',respid,0,0,len(bodydata) + 26,self.MSG_ID,0,0,sum,0,self.DEVID_CODE)
        #respdata = struct.pack('!HHHHHHHHH8sHIIHHBBHBH12x',respid,0,0,0,self.MSG_ID,0,0,0,0,self.DEVID_CODE,0,0,0,0,0,0,0,0,0,0)
        respdata = hdrdata + bodydata
        return respdata
        
    def getResp(self):
    
        respdata = ''
    
        if self.MSG_CMD == 0x1092:
            respid = 0x2092
            respdata = struct.pack('!HHHHHHHHH8s',respid,0,0,0,self.MSG_ID,1,self.MSG_SEQ,0,0,self.DEVID_CODE)
        if self.MSG_CMD == 0x1091:
            return self.make2091()
        if self.MSG_CMD == 0x10A0:
            respid = 0x20A0
            respdata = struct.pack('!HHHHHHHHH8s',respid,0,0,0,self.MSG_ID,0,0,0,0,self.DEVID_CODE)

        print binascii.b2a_hex(respdata)
        return respdata
        pass


class imageCache:
    def __init__(self,DEVID):
        self.DEVID = DEVID
        self.resetCache()
        self.DATA = ''
        
    def resetCache(self):
        self.MSG_ID = 0
        self.MSG_COUNT = 0
        self.TIMP = 0
        self.PKG_DICT = dict()
        self.DATA = ''
        
    def setData(self,pkg):
    
        retcode = 0
        retbody = ''
        if pkg.MSG_CMD == 0x1092:
        
            if self.MSG_ID != pkg.MSG_ID:
                self.resetCache()
                self.MSG_ID = pkg.MSG_ID
                self.MSG_COUNT = pkg.MSG_COUNT
                
                
            print 'SET DATA INFO :'
            print 'pkg.MSG_COUNT : ' + str(pkg.MSG_COUNT)
            print 'pkg.MSG_SEQ : ' + str(pkg.MSG_SEQ)
            print 'pkg.MSG_ID : ' + str(pkg.MSG_ID)

            self.PKG_DICT[pkg.MSG_SEQ-1] = pkg.getImgData()

            if len(self.PKG_DICT) == self.MSG_COUNT :
            
                if self.DEVID[0:12] == 'ffffffffffff' :
                    pass
                else:
                    for i in range(self.MSG_COUNT):
                        self.DATA = self.DATA + self.PKG_DICT[i]
                    return True
            pass
            
        else:
            self.resetCache()
        
        return False

        
 
if __name__ == "__main__":
    data = '\x10\x92\x00\x00\x00\x00\x02\x1F\x00\x02\x00\x0C\x00\x0B\xAE\x75\x10\x91\x86\x55\x33\x03\x00\x02\x45\x9F\x00'
    '''
    \x00\x00\x64\x01\xB9\xAA\xF8\xE0\x50\x6B\x23\xA0\x53\x4F\xAD\xCF\x30\x8C\x0D\xAC\x0F\xFB\x55\xAC\xBD\x29\x14\xC7\x8E\xB5\x20\xA6\x34\x48\xA6\x9F\xBB\xE6\x14\x8A\x27\x0D\x52\x03\x48\x63\xC3\x53\xC3\x50\x50\xED\xD4\xED\xD4\x86\x01\xB8\xA3\x75\x21\x82\xB7\x14\x6E\xA4\x03\x09\xA7\x66\x81\x8D\xCD\x37\x34\x80\x82\xE4\xFE\xEF\xF1\xA9\x49\xA0\x08\x9C\xF1\x48\x0D\x20\x1A\x4D\x46\x4D\x02\x18\x4D\x30\x9A\x00'
    '''
    
    curtim = time.localtime(time.time())
    tim1 = datetime.datetime(curtim[0], curtim[1], curtim[2], curtim[3], curtim[4], curtim[5], 0)
    tim2 = datetime.datetime(curtim[0], curtim[1], curtim[2], 20, 00, 00, 0)
    print (tim2 - tim1).seconds
    
    #print (datetime.datetime(tim2) - datetime.datetime(tim1)).seconds
    
    print tim2 - tim1
    
    #print datetime.datetime.now()
    
    p = PkgParser(data)
    print p.RESULT 
    print len(p.MSG_BODY)
    print p.uchar_checksum(data)
    #p.parser(data)
    
    tstrawdata = '\x00\x01\x00\x08\x00\x00\x00\x01\x00\x02\x00\x08\x00\x00\x00\x02'
    f = BytesIO()
    f.write(tstrawdata);
    f.seek(0)
    
    curtim = time.localtime(time.time())
    tim1 = datetime.datetime(curtim[0], curtim[1], curtim[2], curtim[3], curtim[4], curtim[5], 0)
    tim2 = datetime.datetime(curtim[0], curtim[1], curtim[2], 6, 00, 00, 0)
    sec =  (tim2 - tim1).seconds
    
    print 'TIM == ' + str(sec)

    
 
