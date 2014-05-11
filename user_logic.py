# -*- coding: UTF-8 -*-

#import pymongo
import db_driver
import help_logic
import map_logic

from tornado.escape import json_encode, json_decode
from bson import ObjectId
from bson.json_util import dumps
from define import *
#from help_logic import HelpSimpleInfo 

DB_User = None


#####################
# todo list
# 1. level, rank
# 2. index as avator
#####################

###################################################################
########################## Low Level ##############################
###################################################################
def UserDBInit(DB_name, DB_table):
    global DB_User
    DB_User = db_driver.DB(DB_name)
    if DB_User:
        DB_User.SelectTable(DB_table)
        log_print("User DB initialzation ok! %s, %s" % (DB_User.DataBase, DB_User.Table))
        return STATUS_SUCCESS
    else:
        log_print("User DB initialzation error!")
        return STATUS_FAIL


def UserGetId(user_entry):
    UID = dumps(user_entry['_id'])
    ### After inserted to DB, user_entry has one more member called "_id" ###
    ### UID is a string, something like "{"$oid": "5250441015808c14102afcd6"}", cut it off ###
    UID = UID[10:-2]
    return UID


def UserFindOne(key, val):
    global DB_User
    user_entry = DB_User.FindOne(key, val)
    return user_entry


def UserFindById(userid):
    global DB_User
    user_entry = DB_User.FindOne('_id', ObjectId(userid))
    return user_entry


def UserFindAll():
    global DB_User
    return DB_User.Find()


def UserInsert(user_entry):
#    userid = DB_User.Insert(user_entry)
    DB_User.Insert(user_entry)
    UID = UserGetId(user_entry)
    user_entry['USERID'] = UID
    UserUpdate(user_entry)
    return UID


def UserUpdate(user_entry):
    DB_User.Update(user_entry)
    UID = user_entry['USERID']
    return UID


def UserTotalCount():
    global DB_User
    return DB_User.Count()


def UserSimpleInfo(userid):
    user_entry = UserFindById(userid)
    user_simple_info = {'USERID':user_entry['USERID'], 'NICKNAME':user_entry['NICKNAME'], 
                        'ICON_INDEX':user_entry['ICON_INDEX'], 'ICON':user_entry['ICON'], 
                        'SCORE':user_entry['SCORE'], 'LEVEL':user_entry['LEVEL'], 'DISTANCE':0}
    return user_simple_info


def UsersGetDistance(userid1, userid2):
    user1_entry = UserFindById(userid1)
    user2_entry = UserFindById(userid2)
    update_item = REPORT_USER_DISTANCE
    distance = map_logic.GetDistance(user1_entry['LONGITUDE'], user1_entry['LATITUDE'], 
                                    user2_entry['LONGITUDE'], user2_entry['LATITUDE']) 
    return distance


def UserGetFinishHelpScore(userid, helpid):
    user_entry = UserFindById(userid)
    for help_ext_entry in user_entry['HELP_FINISH_LIST_EXT']:
        if help_ext_entry['HELP_ID'] == helpid:
            return help_ext_entry['HELP_SCORE']
    return 0



###################################################################
######################### HIGH Level ##############################
###################################################################
def UserRegisterAction(msg_req):
    user_entry = None
