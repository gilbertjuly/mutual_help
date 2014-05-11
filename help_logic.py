# -*- coding: UTF-8 -*-

#import pymongo
import db_driver
import user_logic
import map_logic

from tornado.escape import json_encode, json_decode
from bson import ObjectId
from bson.json_util import dumps
from define import *
#from user_logic import UserFindById, UserFindAll, UserUpdate 

DB_Help = None

###################################################################
########################## Low Level ##############################
###################################################################
def HelpDBInit(DB_name, DB_table):
    global DB_Help
    DB_Help = db_driver.DB(DB_name)
    if DB_Help:
        DB_Help.SelectTable(DB_table)
        log_print("Help DB initialzation ok! %s, %s" % (DB_Help.DataBase, DB_Help.Table))
        return STATUS_SUCCESS
    else:
        log_print("Help DB initialzation error!")
        return STATUS_FAIL


def HelpGetId(help_entry):
    HID = dumps(help_entry['_id'])
    ### After inserted to DB, help_entry has one more member called "_id" ###
    ### HID is a string, something like "{"$oid": "5250441015808c14102afcd6"}", cut it off ###
    HID = HID[10:-2]
    return HID


def HelpFindOne(key, val):
    global DB_Help
    help_entry = DB_Help.FindOne(key, val)
    return help_entry


def HelpFindById(helpid):
    ## we may just use help_entry['HELPID'] ##
    global DB_Help
    help_entry = DB_Help.FindOne('_id', ObjectId(helpid))
    return help_entry


def HelpInsert(help_entry):
    DB_Help.Insert(help_entry)
    HID = HelpGetId(help_entry)
    help_entry['HELPID'] = HID
    HelpUpdate(help_entry)
    return HID


def HelpUpdate(help_entry):
    DB_Help.Update(help_entry)
    HID = help_entry['HELPID']
    return HID


def HelpSimpleInfo(helpid):
    help_entry = HelpFindById(helpid)
    help_simple_info = {'HELPID':help_entry['HELPID'], 'INITACTOR':help_entry['INITACTOR'], 'ADDRESS':help_entry['ADDRESS'],
            'START_TIME':help_entry['START_TIME'], 'STATUS':help_entry['STATUS'], 'TITLE': help_entry['TITLE'], 
            'SCORE':help_entry['SCORE'], 'LONGITUDE':help_entry['LONGITUDE'], 'LATITUDE':help_entry['LATITUDE']}
    return help_simple_info


###################################################################
######################### HIGH Level ##############################
###################################################################
##
##  ***Action:
##      input is dict type
##      output is dict type
##  the same as user_logic.py
##
##  HELP DB: HELPERS_CANDO_LIST -> HELPERS_ACCPET_LIST  -> HELPERS_FINISH_LIST
##                    |----------> HELPERS_REJECT_LIST
##
##
##  USER DB: HELP_CANDO_LIST    -> HELP_ACCPET_LIST     -> HELP_FINISH_LIST
##                                          |------------> HELP_UNFINISH_LIST
##                    |----------> HELP_REJECT_LIST
##
##
##

def HelpAddAction(msg_req):
    help_entry = None
    init_user_entry = None
    title = msg_req['TITLE']
    initactorid = msg_req['USERID']
    catagory = msg_req['CATAGORY']
    geo_range = msg_req['RANGE']
    timeout = msg_req['TIMEOUT']
    content = msg_req['CONTENT']
    lat = msg_req['LATITUDE']
    lon = msg_req['LONGITUDE']
    address = msg_req['ADDRESS'] 
    start_time = msg_req['START_TIME']
    score = msg_req['SCORE']
    phone = msg_req['PHONE']
    init_user_entry = user_logic.UserFindById(initactorid)
    if init_user_entry:
        ### the only thing that could connects the userDB and helpDB is the ID, that is: userid and helpid ###
        ### TBD, timeout for each help request, a timer for each help_request???  ###
        help_entry = {
                        'TITLE':title, \
                        'INITACTOR':initactorid, \
                        'CATAGORY':catagory, 'CONTENT':content, \
                        'LATITUDE':lat, 'LONGITUDE':lon, 'RANGE':geo_range, 'ADDRESS':address, \
                        'START_TIME':start_time, 'TIMEOUT':timeout, \
                        'STATUS':STARTED, \
                        'HELPERS_CANDO_LIST':[], \
                        'HELPERS_ACCEPT_LIST':[], \
                        'HELPERS_REJECT_LIST':[], \
                        'HELPERS_FINISH_LIST':[], \
                        'CANDO':0, 'ACCEPT':0, 'REJECT':0, 'FINISH':0, \
                        'SCORE':score,\
                        'PHONE':phone,\
                        'HELPID':0, \
                    }
        ### TBD, Find other users here, currently bypass MAP API and use all users ###
        for user_entry in user_logic.UserFindAll():
            if user_entry['USERID'] == initactorid:
                continue
            else:
                help_entry['HELPERS_CANDO_LIST'].append(user_entry['USERID'])
                help_entry['CANDO'] += 1
        helpid = HelpInsert(help_entry)
        init_user_entry['HELP_ME_LIST'].append(helpid)
        user_logic.UserUpdate(init_user_entry)
        for userid in help_entry['HELPERS_CANDO_LIST']:
            user_entry = user_logic.UserFindById(userid)
            ### when to remove? timeout and initactor click "finish" ###
            user_entry['HELP_CANDO_LIST'].append(helpid)
            user_entry['HAS_UPDATE'] |= UPDATE_HELP_CANDO
            user_logic.UserUpdate(user_entry)
        msg_resp = {'TYPE':MSG_HELP_ADD_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'HELPID':helpid}
    else:
        msg_resp = {'TYPE':MSG_HELP_ADD_RESP, 'STATUS':STATUS_FAIL, 'REASON':'no this user id!'}
    return msg_resp


