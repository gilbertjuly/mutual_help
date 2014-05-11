#-*- coding:utf-8 -*-

#tornado web site
 
import os
import sys
import urllib
import math
import time
import string

import tornado.wsgi
import tornado.httpserver
import tornado.ioloop
import tornado.web
from tornado.httpclient import HTTPClient
from tornado.escape import json_encode, json_decode

import map_logic
from define import *
from user_logic import * 
from help_logic import * 


###############################################################################
###############################################################################
###############################################################################
#todo:


#################################################################################
############################# Golbal data #######################################
#################################################################################



#################################################################################
############################# Functions   #######################################
#################################################################################
def GetDistance( lng1,  lat1,  lng2,  lat2):
    '''
        from http://only-u.appspot.com/?p=36001 method#4
    '''
    EARTH_RADIUS = 6378.137 # 地球周长/2*pi 此处地球周长取40075.02km pi=3.1415929134165665
    from math import asin,sin,cos,acos,radians, degrees,pow,sqrt, hypot,pi

    d=acos(cos(radians(lat1))*cos(radians(lat2))*cos(radians(lng1-lng2))+sin(radians(lat1))*sin(radians(lat2)))*EARTH_RADIUS*1000
    return d


def test_mongo():
    ### 开发者可在requirements.txt中指定依赖pymongo使用
    import pymongo
 
    ### 连接MongoDB服务
    ### 请在管理控制台获取host, port, db_name, api_key, secret_key的值
    con = pymongo.Connection(host = "mongo.duapp.com", port = 8908)  
    db_name = "AXuAgnJLApkefuWllnSG"
    db = con[db_name]
    api_key = "IXj5gFpzufduRv3BnG9i255H"
    secret_key = "yFmYQhLyItkE6i54CPRXBiQKkcOZa1UP"
    db.authenticate(api_key, secret_key)
 
    ### 插入数据到集合test
    collection_name = 'test'
    db[collection_name].insert({"id":10, 'value':"test test"})
 
    ### 查询集合test
    cursor = db[collection_name].find()
    con.disconnect()
    return "select collection test %s"%str(cursor[0])
	

def test_mymongo():
    import db_driver
    db = db_driver.DB('test')
    db.SelectTable('test')
    db.Insert({"id":10, 'value':"test test"})
    cursor = db.Find()
    return "select collection test %s"%str(cursor[0])


#################################################################################
############################# Classes   #########################################
#################################################################################
class RootHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("This is a BAE project: hostname: %s; platform %s;\
                Try to load \"mutualhelp.buapp.com\\test_where\"" % (socket.gethostname(), platform.platform()))

    def post(self):
        self.write("got the post")


class WhereHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/where_are_you.html")


class LocationHandler(tornado.web.RequestHandler):
    def post(self):
        global jiayan_baidu_key, jiayan_latitude, jiayan_longitude, baidu_shanghai_map
        street = self.get_argument("street")
        city = self.get_argument("city")
        street = street.encode("UTF-8")
        city = city.encode("UTF-8")
        street_string = urllib.quote(street)
        city_string = urllib.quote(city)
#       *TBD*, maybe can be replaced by tornado.escape.utf8.
#        self.GeoLocation_request(street_string, city_string)  ##the async method
        key = urllib.quote(jiayan_baidu_key)
        simple_client = HTTPClient()
        response = simple_client.fetch("http://api.map.baidu.com/geocoder/v2/?ak=%s&output=json&address=%s&city=%s" % (key, street, city))
        if  response.error:
            raise  tornado.web.HTTPError(500)
        location_json  =  tornado.escape.json_decode(response.body)
        if location_json['status'] == 0:
            try:
                ### this offset is added to fix people square can't display correctly, I think it's baidu's problem. ###
                location_json['result']['location']['lng'] = location_json['result']['location']['lng'] + 0.000001
#               print  location_json['result']['location']['lng'], location_json['result']['location']['lat']
                distance = GetDistance(float(jiayan_longitude), float(jiayan_latitude),\
                    float(location_json['result']['location']['lng']), float(location_json['result']['location']['lat']))
#               map_link = baidu_shanghai_map + "&labels=%s,%s&labelStyles=MARK,1,14,0xffffff,0xff0000,1" % \
#                        (location_json['result']['location']['lng'], location_json['result']['location']['lat'])
                map_link = baidu_shanghai_map + "&markers=%s,%s|%s,%s&marklStyles=s,A,0xff0000" % \
                        (location_json['result']['location']['lng'], location_json['result']['location']['lat'], \
                        jiayan_longitude, jiayan_latitude)
                self.render("static/map_static.html", 
                    latitude = location_json['result']['location']['lat'], \
                    longitude = location_json['result']['location']['lng'],\
                    map_img = map_link,\
                    distance = "%.2f" % distance,)
            except:
                self.write("<html><body><h2>Oops! Somthing Wrong! Havn't find your location!</h2></body><html>\n")
        else:
            self.write("<html><body><h2>Havn't find your location!</h2></body><html>\n")