#    msg_req = json_decode(msg_req)
    name = msg_req['NAME']
    nickname = msg_req['NICKNAME']
    tel = msg_req['TEL']
    sex = msg_req['SEX']
    age = msg_req['AGE']
    job = msg_req['JOB']
    passwd = msg_req['PASSWD']
    email = msg_req['EMAIL']
    latitude = msg_req['LATITUDE']
    longitude = msg_req['LONGITUDE']
    address = msg_req['ADDRESS']
    icon_index = msg_req['ICON_INDEX']
    icon = msg_req['ICON']
    user_entry = UserFindOne('TEL', tel)
    if user_entry:
        msg_resp = {'TYPE':MSG_USER_REGISTER_RESP, 'STATUS':STATUS_FAIL, \
                    'REASON':'someone has registered by this phone!'}
    else:
        user_idx = UserTotalCount() + 1
        icon_index = user_idx
        user_entry = {
                        'NAME':name, 'NICKNAME':name, 'PASSWD':passwd, \
                        'TEL':tel, 'AGE':age, 'SEX':sex, 'JOB':job, \
                        'LATITUDE':0, 'LONGITUDE':0, 'ADDRESS':address, \
                        'INDEX': user_idx,\
                        'ICON':0, 'ICON_INDEX':icon_index, \
                        'USERID':0, \
                        'RANK': 0, 'LEVEL':0, 'SCORE':100, \
                        'LOG':LOG_OUT, \
                        'ACTION':HELP_NONE, \
                        'HELP_ME_LIST':[], \
                        'HELP_ACCEPT_LIST':[], \
                        'HELP_REJECT_LIST':[], \
                        'HELP_FINISH_LIST':[], \
                        'HELP_FINISH_LIST_EXT':[], \
                        'HELP_UNFINISH_LIST':[], \
                        'HELP_CANDO_LIST':[], \
                        'ACCEPT':0, 'REJECT':0, 'FINISH':0, \
                        'HAS_UPDATE': UPDATE_NONE, \
                        ### In fact, there is still an "_id" key created by mongodb ###
                        # RANK  -- rank is the rank, compared with other people
                        # LEVEL -- level is the level, they both calcualted based on SCORE.
                    }
        #TBD, add try...catch, maybe should put try in db_drvier
        userid = UserInsert(user_entry)
        msg_resp = {'TYPE':MSG_USER_REGISTER_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID':userid}
    return msg_resp


def UserLoginAction(msg_req):
    user_entry = None
    tel = msg_req['TEL']
    passwd = msg_req['PASSWD']
    user_entry = UserFindOne('TEL', tel)
    if user_entry:
        if user_entry['PASSWD'] == passwd:
            user_entry['LOG'] = LOG_IN
            userid = UserUpdate(user_entry)
            msg_resp = {'TYPE':MSG_USER_LOGIN_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID':userid}
        else:
            msg_resp = {'TYPE':MSG_USER_LOGIN_RESP, 'STATUS':STATUS_FAIL, 'REASON':'wrong password!'}
    else:
        msg_resp = {'TYPE':MSG_USER_LOGIN_RESP, 'STATUS':STATUS_FAIL, 'REASON':'no such user!'}
    return msg_resp


def UserLogoutAction(msg_req):
    user_entry = None
    tel = msg_req['TEL']
    user_entry = UserFindOne('TEL', tel)
    if user_entry:
        user_entry['LOG'] = LOG_OUT
        userid = UserUpdate(user_entry)
        msg_resp = {'TYPE':MSG_USER_LOGOUT_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID':userid}
    else:
        msg_resp = {'TYPE':MSG_USER_LOGOUT_RESP, 'STATUS':STATUS_FAIL, 'REASON':'no registered user found!'}
    return msg_resp


def UserInfoAction(msg_req):
    user_entry = None
    userid = msg_req['USERID']
    user_entry = UserFindById(userid)
    if user_entry:
        ### by native, mongdb has "_id" key, delete it otherwise will cause problem in json encoding ###
        if user_entry.has_key('_id'):
            del user_entry['_id']
        #user_entry['USERID'] = userid
        ### after dumps, user_entry is formed as a json string, not a dict anymore ###
        #msg_resp = {'TYPE':MSG_USER_INFO_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'INFO':dumps(user_entry)}
        #try not using dumps
        msg_resp = {'TYPE':MSG_USER_INFO_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'INFO':user_entry}
    else:
        msg_resp = {'TYPE':MSG_USER_INFO_RESP, 'STATUS':STATUS_FAIL, 'REASON':'no registered user found!'}
    return msg_resp


def UserPollingAction(msg_req):
    user_entry = None
    userid = msg_req['USERID']
    update_item = msg_req['UPDATE']
    user_entry = UserFindById(userid)
    index = 0
    if user_entry:
        ### TBD, could have some merge here, the if branch's behavior is very similar. ###
        if update_item == POLLING_HELP_CANDO:
            #if user_entry['HAS_UPDATE'] & UPDATE_HELP_CANDO:
            #   user_entry['HAS_UPDATE'] &= (~UPDATE_HELP_CANDO)
            userid = UserUpdate(user_entry)
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'HELP_CANDO_LIST':user_entry['HELP_CANDO_LIST']}
            #else:
            #    msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'UPDATE':update_item, 'TOTAL_NUM': index, 
            #            'REASON':'no new incoming help request for you!'} 
        elif update_item == POLLING_HELP_CANDO_EXT:
            ### one help_simple_entry = one user(initactor)_simple_info + one help_simple_info ###
            #if user_entry['HAS_UPDATE'] & UPDATE_HELP_CANDO:
            #    user_entry['HAS_UPDATE'] &= (~UPDATE_HELP_CANDO)
            userid = UserUpdate(user_entry)
            help_simple_entry_list = []
            for helpid in user_entry['HELP_CANDO_LIST']: 
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                initactorid = help_simple_info['INITACTOR']
                initactor_simple_info = UserSimpleInfo(initactorid)
                ### initactor's userid is contained in help_simple_info already ###
                del initactor_simple_info['USERID']
                help_simple_entry = dict(help_simple_info.items() + initactor_simple_info.items()) 
                help_simple_entry.update({'INDEX':index})
                distance = map_logic.GetDistance(user_entry['LONGITUDE'], user_entry['LATITUDE'], 
                                    help_simple_info['LONGITUDE'], help_simple_info['LATITUDE']) 
                help_simple_entry.update({'DISTANCE':distance})
                help_simple_entry_list.append(help_simple_entry)
                index += 1
            help_simple_entry_list.reverse()
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'TOTAL_NUM': index, 'HELP_CANDO_LIST_EXT':help_simple_entry_list}
            #else:
            #    msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'UPDATE':update_item, 'TOTAL_NUM': index, 
            #            'REASON':'no new incoming help request for you!'} 
        elif update_item == POLLING_HELP_ME:
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'HELP_ME_LIST':user_entry['HELP_ME_LIST']}
        elif update_item == POLLING_HELP_ME_EXT:
            user_simple_info = UserSimpleInfo(userid)
            help_simple_info_list = []
            for helpid in user_entry['HELP_ME_LIST']:
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                help_simple_info.update({'INDEX':index})
                help_simple_info_list.append(help_simple_info)
                index += 1
            help_simple_info_list.reverse()
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', \
                    'UPDATE':update_item, 'USER_INFO':user_simple_info, 'TOTAL_NUM': index, 'HELP_ME_LIST_EXT':help_simple_info_list}
        elif update_item == POLLING_HELP_ME_DOING_EXT:
            user_simple_info = UserSimpleInfo(userid)
            help_simple_info_list = []
            for helpid in user_entry['HELP_ME_LIST']:
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                if help_simple_info['STATUS'] != FINISHED:
                    help_simple_info.update({'INDEX':index})
                    help_simple_info_list.append(help_simple_info)
                    index += 1
                else:
                    continue
            help_simple_info_list.reverse()#time order
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', \
                    'UPDATE':update_item, 'USER_INFO':user_simple_info, 'TOTAL_NUM': index, 'HELP_ME_LIST_DOING_EXT':help_simple_info_list}
        elif update_item == POLLING_HELP_ME_DONE_EXT:
            user_simple_info = UserSimpleInfo(userid)
            help_simple_info_list = []
            for helpid in user_entry['HELP_ME_LIST']:
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                if help_simple_info['STATUS'] == FINISHED:
                    help_simple_info.update({'INDEX':index})
                    help_simple_info_list.append(help_simple_info)
                    index += 1
                else:
                    continue
            help_simple_info_list.reverse()#time order
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', \
                    'UPDATE':update_item, 'USER_INFO':user_simple_info, 'TOTAL_NUM': index, 'HELP_ME_LIST_DONE_EXT':help_simple_info_list}
        elif update_item == POLLING_HELP_ACCEPT:
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'HELP_ACCEPT_LIST':user_entry['HELP_ACCEPT_LIST']}
        elif update_item == POLLING_HELP_ACCEPT_EXT:
            userid = UserUpdate(user_entry)
            help_simple_entry_list = []
            for helpid in user_entry['HELP_ACCEPT_LIST']: 
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                initactorid = help_simple_info['INITACTOR']
                initactor_simple_info = UserSimpleInfo(initactorid)
                ### initactor's userid is contained in help_simple_info already ###
                del initactor_simple_info['USERID']
                help_simple_entry = dict(help_simple_info.items() + initactor_simple_info.items()) 
                help_simple_entry.update({'INDEX':index})
                help_simple_entry_list.append(help_simple_entry)
                index += 1
            help_simple_entry_list.reverse()
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'TOTAL_NUM': index, 'HELP_ACCEPT_LIST_EXT':help_simple_entry_list}
        elif update_item == POLLING_HELP_FINISH:
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'HELP_ACCEPT_LIST':user_entry['HELP_FINISH_LIST']}
        elif update_item == POLLING_HELP_FINISH_EXT:
            userid = UserUpdate(user_entry)
            help_simple_entry_list = []
            for helpid in user_entry['HELP_FINISH_LIST']: 
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                initactorid = help_simple_info['INITACTOR']
                initactor_simple_info = UserSimpleInfo(initactorid)
                ### initactor's userid is contained in help_simple_info already ###
                del initactor_simple_info['USERID']
                help_simple_entry = dict(help_simple_info.items() + initactor_simple_info.items()) 
                help_simple_entry.update({'INDEX':index})
                help_simple_entry_list.append(help_simple_entry)
                index += 1
            help_simple_entry_list.reverse()
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'TOTAL_NUM': index, 'HELP_FINISH_LIST_EXT':help_simple_entry_list}
        elif update_item == POLLING_HELP_UNFINISH:
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'HELP_ACCEPT_LIST':user_entry['HELP_UNFINISH_LIST']}
        elif update_item == POLLING_HELP_UNFINISH_EXT:
            userid = UserUpdate(user_entry)
            help_simple_entry_list = []
            for helpid in user_entry['HELP_UNFINISH_LIST']: 
                help_simple_info = help_logic.HelpSimpleInfo(helpid)
                initactorid = help_simple_info['INITACTOR']
                initactor_simple_info = UserSimpleInfo(initactorid)
                ### initactor's userid is contained in help_simple_info already ###
                del initactor_simple_info['USERID']
                help_simple_entry = dict(help_simple_info.items() + initactor_simple_info.items()) 
                help_simple_entry.update({'INDEX':index})
                help_simple_entry_list.append(help_simple_entry)
                index += 1
            help_simple_entry_list.reverse()
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, \
                        'UPDATE':update_item, 'TOTAL_NUM': index, 'HELP_UNFINISH_LIST_EXT':help_simple_entry_list}
        else:
            msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'REASON':'no such update item!'}

    else:
        msg_resp = {'TYPE':MSG_USER_POLLING_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'REASON':'no registered user found!'}
    return msg_resp