def HelpAcceptAction(msg_req):
    help_entry = None
    user_entry = None
    helpid = msg_req['HELPID']
    userid = msg_req['USERID']
    help_entry = HelpFindById(helpid)
    user_entry = user_logic.UserFindById(userid)
    if help_entry and user_entry and (userid in help_entry['HELPERS_CANDO_LIST']):
        help_entry['STATUS'] = HAS_SOME_HELPERS
        help_entry['ACCEPT'] += 1
        help_entry['CANDO'] -= 1
        help_entry['HELPERS_ACCEPT_LIST'].append(userid)
        help_entry['HELPERS_CANDO_LIST'].remove(userid)
        helpid = HelpUpdate(help_entry)
        user_entry['HELP_ACCEPT_LIST'].append(helpid)
        user_entry['HELP_CANDO_LIST'].remove(helpid)
        user_entry['HAS_UPDATE'] |= UPDATE_HELP_CANDO
        user_entry['ACCEPT'] += 1
        user_logic.UserUpdate(user_entry)
        msg_resp = {'TYPE':MSG_HELP_ACCEPT_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'HELPID':helpid}
    else:
        msg_resp = {'TYPE':MSG_HELP_ACCEPT_RESP, 'STATUS':STATUS_FAIL, 'REASON':'Help ID or User ID wrong!'}
    return msg_resp


def HelpRejectAction(msg_req):
    help_entry = None
    user_entry = None
    helpid = msg_req['HELPID']
    userid = msg_req['USERID']
    help_entry = HelpFindById(helpid)
    user_entry = user_logic.UserFindById(userid)
    if help_entry and user_entry:
        help_entry['REJECT'] += 1
        help_entry['CANDO'] -= 1
        help_entry['HELPERS_REJECT_LIST'].append(userid)
        help_entry['HELPERS_CANDO_LIST'].remove(userid)
        helpid = HelpUpdate(help_entry)
        user_entry['HELP_REJECT_LIST'].append(helpid)
        user_entry['HELP_CANDO_LIST'].remove(helpid)
        user_entry['HAS_UPDATE'] |= UPDATE_HELP_CANDO
        user_entry['REJECT'] += 1
        user_logic.UserUpdate(user_entry)
        msg_resp = {'TYPE':MSG_HELP_REJECT_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'HELPID':helpid}
    else:
        msg_resp = {'TYPE':MSG_HELP_REJECT_RESP, 'STATUS':STATUS_FAIL, 'REASON':'Help ID or User ID wrong!'}
    return msg_resp


def HelpFinishAction(msg_req):
    help_entry = None
    init_user_entry = None
    helpid = msg_req['HELPID']
    inituserid = msg_req['USERID']
    finished_helpers_list = msg_req['FINISHED_HELPERS']
    help_entry = HelpFindById(helpid)
    init_user_entry = user_logic.UserFindById(inituserid)
    total_user_score = 0
    if help_entry and init_user_entry and (init_user_entry['USERID'] == help_entry['INITACTOR']):
        help_entry['STATUS'] = FINISHED
        for finished_helper in finished_helpers_list:
            userid = finished_helper['FINISHER_ID']
            user_score = finished_helper['FINISHER_SCORE']
            if userid == '':
                continue
            total_user_score += user_score
