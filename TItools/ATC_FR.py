import requests
import pandas as pd
import numpy as np
from requests.auth import HTTPBasicAuth
from io import StringIO
import getpass
import argparse
import logging
import sys
import time


#log_path = r'D:\songsonl\check_FR.log'
logger = logging.getLogger("AppName")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
#file_handler = logging.FileHandler(log_path)
#file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
#logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)


parser = argparse.ArgumentParser()
parser.add_argument('-u', '--user', default='')
parser.add_argument('-p', '--password', default='')
parser.add_argument('-D', '--debug', action="store_true", default=False)
parser.add_argument('-i', '--idlist', default='songsonl,qyao,hcma,yzhou027,qczhou')
args = parser.parse_args()
if args.debug:
    logger.setLevel(logging.DEBUG)
logger.debug(args)


cq_report_url = 'http://aww.sh.bel.alcatel.be/tools/dslam/cq/cgi-bin/cqReport.cgi'
pd.set_option('expand_frame_repr', False)


logger.info('\n\n' + '#'*80)
if args.user == '':
    username = input('===> please input your username:')
    password = getpass.getpass('===> password:')
else:
    username, password = args.user, args.password

user_list = args.idlist
logger.debug('user_list: %s' % user_list)


auth = HTTPBasicAuth(username, password)

#filter1 = 'id eq ALU02437644'
#filter2 = '''SubmitterId in (%s) and State eq Resolved''' % user_list
#filter3 = '''SubmitterId in (%s) and State eq Duplicate and DuplicateVerified neq Y''' % user_list
#'id,SubmitterId,SubmitterId.email,State,PlannedRelease,AssignedEngineer,Team,BriefDescription,DuplicateOn,DuplicateVerified',
# ResolvedOn is date


filter_resolved = '''SubmitterId in (%s) and State eq Resolved and Type eq FR''' % user_list
filter_query = '''SubmitterId in (%s) and State eq Query and Type eq FR''' % user_list
filter_duplicate = '''SubmitterId in (%s) and State eq Duplicate and DuplicateVerified eq N''' % user_list


payload = {
    'type' : 'FR_IR',
    'display' : 'id,SubmitterId.email,State,PlannedRelease,BriefDescription,BuildReference,DuplicateVerified',
    'format' : 'csv',
    'header' : 'yes',
    'filter' : ''}

##'resolved', 'query', 'duplicate'

for filter in ['resolved', 'query', 'duplicate']:
    payload['filter'] = vars()['filter_%s' % filter]
    logger.debug(payload['filter'])
    r = requests.get(cq_report_url, auth=auth, params=payload)
    logger.debug(r.url)
    logger.debug(r.content.decode('utf-8'))
    datastr = r.content.decode()
    if 'Invalid field reference' in datastr:
        logger.info('@@@@@@@@@@ query FR failed for filter %s @@@@@@@@@@@@' % filter)
        continue

    if '401 Authorization Required' in datastr:
        logger.error('login failed, use CIL as username')
        exit(-1)

    datastr = datastr.replace('\t',',')
    data = pd.read_csv(StringIO(datastr))

    logger.info('#'*80)
    logger.info('=> SW FR in %s status:\n' % filter)
    SW_FR = data[data['PlannedRelease'].str.contains('ISR')]
    #logger.info(SW_FR)
    print(SW_FR)
    print()
    logger.info('')
    logger.info('#'*80)
    logger.info('=> ATC FR in %s status:\n' % filter)
    ATC_FR = data[data['PlannedRelease'].str.contains('AUTO_ATC')]
    #logger.info(ATC_FR)
    print(ATC_FR)
    print()
    time.sleep(10)