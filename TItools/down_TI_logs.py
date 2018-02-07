#!/usr/bin/python
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
from set_excel_format import set_excel_format
from contextlib import contextmanager
from requests_futures.sessions import FuturesSession
from log import logger


local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/var/www/html/TI_logs'
#local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/atxuser/TI_logs'
#log_url = 'http://135.252.240.214:8080/TI_logs/%s/%s/InstantStatus.html'
log_url = 'http://135.251.196.133:8080/atxuser/TI_logs/%s/%s/InstantStatus.html'


with open(os.path.split(os.path.realpath(__file__))[0]+'/database.yaml', 'r') as stream:
        data = yaml.load(stream)

#global result_data
#result_data = pd.read_excel(r'D:\tmp\FTTU_EQMT.xls', sheetname='sheet1', converters={'SNo':str,'Failed_Steps':str, 'Build':str})

def get_pending_TI(product='FTTU', version=''):

    #'FTTU': ['FTTU_L3FWD_weekly', 'FTTU_SETUP_weekly', 'FTTU_EQMT_weekly'],
    batch_list = {
        'FTTU': ['FTTU_L3FWD_weekly'],
        'PORTPROT': ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']
    }
    url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'
    pending = []

    logger.info('===> get pending TI from webtia: %s, %s' % (product, str(batch_list[product])))

    for batch in batch_list[product]:
        uu = url % (version, batch, product)
        logger.info(uu)
        try:
            r = requests.get(uu)
            data = r.content.decode('utf-8')
        except:
            logger.info('===> get TI data from TIAWeb failed')

        result = re.findall('<tr><td>.*?</td></tr>', data)

        for case in result:
            case_info = [x.strip('</td>').strip('<td>')  for x in case.split('<td align=left>')]

            ## abort 7362
            #if 'CFXRA' in case_info[4]:
            #    continue

            if case_info[10]=='' and ver_in_range(case_info[3]):
                logger.info(case_info[1:7])
                pending.append(case_info[1:10])

    #pending = list(set(pending))
    return pending



async def get_pending_TI_for_batch(product='FTTU', version='', batch=''):

    url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'
    pending = []

    logger.info('===> get pending TI from webtia: %s, %s' % (product, batch))

    uu = url % (version, batch, product)
    logger.info(uu)
    r = await requests.get(uu)
    data = r.content.decode('utf-8')

    result = re.findall('<tr><td>.*?</td></tr>', data)

    for case in result:
        case_info = [x.replace('</td>', '').replace('<td>', '')  for x in case.split('<td align=left>')]

        if case_info[10]=='' and ver_in_range(case_info[3]):
            logger.info(case_info[1:7])
            pending.append(case_info[:10])

    #pending = list(set(pending))
    return pending


def get_pending_TI_2(product='FTTU', version=''):

    batch_list = {
        'FTTU': ['FTTU_L3FWD_weekly', 'FTTU_SETUP_weekly', 'FTTU_EQMT_weekly'],
        'PORTPROT': ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']
    }
    url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'
    pending = []
    ret = []
    async def main():
        loop = asyncio.get_event_loop()
        for batch in batch_list[product]:
            uu = url % (version, batch, product)
            logger.info(uu)
            ret.append(loop.run_in_executor(None, requests.get, uu))
            
        for r in ret:
            response1 = await r
            data = response1.content.decode('utf-8')
            result = re.findall('<tr><td>.*?</td></tr>', data)
            for case in result:
                case_info = [x.replace('</td>', '').replace('<td>', '')  for x in case.split('<td align=left>')]
                # abort 7362
                #if 'CFXRA' in case_info[4]:
                #    continue
                if case_info[10]=='' and ver_in_range(case_info[3]) and (int(case_info[1]))>1600000:
                    logger.info(case_info[1:7])
                    pending.append(case_info[1:10])

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    #pending = list(set(pending))
    return pending





