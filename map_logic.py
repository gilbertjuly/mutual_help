# -*- coding: UTF-8 -*-
import math

def GetDistance( lng1,  lat1,  lng2,  lat2):
    '''
        from http://only-u.appspot.com/?p=36001 method#4
    '''
    EARTH_RADIUS = 6378.137 # 地球周长/2*pi 此处地球周长取40075.02km pi=3.1415929134165665
    from math import asin,sin,cos,acos,radians, degrees,pow,sqrt, hypot,pi

    d=acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng1-lng2))+sin(radians(lat1))*sin(radians(lat2)))*EARTH_RADIUS*1000
    return d




