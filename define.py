#-*- coding:utf-8 -*-
import os
import sys


################################################################################
################################################################################
################################################################################
import socket
import platform

MY_DELL = "dell"
MY_PRESARIO = "presario"

running_host = socket.gethostname() 
if (MY_DELL == running_host) or (MY_PRESARIO == running_host):
    IS_BAE = False
else:
    IS_BAE = True


################################################################################
################################################################################
################################################################################
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger()

def log_print(log_str):
    if IS_BAE == True:
        logger.info(log_str)
    else:
        print log_str


###################################################################
####################### CONFIGURATIONS ############################
###################################################################
UserDBName  = "userdb1"
HelpDBName  = "helpdb1"
UserDBTable = "user_0511" #collection is the same as table
HelpDBTable = "help_0511" 


###################################################################
######################## DEFINIATIONS #############################
###################################################################
STATUS_SUCCESS  = 0x00
STATUS_FAIL     = 0x01


MSG_USER_REGISTER_REQ   = 0x01
MSG_USER_REGISTER_RESP  = 0x02
MSG_USER_LOGIN_REQ      = 0x03
MSG_USER_LOGIN_RESP     = 0x04
MSG_USER_LOGOUT_REQ     = 0x05
MSG_USER_LOGOUT_RESP    = 0x06
MSG_USER_INFO_REQ       = 0x07
MSG_USER_INFO_RESP      = 0x08
MSG_USER_POLLING_REQ    = 0x09
MSG_USER_POLLING_RESP   = 0x0A
MSG_USER_REPORT_REQ     = 0x0B
MSG_USER_REPORT_RESP    = 0x0C


MSG_HELP_ADD_REQ        = 0x21
MSG_HELP_ADD_RESP       = 0x22
MSG_HELP_INFO_REQ       = 0x23
MSG_HELP_INFO_RESP      = 0x24
MSG_HELP_ACCEPT_REQ     = 0x25
MSG_HELP_ACCEPT_RESP    = 0x26
MSG_HELP_REJECT_REQ     = 0x27
MSG_HELP_REJECT_RESP    = 0x28
MSG_HELP_FINISH_REQ     = 0x29
MSG_HELP_FINISH_RESP    = 0x2A


#MSG_PERIODIC_REQ     = 0x0B
#MSG_PERIODIC_RESP    = 0x0C

#UserLogStatus:
UNREGISTERED    = 0x00
REGISTERED      = 0x01
LOG_IN          = 0x02
LOG_OUT         = 0x04


#UserHelpStatus:
HELP_NONE       = 0x00
HELP_ME         = 0x01
HELP_OTHERS     = 0x02


#HelpStatus:
STARTED          = 0
FORWARDED        = 1
NO_HELPERS       = 2
HAS_FEW_HELPERS  = 3
HAS_SOME_HELPERS = 4
HAS_MANY_HELPERS = 5
FINISHED         = 10


#Polling SubType:
POLLING_SOME_THING          = 0
POLLING_HELP_CANDO          = 1
POLLING_HELP_CANDO_EXT      = 2
POLLING_HELP_ME             = 3
POLLING_HELP_ME_EXT         = 4
POLLING_HELP_ACCEPT         = 5
POLLING_HELP_ACCEPT_EXT     = 6
POLLING_HELP_FINISH         = 7
POLLING_HELP_FINISH_EXT     = 8
POLLING_HELP_UNFINISH       = 9
POLLING_HELP_UNFINISH_EXT   = 10
POLLING_HELP_ME_DOING_EXT   = 11
POLLING_HELP_ME_DONE_EXT    = 12


#Report SubType:
REPORT_SOME_THING    = 0
REPORT_USER_LOCATION = 1
REPORT_USER_DISTANCE = 2


#UpdateStatus:
UPDATE_NONE         = 0x00
UPDATE_HELP_CANDO   = 0x01
#HAS_MSG         = 0x1
#NEW_HELP        = 0x2
#END_HELP        = 0x4


MAX_NUM_IN_USER_LIST = 10
MAX_NUM_IN_HELP_LIST = 10

###################################################################
######################## DB structure #############################
###################################################################
'''
USER DB: USER_ID | BASIC_INFO | LOGGING_STATUS | HELPME_LIST | HELPOTHER_LIST
HELP DB: HELP_ID | REQUEST_INFO (PEOPLE|LOCATION|TIME) | TRACKING_STATUS | PEOPLE_INVOLVED 
'''


################################################################################
################################################################################
################################################################################
######### below is for testing ########
jiayan_latitude = "31.190191760237"
jiayan_longitude = "121.54451409752"
jiayan_baidu_key = "68c73dd79134ebf8f8574eed21f77f64"
jiayan_baidu_key = jiayan_baidu_key.encode("UTF-8")
baidu_shanghai_map = "http://api.map.baidu.com/staticimage?width=800&height=600&center=121.47894508654,31.236004921296&zoom=12"


####### for code backup #######