def download_log_rlab(version, batch):
    logger.info(log_url % (version, batch))
    os.chdir(local_log_path)
    remotepath = '%s/%s' % (version, batch)
    if (os.path.exists(remotepath+'/apelogs/TS_focus.log1.gz')  \
            or os.path.exists(remotepath+'/apelogs/TS_focus.log1')) \
            and os.path.exists(remotepath+'/InstantStatus.html'):
        logger.info('log for %s exist, abort download.' % remotepath)
        return

    t = paramiko.Transport(("172.21.128.21",22))
    t.connect(username = "rmtlab", password = "rmtlab")
    sftp = paramiko.SFTPClient.from_transport(t)
    localpath =  remotepath
    try:
        os.makedirs( remotepath + "/apelogs/Logs" )
        os.makedirs( remotepath + "/HTML_Temp" )
        os.makedirs( remotepath + "/ARIES" )
    except:
        pass

    file_list = [remotepath+'/apelogs/TS_focus.log1.gz',
                remotepath+'/InstantStatus.html',
                remotepath+'/AtcInfo.html']
    try:
        for ff in sftp.listdir(remotepath+'/apelogs/Logs'):
            file_list.append(remotepath+'/apelogs/Logs/'+ff)

        for ff in sftp.listdir(remotepath+'/HTML_Temp'):
            file_list.append(remotepath+'/HTML_Temp/'+ff)

        for ff in sftp.listdir(remotepath+'/ARIES'):
            if ff.endswith('.log'):
                file_list.append(remotepath+'/ARIES/'+ff)
    except:
        logger.info('download log for %s %s failed' % (version, batch))


    for ff in file_list:
        logger.info('==> download file: %s' % ff)
        try:
            sftp.get(ff, ff)
        except:
            logger.info('download file %s failed')
    t.close()
    os.chdir(remotepath+'/apelogs/')
    os.system('gzip -d TS_focus.log1.gz')
    os.chdir(local_log_path)


def download_log_ASB(version, batch):
    #logger.info('dont need download log for SHA batch')
    #return
    logger.info(log_url % (version, batch))
    os.chdir(local_log_path)
    localpath = '%s/%s' % (version, batch)
    if (os.path.exists(localpath+'/SB_Logs/apelogs/TS_focus.log1.gz')  \
            or os.path.exists(localpath+'/SB_Logs/apelogs/TS_focus.log1')) \
            and os.path.exists(localpath+'/SB_Logs/InstantStatus.html'):
        logger.info('log for %s exist, abort download.' % localpath)
        return

    # search logs path on server
    #version2 = re.sub('0[12]{1}.', '.', version)
    version2 = version
    ret = re.match('.*_FTTU_(.*)_weekly', batch)
    domain_name = ret.group(1)

    if batch.startswith('SHA_NFXSD_FANTF'):
        atxserver_ip = '135.252.245.40'
        log_subdir = 'ASB-NFXSD-FANTF-FTTU-GPON-WEEKLY*'
        search_pattern = '-b %s.*? -d %s' % (version2, domain_name)

    if batch.startswith('SHA2_NFXSD_FANTF'):
        atxserver_ip = '135.252.245.33'
        log_subdir = 'SHA-NFXSD-FANTF-FTTU-WEEKLY-04'
        search_pattern = '-b %s.*? -d ROBOT:suite-FTTU,%s' % (version2, domain_name)

    if batch.startswith('SHA_CFXSC_CFNTC'):
        atxserver_ip = '135.252.245.33'
        log_subdir = 'SHA-CFXSC-CFNTC-SF8-FTTU-WEEKLY-01'
        search_pattern = '-b %s.*? -d ROBOT:suite-FTTU,%s' % (version2, domain_name)

    if batch.startswith('SHA_CFXRA_CFNTB'):
        atxserver_ip = '135.252.245.33'
        log_subdir = 'SHA-CFXRA-CFNTB-DF16-FTTU-WEEKLY-01'
        search_pattern = '-b %s.*? -d ROBOT:suite-FTTU,%s' % (version2, domain_name)


    logger.info('===> atxserver_ip: %s; log_subdir: %s; search_pattern: %s' % (atxserver_ip, log_subdir, search_pattern))
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(atxserver_ip, 22, "atxuser", "alcatel01")

    #search_cmd = "find /tftpboot/atx/logs/ASB-NFXSD-FANTF-FTTU-GPON-WEEKLY*/SD_%s -name \"testsummary.log\" | xargs grep \"d %s\"" % (version, domain_name)
    search_cmd = "find /tftpboot/atx/logs/%s/ -name \"testsummary.log\" | xargs grep -E -- \"%s\"" % (log_subdir, search_pattern)
    stdin, stdout, stderr = ssh.exec_command(search_cmd)
    output = stdout.readlines()

    if not output:
        logger.info('===> download_log_ASB: find log failed, no output')
        logger.info(search_cmd)
        return False

    ret = re.match('(.*?SB_Logs)/testsummary.log', output[0])
    if not ret:
        logger.info('===> download_log_ASB: find log failed')
        logger.info(output[0])
        return False

    remotepath = ret.group(1)
    print (version, batch, domain_name, remotepath)
    ssh.close()

    # scp from server
    cmd = 'pscp -r atxuser@%s:%s  %s' % (atxserver_ip, remotepath, localpath)
    print (cmd)
    try:
        os.makedirs(localpath)
    except:
        pass

    #child = pexpect.spawn(cmd)
    #pdb.set_trace()
    if sys.platform.startswith('win'):
        child = pexpect.popen_spawn.PopenSpawn(cmd, logfile = sys.stdout.buffer)
    else:
        child = pexpect.spawn(cmd)
    index = child.expect([u"(?i)yes/no",u"(?i)password", pexpect.EOF, pexpect.TIMEOUT])
    #import ipdb
    #ipdb.set_trace()
    if index==0:
        child.sendline('yes')
        child.expect(u'(?i)password')
        child.sendline('alcatel01')
    elif index==1:
        child.sendline('alcatel01')

    while 1:
        time.sleep(5)
        index = child.expect([u"(?i)100%",pexpect.EOF, pexpect.TIMEOUT])
        for line in child:
            print (line,)
        if index == 1:
            return

    return


