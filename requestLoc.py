#coding=utf-8

import urllib,urllib2,json

def getLocInfo(cell,lac):

    lbs_token = 'a5dd3d2e51e6a49fe25a76cc997f8e6d'
    #url='http://v.juhe.cn/cell/get?mnc=0&cell=%s&lac=%s&key=9139e1948d19a83ecf2102adcb848264'%(cell,lac)
    url = 'http://api.cellocation.com:81/cell/?mcc=460&mnc=1&lac=%s&ci=%s&output=json'%(lac,cell)

    '''
    url = 'http://api.cellocation.com:81/cell/?mcc=460&mnc=1&lac=%s&ci=%s&output=json'%(lac,cell)
	address = locinfo['result']['data'][0]['ADDRESS']
	loclng = locinfo['result']['data'][0]['LNG']
	loclat = locinfo['result']['data'][0]['LAT']

    '''
    print url
    res = urllib2.urlopen(url)
    res = res.read()

    json_data = json.loads(res)
    print json_data
    #print json_data['result']['data'][0]['ADDRESS']
    #print json_data['result']['data'][0]['ADDRESS']

    #http://uri.amap.com/marker?position=116.473195,39.993253

    res2 = dict()

    '''
    res2['ADDRESS'] = json_data['result']['data'][0]['ADDRESS']
    res2['LNG'] = json_data['result']['data'][0]['LNG']
    res2['LAT'] = json_data['result']['data'][0]['LAT']
    '''

    res2['ADDRESS'] = json_data['address']
    res2['LNG'] = json_data['lon']
    res2['LAT'] = json_data['lat']
    
    return res2

    
if __name__ == "__main__":
    print getLocInfo(28655,17695)
