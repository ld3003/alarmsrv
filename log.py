#coding=utf-8
import logging
import global_vals

def settinglog():

    LOG_DATE_FORMAT = '%b %d %H:%M:%S'
    LOG_FORMAT = '%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s'
    LOG_LEVEL = logging.DEBUG
    LOG_FILE = global_vals.LOGFILE_PATH


    logger = logging.getLogger()

    fileLogger = logging.FileHandler(LOG_FILE)
    fileLogger.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

    streamLogger = logging.StreamHandler()
    streamLogger.setFormatter(logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT))

    logger.addHandler(fileLogger)
    logger.addHandler(streamLogger)
    logger.setLevel(LOG_LEVEL)
    
 
    
if __name__ == "__main__":
    settinglog()
    print __file__
