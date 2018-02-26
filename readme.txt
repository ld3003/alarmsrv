这是一个能够接受报警信息和图片的服务端软件，能够支持跨平台应用

使用方式：

windows:

1,安装python2.7
2,双击运行main.py


linux:

1,安装python2.7
2,用命令行执行 python main.py


配置方法:

打开global_vals.py文件

修改为本地主机的ip地址和端口号
HOST, PORT = '172.17.180.57', 29102

设置日志文件保存目录
LOGFILE_PATH = './iot.log'

设置接收到的图片信息目录
IMGPATH = '/home/wwwroot/default/IMGDATA/'