class MutualHandler(tornado.web.RequestHandler):
    def get(self):
        log_print('get the get')
        try:
            self.write('%s' % test_mymongo())
            #self.write('get the get')
        except:
            self.write('mongo test failed')
        #pass

    def post(self):
        pass


class AppHandler(tornado.web.RequestHandler):
#   self.request.remote_ip is the client's IP address
    def get(self):
        self.write("Mutual Server: HTTP GET is ok!\r\n")

    def post(self):
        msg_req = self.get_argument("PAYLOAD")
        msg_req = json_decode(msg_req)
        msg_type = msg_req["TYPE"]
        if msg_type == MSG_USER_REGISTER_REQ:
            msg_resp = UserRegisterAction(msg_req)
        elif msg_type == MSG_USER_LOGIN_REQ:
            msg_resp = UserLoginAction(msg_req)
        elif msg_type == MSG_USER_LOGOUT_REQ:
            msg_resp = UserLogoutAction(msg_req)
        elif msg_type == MSG_USER_INFO_REQ:
            msg_resp = UserInfoAction(msg_req)
        elif msg_type == MSG_USER_POLLING_REQ:
            msg_resp = UserPollingAction(msg_req)
        elif msg_type == MSG_USER_REPORT_REQ:
            msg_resp = UserReportAction(msg_req)
        elif msg_type == MSG_HELP_ADD_REQ:
            msg_resp = HelpAddAction(msg_req)
        elif msg_type == MSG_HELP_INFO_REQ:
            msg_resp = HelpInfoAction(msg_req)
        elif msg_type == MSG_HELP_ACCEPT_REQ:
            msg_resp = HelpAcceptAction(msg_req)
        elif msg_type == MSG_HELP_REJECT_REQ:
            msg_resp = HelpRejectAction(msg_req)
        elif msg_type == MSG_HELP_FINISH_REQ:
            msg_resp = HelpFinishAction(msg_req)
        else:
            msg_resp = {"reason":"this msg type is unsupported yet!\r\n"}
        self.write(json_encode(msg_resp))


class TestUserRegHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_register_db.html")

    def post(self):
        name = self.get_argument("NAME")
        tel = self.get_argument("TEL")
        sex = self.get_argument("SEX")
        age = self.get_argument("AGE")
        job = self.get_argument("JOB")
        nickname = self.get_argument("NICKNAME")
        email = self.get_argument("EMAIL")
        longitude = self.get_argument("LONGITUDE")
        latitude = self.get_argument("LATITUDE")
        address = self.get_argument("ADDRESS")
        icon_index = self.get_argument("ICON_INDEX")
        icon = self.get_argument("ICON")
        passwd = self.get_argument("PASSWD")
        msg_req = {u"TYPE":MSG_USER_REGISTER_REQ ,u"NAME":name, u"TEL":tel, u"SEX":sex, \
                u"AGE":age, u"JOB":job, u"PASSWD":passwd, u"NICKNAME":nickname, u"EMAIL":email,\
                u"LONGITUDE":longitude, u"LATITUDE":latitude, u"ADDRESS":address, \
                u"ICON_INDEX":icon_index, u"ICON":icon,}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = UserRegisterAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserLoginHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_login_db.html")

    def post(self):
        tel = self.get_argument("TEL")
        passwd = self.get_argument("PASSWD")
        msg_req = {u"TYPE":MSG_USER_LOGIN_REQ, u"TEL":tel, u"PASSWD":passwd}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req) 
        msg_req = json_decode(msg_req)
        msg_resp = UserLoginAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserLogoutHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_logout_db.html")

    def post(self):
        tel = self.get_argument("TEL")
        msg_req = {u"TYPE":MSG_USER_LOGOUT_REQ ,u"TEL":tel}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = UserLogoutAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserInfoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_info_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        msg_req = {u"TYPE":MSG_USER_INFO_REQ ,u"USERID":userid}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = UserInfoAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserPollingHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_polling_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        update_item = string.atoi(self.get_argument("UPDATE_ITEM"))
        msg_req = {u"TYPE":MSG_USER_POLLING_REQ, u"USERID":userid, u"UPDATE":update_item}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = UserPollingAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserReportHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_report_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        lat = int(self.get_argument("LATITUDE"))
        lon = int(self.get_argument("LONGITUDE"))
        msg_req = {u"TYPE":MSG_USER_REPORT_REQ, u"USERID":userid, u"UPDATE":REPORT_USER_LOCATION,
                    u"LATITUDE":lat, u"LONGITUDE":lon}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = UserReportAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestUserDistanceHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/user_distance.html")

    def post(self):
        userid1 = self.get_argument("USERID1")
        userid2 = self.get_argument("USERID2")
        msg_req = {u"USERID1":userid1, u"USERID2":userid2}
        #msg_req = json_encode(msg_req)
        #self.write("<br>\r\nclient msg:\r\n<br>")
        #self.write(msg_req)
        #msg_req = json_decode(msg_req)
        msg_resp = UsersGetDistanceAction(userid1, userid2)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestHelpAddHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/help_add_db.html")

    def post(self):
        title = self.get_argument("TITLE")
        userid = self.get_argument("USERID")
        catagory = self.get_argument("CATAGORY")
        place = self.get_argument("RANGE")
        timeout = self.get_argument("TIMEOUT")
        content = self.get_argument("CONTENT")
        lat = self.get_argument("LATITUDE")
        lon = self.get_argument("LONGITUDE")
        address = self.get_argument("ADDRESS")
        start_time = self.get_argument("START_TIME")
        score = int(self.get_argument("SCORE"))
        phone = self.get_argument("PHONE")
        msg_req = {u"TYPE":MSG_HELP_ADD_REQ, u"TITLE":title, u"USERID":userid, u"CATAGORY":catagory,\
                u"LATITUDE":lat, u"LONGITUDE":lon, u"RANGE":place, u"TIMEOUT":timeout, u"CONTENT":content,
                u"ADDRESS":address, u"START_TIME":start_time, u"SCORE": score, u"PHONE": phone}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = HelpAddAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestHelpAcceptHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/help_accept_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        helpid = self.get_argument("HELPID")
        msg_req = {u"TYPE":MSG_HELP_ACCEPT_REQ, u"USERID":userid, u"HELPID":helpid}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = HelpAcceptAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestHelpRejectHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/help_reject_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        helpid = self.get_argument("HELPID")
        msg_req = {u"TYPE":MSG_HELP_REJECT_REQ, u"USERID":userid, u"HELPID":helpid}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = HelpRejectAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestHelpFinishHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/help_finish_db.html")

    def post(self):
        userid = self.get_argument("USERID")
        helpid = self.get_argument("HELPID")
        finished_helpers = []
        finished_helpers.append({"FINISHER_ID": self.get_argument("finisher1_id"), 
                                "FINISHER_SCORE": int(self.get_argument("finisher1_score"))})
        finished_helpers.append({"FINISHER_ID": self.get_argument("finisher2_id"), 
                                "FINISHER_SCORE": int(self.get_argument("finisher2_score"))})
        msg_req = {u"TYPE":MSG_HELP_FINISH_REQ, u"USERID":userid, u"HELPID":helpid, u"FINISHED_HELPERS":finished_helpers}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = HelpFinishAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))


class TestHelpInfoHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("static/help_info_db.html")

    def post(self):
        helpid = self.get_argument("HELPID")
        msg_req = {u"TYPE":MSG_HELP_INFO_REQ ,u"HELPID":helpid}
        msg_req = json_encode(msg_req)
        self.write("<br>\r\nclient msg:\r\n<br>")
        self.write(msg_req)
        msg_req = json_decode(msg_req)
        msg_resp = HelpInfoAction(msg_req)
        self.write("<br>\r\nserver msg:\r\n<br>")
        self.write(json_encode(msg_resp))




#################################################################################
############################# Main Entry   ######################################
################################################################################# 
settings = {
        'debug' : True,
        "static_path": os.path.join(os.path.dirname(__file__), "static"),
    }

url_handlers = [
        (r"/", RootHandler),
        (r"/app", AppHandler),
	    (r"/mutual", MutualHandler),
	    (r"/test_where", WhereHandler),        # a self-test for handler
	    (r"/test_location", LocationHandler),  # a self-test for handler
        (r"/test_user_register", TestUserRegHandler),
        (r"/test_user_login", TestUserLoginHandler),
        (r"/test_user_logout", TestUserLogoutHandler),
        (r"/test_user_info", TestUserInfoHandler),
        (r"/test_user_polling", TestUserPollingHandler),
        (r"/test_user_report", TestUserReportHandler),
        (r"/test_user_distance", TestUserDistanceHandler),
        (r"/test_help_add", TestHelpAddHandler),
        (r"/test_help_accept", TestHelpAcceptHandler),
        (r"/test_help_reject", TestHelpRejectHandler),
        (r"/test_help_finish", TestHelpFinishHandler),
        (r"/test_help_info", TestHelpInfoHandler),
    ]

log_print('starting...')


if UserDBInit(UserDBName, UserDBTable) == STATUS_FAIL:
    log_print('failed to init user db')
    sys.exit()
if HelpDBInit(HelpDBName, HelpDBTable) == STATUS_FAIL:
    log_print('failed to init help db')
    sys.exit()

if IS_BAE == True:
    app = tornado.wsgi.WSGIApplication(url_handlers,**settings) 
    from bae.core.wsgi import WSGIApplication
    application = WSGIApplication(app)
else:
    class Application(tornado.web.Application):
        def __init__(self):
            tornado.web.Application.__init__(self, url_handlers, **settings)

    from tornado.options import define, options
    define("port", default=8008, help="run on the given port", type=int)

    if __name__ == "__main__":
        tornado.options.parse_command_line()
        http_server = tornado.httpserver.HTTPServer(Application())
        http_server.listen(options.port)
        log_print('tornado server listening at %d' % options.port)
        tornado.ioloop.IOLoop.instance().start()