def download_log(version, batch):
    if batch.startswith('SHA'):
        download_log_ASB(version, batch)
    else:
        download_log_rlab(version, batch)


def verify_log_content(case, log_mark):
    version, batch, case_name, failed_step = case[3], case[4], case[5], case[8]
    return True


def get_TI_result(case):
    #logger.info('get_TI_result:', data)
    batch, case_name, failed_step = case[4], case[5], case[8]
    for x in data:
        if x['case_name'] in case_name and \
            x.setdefault('batch', 'weekly') in batch  and \
            failed_step == x['failed_step'] :

            if x.setdefault('log', None) and not verify_log_content(case, x['log']):
                #logger.info("\t\t find matched case bug verify log content failed")
                continue
            return eval(x['result'])

    return ('', '', '', '')


def get_TI_result_from_excel_file(case):
    global result_data

    TI_id, version, batch = case[0], case[3], case[4]
    if TI_id not in list(result_data.SNo):
        return ('', '', '', '')
    _data = result_data[result_data.SNo==TI_id]
    TI_type = str(_data['TI_Type'].iloc[0])
    NTI = str(_data['NEW_TI'].iloc[0])
    fr_id = str(_data['FRID'].iloc[0])
    commnt = str(_data['Comments'].iloc[0])
    TI_type = '' if TI_type=='nan' else TI_type
    NTI = '' if NTI=='nan' else NTI
    fr_id = '' if fr_id=='nan' else fr_id
    commnt = '' if commnt=='nan' else commnt
    #print ('#get_TI_result_from_excel_file: ', case, TI_type, NTI, fr_id, commnt)
    return (TI_type, NTI, fr_id, commnt)



def _TI_fill_result(s, TI_case):
    TI_id, version, batch = TI_case[0], TI_case[2], TI_case[3]
    logger.info('fill TI result: ', '  '.join(TI_case))
    #TI_type, NTI, fr_id, commnt = get_TI_result(TI_case)
    TI_type, NTI, fr_id, commnt = get_TI_result_from_excel_file(TI_case)

    if TI_type=='':
      logger.info('\t\tnot found matched result from datebase')
      return

    logger.info('\t\t', TI_type, NTI, fr_id, commnt)
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
        'User_name[%s]'%TI_id : 'no_one',
        'auto_suggest[%s]'%TI_id : '',
        'formSubmit' : 'Save',
    }
    #logger.info(payload)
    r = s.post(url, payload)
    if '#alert-pass' in r.text:
        logger.info('\t\tsuccess')
    else:
        logger.info('\tfailed')


