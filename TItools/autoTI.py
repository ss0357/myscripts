import paramiko
import pexpect
import os
import re
import time
import sys
from pexpect import popen_spawn
import pdb
import yaml
import asyncio
import requests
import pandas as pd
import numpy as np
import getpass
from set_excel_format import set_excel_format
from contextlib import contextmanager
from requests_futures.sessions import FuturesSession
from down_TI_logs import download_log
from log import logger


class TICase(object):

    def __init__(self, case_info, flag=1):
        self.SNo, self.Stream, self.Build, self.Platform, self.ATC,\
        self.Board, self.ONT, self.Failed_Steps, self.RESULT,\
        self.TI_Type, self.NEW_TI, self.FRID, self.Comments = case_info

        self.flag = flag
        #logger.info(self.to_list())

    def to_list(self):
        return [self.SNo, self.Stream, self.Build, self.Platform, self.ATC,\
        self.Board, self.ONT, self.Failed_Steps, self.RESULT,\
        self.TI_Type, self.NEW_TI, self.FRID, self.Comments, self.flag]


class AutoTI(object):

    def __init__(self, version='', domain='FTTU'):
        batch_list = {
            'FTTU2': ['FTTU_L3FWD_weekly'],
            #'FTTU': ['FTTU_L3FWD_weekly', 'FTTU_SETUP_weekly', 'FTTU_EQMT_weekly'],
            'FTTU': ['FTTU_L3FWD_weekly', 'FTTU_EQMT_weekly'],
            'PORTPROT': ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']
        }
        self.version = version
        self.domain = domain
        self.batch_list = batch_list[domain]

        if self.domain=='FTTU':
            self.result_file = 'FTTU_EQMT.xls'
            self.result_file_raw = 'FTTU_EQMT_raw.xls'
            self.result_file_new = 'FTTU_EQMT_new.xls'
            self.result_file_old = 'FTTU_EQMT_old.xls'
        elif self.domain=='PORTPROT':
            self.result_file = 'A2A.xls'
            self.result_file_raw = 'A2A_raw.xls'
            self.result_file_new = 'A2A_new.xls'
            self.result_file_old = 'A2A_old.xls'

        if os.name=='nt':
            self.result_path = r'D:\TI_logs\result'
            self.local_log_path = 'D:\\TI_logs\\'
        else:
            self.result_path = '/home/songsonl/TI_logs/result'
            self.local_log_path = '/var/www/html/TI_logs'



    def get_pending_TI(self):
        self.pending = []
        url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'
        logger.info('===> get pending TI from webtia: %s, %s' % (self.domain, str(self.batch_list)))

        for batch in self.batch_list:
            uu = url % (self.version, batch, self.domain)
            logger.info(uu)
            try:
                r = requests.get(uu)
                data = r.content.decode('utf-8')
            except:
                logger.info('===> get TI data from TIAWeb failed')

            result = re.findall('<tr><td>.*?</td></tr>', data)
            for case in result:
                case_info = [x.replace('</td>', '').replace('<td>', '') for x in case.split('<td align=left>')]

                if case_info[10]=='' and int(case_info[1])>1600000 and self.ver_in_range(case_info[3]):
                    logger.info(case_info[1:7])
                    if self.domain=='FTTU':
                        self.pending.append(TICase(case_info[1:14]))

                if self.domain=='PORTPROT':
                    self.pending.append(TICase(case_info[1:14], flag=0))



    def ver_in_range(self, ver):
        min_ver_list = [
          '4503.999',
          '5002.009',
          '5102.713',
          '52.144', '5201.441', '5202.562', '5203.623',
          '53.160', '5301.445', '5302.553',
          '54.170', '5401.551', '5402.575',
          '55.142', '5501.448', '5502.568',
          '56.170', '5601.452', '5602.500',
          ]

        ver1_1, ver1_2 = ver.split('.')
        ver1_1 = int(ver1_1)
        ver1_2 = int(ver1_2)

        for ver2 in min_ver_list:
          ver2_1, ver2_2 = ver2.split('.')
          ver2_1 = int(ver2_1)
          ver2_2 = int(ver2_2)

          #logger.info('check ver: ', ver1_1, ver1_2, ver2_1, ver2_2)
          if ver1_1 == ver2_1 and ver1_2<=ver2_2:
            return False

        return True


    def update_excel_file(self):
        if not self.pending:
            logger.info('===> not found pending TI, abort update excel')
            return
        self.columns = ['SNo','Stream','Build','Platform','ATC','Board','ONT','Failed_Steps','RESULT', 'TI_Type','NEW_TI','FRID','Comments', 'flag']
        sheetname='sheet1'
        os.chdir(self.result_path)
        old_data = pd.read_excel(self.result_file, sheetname=sheetname, converters={'SNo':str,'Failed_Steps':str, 'Build':str, 'flag':str})

        writer = pd.ExcelWriter(self.result_file_old)
        old_data.to_excel(writer,sheetname)
        writer.save()

        # update flag
        if self.domain=='FTTU':
            pending = [case.SNo for case in self.pending]
            old_data['flag'] = old_data['SNo'].where(old_data['SNo'].isin(pending), 0).where(~old_data['SNo'].isin(pending), 1)

        cases = [case.to_list() for case in self.pending]
        new_data = pd.DataFrame(cases, columns=self.columns)
        writer = pd.ExcelWriter(self.result_file_new)
        new_data.to_excel(writer,sheetname)
        writer.save()

        concat_data = pd.concat([old_data,new_data]).drop_duplicates('SNo').reset_index(drop=True)
        concat_data = concat_data[self.columns]

        concat_data = concat_data.sort_values(["SNo"],ascending=False)
        #import pdb; pdb.set_trace()
        concat_data = self.map_result(concat_data)
        concat_data = concat_data[self.columns]

        writer = pd.ExcelWriter(self.result_file_raw)
        concat_data.to_excel(writer,sheetname, na_rep='')
        writer.save()
        logger.info('===> excel file updated: %s' % self.result_file_raw)
        set_excel_format(self.result_file_raw, self.result_file)


    def map_result(self, data):
        logger.info('#'*80)
        logger.info('===> start map TI reuslt from history:')
        ddata = data.to_dict(orient='records')
        # ddata_TI = [x for x in ddata ddata['TI_Type']=='']
        # import pdb; pdb.set_trace()

        for case in ddata:
            for x in case:
                if str(case[x])=='nan':
                    case[x] = ''

        for case in ddata:
            if case['TI_Type']!='':
                continue
            for his_case in ddata:
                if his_case['TI_Type']=='' or  int(case['SNo'])<int(his_case['SNo']) or his_case['TI_Type']=='NonReproducible':
                    continue
                if case['ATC']==his_case['ATC'] and case['Failed_Steps']==his_case['Failed_Steps']\
                    and case['Platform']==his_case['Platform']:
                    # if his case comment !, dont map from it
                    if his_case['Comments'].startswith('!'):
                        continue
                    case['TI_Type'] = his_case['TI_Type']
                    case['NEW_TI'] = his_case['NEW_TI']
                    case['FRID'] = his_case['FRID']
                    if not his_case['Comments'].startswith('*'):
                        case['Comments'] = '*' + his_case['Comments']
                    else:
                        case['Comments'] = his_case['Comments']
                    case['flag'] = '2'
                    logger.info('-'*80)
                    logger.info('TI: %s  %s  %s maped success' % (case['Build'], case['ATC'], case['Platform']))
                    logger.info('\t\t ' + case['SNo'] + ' <---> ' + his_case['SNo'])
                    logger.info('\t\t ' + ' '.join([case['TI_Type'], case['NEW_TI'], case['FRID'], case['Comments']]))
                    break

        logger.info('#'*80)
        ret = pd.DataFrame.from_dict(ddata)
        return ret


    def download_log(self):
        log_list = [(x.Build, x.Platform) for x in self.pending]
        log_list = list(set(log_list))
        logger.info(log_list)
        for ver,batch in log_list:
            logger.info(self.get_log_url(ver, batch))
            download_log(ver, batch)


    def get_log_url(self, ver, batch):
        if batch.startswith('SHA_'):
            return 'http://135.251.200.212/log/%s/ASB-NFXSD-FANTF-FTTU-GPON-WEEKLY-B2-240-51/' % ver
        elif batch.startswith('SHA2_'):
            return 'http://135.251.200.212/log/%s/SHA_NFXSD_FANTF_FTTU_WEEKLY_04/' % ver
        else:
            return 'http://135.252.240.214:8080/TI_logs/%s/%s/InstantStatus.html' % (ver, batch)


    def get_TI_database(self):
        os.chdir(self.result_path)
        self.result_data = pd.read_excel(self.result_file, sheetname='sheet1', keep_default_na=False, converters={'SNo':str,'Failed_Steps':str, 'Build':str})
        self.ddata = self.result_data.set_index('SNo').to_dict('index')


    def fill_TI_result(self):
        self.get_TI_database()
        TI_Type_valid = ['ENV', 'SW', 'ATC', 'SW-ONT', 'NonReproducible', 'Inconsistent']
        #import pdb; pdb.set_trace()
        self.TI_filled = {case:self.ddata[case] for case in self.ddata if self.ddata[case]['flag'] and self.ddata[case]['TI_Type'] in TI_Type_valid}
        if len(self.TI_filled)<=0:
            logger.info('===> no TI need filled.')
            return

        logger.info('===> %s TIs will filled:' % len(self.TI_filled))
        for case in self.TI_filled:
            logger.info('\t', case, self.TI_filled[case]['Build'], self.TI_filled[case]['ATC'], self.TI_filled[case]['Platform'])

        logger.info('\n\n' + '#'*80)
        username = input('===> please input your username:')
        password = getpass.getpass('===> password:')
        #username, password = 'svc_hetran', 'asb#2345'
        #username, password = args.username, args.password
        with webtia_session(username, password) as fs:
            cocurrent = 8
            #tid_list = self.TI_filled.keys()
            tid_list = [x for x in self.TI_filled]
            for x,y in zip(range(0,len(tid_list), cocurrent), range(cocurrent, len(tid_list)+cocurrent, cocurrent)):
                self.TI_fill_result_future(fs, tid_list[x:y], username=username)


    def TI_fill_result_future(self, fs, tid_list, username='no one'):
        ret = {}
        logger.info('\n\n' + '#'*80)
        for case in tid_list:
            logger.info('fill TI result: ', case, self.TI_filled[case]['Build'], self.TI_filled[case]['ATC'], self.TI_filled[case]['Platform'])
            logger.info('\t\t', self.TI_filled[case]['TI_Type'],self.TI_filled[case]['NEW_TI'],self.TI_filled[case]['FRID'],self.TI_filled[case]['Comments'])

            TI_id = case
            batch = self.TI_filled[case]['Platform']
            TI_type = self.TI_filled[case]['TI_Type']
            NTI = self.TI_filled[case]['NEW_TI']
            fr_id = self.TI_filled[case]['FRID']
            commnt = self.TI_filled[case]['Comments']

            url = "http://135.249.31.173/webtia/modalpopup.php?id=%s" % batch
            payload = {
                'form_margin_remove_length': '10',
                'id': batch,
                'Sno_it[]': TI_id,
                'Select_box[]': TI_id,
                'TI[%s]'%TI_id : TI_type,
                'NTI[%s]'%TI_id : NTI,
                'fr_id[%s]'%TI_id : fr_id,
                'commnt[%s]'%TI_id : commnt,
                'User_name[%s]'%TI_id : username+'+',
                'auto_suggest[%s]'%TI_id : '',
                'formSubmit' : 'Save',
            }

            ret[case] = fs.post(url, payload)

        logger.info('\n\n' + '#'*80)
        for case in tid_list:
            logger.info('verify TI result: ', case, self.TI_filled[case]['Build'], self.TI_filled[case]['ATC'], self.TI_filled[case]['Platform'])
            response = ret[case].result()
            if response.status_code==200 and '#alert-pass' in response.text:
                logger.info('\t\tsuccess')
            else:
                logger.info('\t\tfailed')



@contextmanager
def webtia_session(username, password):
    logger.info('login')
    #s = requests.Session()
    fs = FuturesSession()
    payload = {'redi': 'index.php', 'pid': username, 'password':password, 'btnsubmit': 'login'}
    r = fs.post("http://135.249.31.173/webtia/login.php", data=payload)
    r = r.result()
    if r.status_code== 200 and b'Authenticate successful' in r.content:
        logger.info('===> login successful')
    else:
        logger.info('===> login failed with %s %s' % (username, '*********'))
        exit()
    yield fs
    logger.info('logout')