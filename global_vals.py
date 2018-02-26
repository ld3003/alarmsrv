#coding=utf-8

import Queue

HOST, PORT = '172.17.180.57', 29102

MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = '3306'
MYSQL_USER = 'root'
MYSQL_PWD = ''
MYSQL_DB = 'IOT'

LOGFILE_PATH = './iot.log'
IMGPATH = '/home/wwwroot/default/IMGDATA/'

WECHAT_APPID = ''
WECHAT_SECRET = ''
WECHAT_TEMPLET = ''



UDP_PKG_QUEUE = Queue.Queue(maxsize = 1024)
WECHAT_PUSH_QUEUE = Queue.Queue(maxsize = 1024)
WECHAT_PKG_QUQUE = Queue.Queue(maxsize = 128)


#CONST VALUE

ALARM_TYPE_YIDONG       = 0
ALARM_TYPE_JINGZHI      = 1

PKG_TYPE_PHOTO          = 0
PKG_TYPE_ALARM          = 1