def found_TI_result(case):
    TI_type, NTI, fr_id, commnt = get_TI_result_from_excel_file(case)
    if TI_type in ['ENV', 'SW', 'ATC', 'SW-ONT', 'NonReproducible', 'Inconsistent']:
        return True
    else:
        return False


def TI_fill_result(s, pending, username='no one'):

    cocurrent = 8
    logger.info('===> TIs not found result from excel file:')
    for case in pending:
        TI_id, version, batch = case[0], case[3], case[4]
        if not found_TI_result(case):
            logger.info('\t', '  '.join(case[2:5]))
            logger.info('\t', get_TI_result_from_excel_file(case))

    pending2 = [case for case in pending if found_TI_result(case)]
    for x,y in zip(range(0,len(pending2), cocurrent), range(cocurrent, len(pending2)+cocurrent, cocurrent)):
        TI_fill_result_future(s, pending2[x:y], username=username)




def TI_fill_result_future(fs, many_cases, username='no one'):
    ret = {}

    logger.info('\n\n' + '#'*80)
    for case in many_cases:
        TI_id, version, batch = case[0], case[2], case[3]
        TI_type, NTI, fr_id, commnt = get_TI_result_from_excel_file(case)

        logger.info('fill TI result: ', '  '.join(case[2:5]))
        logger.info('\t\t', TI_type, NTI, fr_id, commnt)

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
            'User_name[%s]'%TI_id : 'no_one',
            'auto_suggest[%s]'%TI_id : '',
            'formSubmit' : 'Save',
        }

        ret[TI_id] = fs.post(url, payload)

    logger.info('\n\n' + '#'*80)
    for case in many_cases:
        TI_id, version, batch = case[0], case[2], case[3]
        #logger.info('fill TI result: ', '  '.join(case))
        TI_type, NTI, fr_id, commnt = get_TI_result_from_excel_file(case)
        logger.info('verify TI result: ', '  '.join(case[2:5]))
        response = ret[TI_id].result()
        if response.status_code==200 and '#alert-pass' in response.text:
            logger.info('\t\tsuccess')
        else:
            logger.info('\tfailed')



def ver_in_range(ver):
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


if __name__ == '__main__':
    version, batch = sys.argv[1], sys.argv[2]
    download_log(version, batch)
    #with open('database.yaml', 'r') as stream:
    #    data = yaml.load(stream)
    #logger.info(data)
    


def update_excel_file(excel_file, cases, sheetname='sheet1'):

    os.chdir(r'D:\tmp')
    old_data = pd.read_excel('FTTU_EQMT.xls', sheetname='sheet1', converters={'SNo':str,'Failed_Steps':str, 'Build':str})
    writer = pd.ExcelWriter('FTTU_EQMT_raw_old.xls')
    old_data.to_excel(writer,sheetname)
    writer.save()

    new_data = pd.DataFrame(cases, columns=['SNo','Stream','Build','Platform','ATC','Board','ONT','Failed_Steps','RESULT'])
    writer = pd.ExcelWriter('FTTU_EQMT_raw_new.xls')
    new_data.to_excel(writer,sheetname)
    writer.save()

    concat_data = pd.concat([old_data,new_data]).drop_duplicates('SNo').reset_index(drop=True)
    reordered = ['SNo','Stream','Build','Platform','ATC','Board','ONT','Failed_Steps','RESULT', 'TI_Type','NEW_TI','FRID','Comments']
    concat_data = concat_data[reordered]

    concat_data = concat_data.sort_values(["SNo"],ascending=True)

    writer = pd.ExcelWriter('FTTU_EQMT_raw.xls')
    concat_data.to_excel(writer,sheetname)
    writer.save()
    logger.info('===> excel file updated: D:\\tmp\\FTTU_EQMT_raw.xls')
    set_excel_format()


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