def UserReportAction(msg_req):
    user_entry = None
    userid = msg_req['USERID']
    update_item = msg_req['UPDATE']
    lat = msg_req['LATITUDE']
    lon = msg_req['LONGITUDE']
    user_entry = UserFindById(userid)
    if user_entry:
        if update_item == REPORT_USER_LOCATION:
            user_entry['LATITUDE'] = lat
            user_entry['LONGITUDE'] = lon
            userid = UserUpdate(user_entry)
            msg_resp = {'TYPE':MSG_USER_REPORT_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'USERID': userid, 'UPDATE':update_item}
        else:
            msg_resp = {'TYPE':MSG_USER_REPORT_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'REASON':'no such update item!'}

    else:
        msg_resp = {'TYPE':MSG_USER_REPORT_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'REASON':'no registered user found!'}
    return msg_resp


def UsersGetDistanceAction(userid1, userid2):
    user1_entry = UserFindById(userid1)
    user2_entry = UserFindById(userid2)
    update_item = REPORT_USER_DISTANCE
    distance = map_logic.GetDistance(user1_entry['LONGITUDE'], user1_entry['LATITUDE'], 
                                    user2_entry['LONGITUDE'], user2_entry['LATITUDE']) 
    if user1_entry and user2_entry:
        msg_resp = {'TYPE':MSG_USER_REPORT_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'DISTANCE': distance,'REASON':'ok!'}
    else:
        msg_resp = {'TYPE':MSG_USER_REPORT_RESP, 'STATUS':STATUS_FAIL, 'UPDATE':update_item, 'REASON':'no registered user found!'}
    return msg_resp