### Note: this is the last step, people in HELPERS_ACCEPT_LIST are those who accepted help but unfinished. 
### so if there is a query for helpers who accept the help_req after the help_req is finished, 
### it should be people in HELPERS_FINISH_LIST + HELPERS_ACCEPT_LIST(namely, HELPERS_UNFINISHED_LIST)
            help_entry['HELPERS_FINISH_LIST'].append(userid)
            help_entry['HELPERS_ACCEPT_LIST'].remove(userid)
            help_entry['FINISH'] += 1
            user_entry = user_logic.UserFindById(userid)
            user_entry['HELP_ACCEPT_LIST'].remove(helpid)
            user_entry['HELP_FINISH_LIST'].append(helpid)
            user_entry['HELP_FINISH_LIST_EXT'].append({"HELP_ID": helpid, "HELP_SCORE": user_score})
            user_entry['FINISH'] += 1
            user_entry['SCORE'] += user_score
            user_logic.UserUpdate(user_entry)

        for userid in help_entry['HELPERS_ACCEPT_LIST']:
            user_entry = user_logic.UserFindById(userid)
            user_entry['HELP_ACCEPT_LIST'].remove(helpid)
            user_entry['HELP_UNFINISH_LIST'].append(helpid)
            user_logic.UserUpdate(user_entry)

#        for userid in help_entry['HELPERS_REJECT_LIST']:
#            user_entry = user_logic.UserFindById(userid)
#            user_logic.UserUpdate(user_entry)

        for userid in help_entry['HELPERS_CANDO_LIST']:
            user_entry = user_logic.UserFindById(userid)
            user_entry['HELP_CANDO_LIST'].remove(helpid)
            user_entry['HAS_UPDATE'] |= UPDATE_HELP_CANDO
            user_logic.UserUpdate(user_entry)
        helpid = HelpUpdate(help_entry)
        init_user_entry['SCORE'] -= total_user_score
        user_logic.UserUpdate(init_user_entry)

        if total_user_score == help_entry['SCORE']:
            msg_resp = {'TYPE':MSG_HELP_FINISH_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'HELPID':helpid}
        else:
            msg_resp = {'TYPE':MSG_HELP_FINISH_RESP, 'STATUS':STATUS_FAIL, 'REASON':'Help Score doesnot match!'}
    else:
        msg_resp = {'TYPE':MSG_HELP_FINISH_RESP, 'STATUS':STATUS_FAIL, 'REASON':'Help ID or User ID wrong!'}
    return msg_resp


def HelpInfoAction(msg_req):
#    global DB_Help
    help_entry = None
    helpid = msg_req['HELPID']
    help_entry = HelpFindById(helpid)
    if help_entry:
        if help_entry.has_key('_id'):
            del help_entry['_id']
        user_accept_simple_info_list = []
        user_finish_simple_info_list = []
        loop_num = 0
        for userid in help_entry['HELPERS_ACCEPT_LIST']:
            user_simple_info = user_logic.UserSimpleInfo(userid)
            user_simple_info['DISTANCE'] = user_logic.UsersGetDistance(userid, help_entry['INITACTOR']) 
            user_accept_simple_info_list.append(user_simple_info)
            loop_num += 1
            if loop_num >= MAX_NUM_IN_USER_LIST:
                break;
        user_accept_simple_info_list = sorted(user_accept_simple_info_list, key = lambda x:x['DISTANCE'])
        loop_num = 0
        for userid in help_entry['HELPERS_FINISH_LIST']:
            user_simple_info = user_logic.UserSimpleInfo(userid)
            user_simple_info['DISTANCE'] = user_logic.UsersGetDistance(userid, help_entry['INITACTOR']) 
            user_simple_info['FINISH_SCORE'] = user_logic.UserGetFinishHelpScore(userid, helpid)
            user_finish_simple_info_list.append(user_simple_info)
            loop_num += 1
            if loop_num >= MAX_NUM_IN_USER_LIST:
                break;
        user_finish_simple_info_list = sorted(user_finish_simple_info_list, key = lambda x:x['DISTANCE'])
        del help_entry['HELPERS_ACCEPT_LIST']
        del help_entry['HELPERS_FINISH_LIST']
        del help_entry['HELPERS_CANDO_LIST']
        del help_entry['HELPERS_REJECT_LIST']
        help_entry.update({'HELPERS_ACCEPT_LIST_EXT':user_accept_simple_info_list})
        help_entry.update({'HELPERS_FINISH_LIST_EXT':user_finish_simple_info_list})
        initactor_simple_info = user_logic.UserSimpleInfo(help_entry['INITACTOR'])
        del help_entry['INITACTOR']
        help_entry.update({'INITACTOR_EXT':initactor_simple_info})
        #help_entry['HELPID'] = helpid
        #msg_resp = {'TYPE':MSG_HELP_INFO_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'INFO':dumps(help_entry)}
        #try not using dumps
        msg_resp = {'TYPE':MSG_HELP_INFO_RESP, 'STATUS':STATUS_SUCCESS, 'REASON':'OK', 'INFO':help_entry}
    else:
        msg_resp = {'TYPE':MSG_HELP_INFO_RESP, 'STATUS':STATUS_FAIL, 'REASON':'no help entry found!'}
    return msg_resp








