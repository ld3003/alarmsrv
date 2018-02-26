#coding=utf-8

import socket
import threading
import SocketServer
import time
import datetime
import binascii

import thread
import json
import recvimg
import global_vals
import requestLoc
import uuid
import os
import sys
import traceback
import logging
import log


#from ipdb import
#set_trace set_trace()

reload(sys) # Python2.5 初始化后删除了 sys.setdefaultencoding 方法，我们需要重新载入 
sys.setdefaultencoding('utf-8')

cmd_func = dict()

class MyUDPHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            data = self.request[0]
            socket = self.request[1]

            logging.info('UDP RECV PKG:' + binascii.b2a_hex(data))
            pkg = (socket,self.client_address,data)
            process_udppkg(pkg)
        except Exception, e:
                logging.warn(traceback.format_exc())
            
 

class ThreadedUDPServer(SocketServer.ThreadingMixIn, SocketServer.UDPServer):
    pass

def process1091(pkg):
    pass
def process2091(pkg):
    pass

def process_udppkg(pkg):
    socket = pkg[0]
    address = pkg[1]
    data = pkg[2];
    
    wechat_item = dict()
    wechat_item_body = dict()
    
    pkg = recvimg.PkgParser(data)

    #如果解析成功
    if (pkg.RESULT == True):

        logging.info('pkg parser success')

        respdata = pkg.getResp()
        logging.info('UDP SEND PKG:' + binascii.b2a_hex(respdata))
        socket.sendto(pkg.getResp(),address)
        
        if (pkg.MSG_CMD == 0x1092):
        
            if recvimg.DEVICE_IMGCACHE_DICT.has_key(pkg.DEVID):
                #print '当前设备设备已经存在'
                pass
            else:
                logging.info('INSERT TO CACHE')
                cache = recvimg.imageCache(pkg.DEVID)
                recvimg.DEVICE_IMGCACHE_DICT[pkg.DEVID] = cache
                pass
            result = recvimg.DEVICE_IMGCACHE_DICT[pkg.DEVID].setData(pkg)
            
            
            
            if (result == True):
                
                #print 'IMGDATA:' + binascii.b2a_hex(recvimg.DEVICE_IMGCACHE_DICT[pkg.DEVID].DATA)
                imgname = save_img(pkg.DEVID,recvimg.DEVICE_IMGCACHE_DICT[pkg.DEVID].DATA)
                recvimg.DEVICE_IMGCACHE_DICT[pkg.DEVID].resetCache()
                
                wechat_item_body['IMGNAME'] = imgname
                
                wechat_item['DEVID'] = pkg.DEVID
                wechat_item['TYPE'] = global_vals.PKG_TYPE_PHOTO
                wechat_item['BODY'] = wechat_item_body
                
                global_vals.WECHAT_PUSH_QUEUE.put_nowait(wechat_item)
                print 'WeChatPush  --> Queue : ' + str(global_vals.WECHAT_PUSH_QUEUE.qsize())
        
        
        if (pkg.MSG_CMD == 0x10A0):
            logging.info('alarm type 0x10A0')
            
            item = dict()
            body = dict()

            alarmData = pkg.getAlarmData()
            
            alarmtype = alarmData[0]
            gsmlac = alarmData[3];
            gsmci = alarmData[4];
            
            #item = [pkg.DEVID, global_vals.WECHAT_MSG_ALARM,[alarmtype,'',gsmlac,gsmci]]  #id,type,body[alarmtype,alarmstr,lac,ci]
            
            body['ALARMTYE'] = alarmtype
            body['ALARMSTR'] = ''
            body['LAC'] = gsmlac
            body['CI'] = gsmci

            item['DEVID'] = pkg.DEVID
            item['TYPE'] = global_vals.PKG_TYPE_ALARM
            item['BODY'] = body
                           
            global_vals.WECHAT_PUSH_QUEUE.put_nowait(item)
            print 'WeChatPush  --> Queue : ' + str(global_vals.WECHAT_PUSH_QUEUE.qsize())
            
        if (pkg.MSG_CMD == 0x10A1):
            logging.info('alarm type 0x10A1')
            # MAC ADDRESS
            # CELL INFO
            
            pass;
            
    else:
        logging.warn( 'parser data error!')

def process_wechat_push(Q):
    while True:
        try:
            item = Q.get()
            print 'INFO : ' + str(item)
	except:
            print ''
    pass

def save_img(devid,data):
    imgpath = global_vals.IMGPATH + devid + '/'
    if (os.path.exists(imgpath) != True):
        os.makedirs(imgpath)
    imgname = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
    filename = imgpath + imgname + '.jpg'
    imgfile = open(filename,'wb')
    imgfile.write(data)
    imgfile.close()
    logging.info('SAVE IMG TO: ' + filename)
    return imgname + '.jpg'
    
        
if __name__ == "__main__":

    log.settinglog()
        
    logging.info('SRV START ' + __file__)

    #print database.get_userdevice_info('opP9Sv8ImKryDRGTA5Mg6UDVZRBY','862991528784447f')['NAME']

    server = ThreadedUDPServer((global_vals.HOST, global_vals.PORT), MyUDPHandler)
    server_thread = threading.Thread(target=server.serve_forever)
    
    server_thread.daemon = True
    server_thread.start()
    
    process_wechatpush_thread = threading.Thread(target=process_wechat_push,args=(global_vals.WECHAT_PUSH_QUEUE,))
    process_wechatpush_thread.setDaemon(True)
    process_wechatpush_thread.start()

  
    while True:
        #print ( 'RUNNING ' + datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        time.sleep(2)
