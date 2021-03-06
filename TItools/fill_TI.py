#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Li Songsong <ss0357@outlook.com>

import os
import re
import xlrd
import argparse
import pdb
import getpass
import requests
from contextlib import contextmanager
from requests_futures.sessions import FuturesSession



parser = argparse.ArgumentParser()
parser.add_argument('-f', '--exfile', default='dwerferferf', required=True,
    help='excel file: \\135.251.206.152\\pt\\Automation\\TI_analysis\\A2A\\57.069_NFXSE_FANTF_REDUND_PORTPROT_weekly.xls')
parser.add_argument('-A', '--all', action="store_true", default=False, help='fill for all TI')
args = parser.parse_args()


def get_TI_result_excel(exfile):

    TI_result = []

    try:
        data = xlrd.open_workbook(exfile)
    except Exception as e:
        print ('===> open excel file %s failed: %s' % (exfile, str(e)))
        exit(-1)

    table = data.sheets()[0]

    for case in range(1, table.nrows):
        if int(table.row_values(case)[-1]) > 0 and table.row_values(case)[-5] != '':
            case_name = table.row_values(case)[5]
            TI_type = table.row_values(case)[-5]
            NTI = table.row_values(case)[-4].upper()
            fr_id = table.row_values(case)[-3]
            commnt= table.row_values(case)[-2][0:100]

            #assert(TI_type in ['ATC', 'SW', 'ENV', 'NonReproducible', 'Inconsistent'])
            #assert(NTI in ['YES', 'NO'])
            if TI_type not in ['ATC', 'SW', 'ENV', 'NonReproducible', 'Inconsistent']:
                print('===> wrong TI type, must be ATC/SW/ENV/NonReproducible/Inconsistent')
                exit(-1)
            if NTI not in ['YES', 'NO']:
                print('===> new TI must be YES or NO')
                exit(-1)

            TI_result.append(table.row_values(case))

    data.release_resources()
    return TI_result


def TI_fill_result(s, TI_case, username='no one'):
    TI_id, version, batch = TI_case[1], TI_case[3], TI_case[4]
    print('fill TI result: ', ' '.join(TI_case[1:5]))
    TI_type = TI_result[TI_case[5]]['TI_type']
    NTI     = TI_result[TI_case[5]]['NTI']
    fr_id   = TI_result[TI_case[5]]['fr_id']
    commnt  = TI_result[TI_case[5]]['commnt']

    print(TI_type, NTI, fr_id, commnt)
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
        'User_name[%s]'%TI_id : username,
        'auto_suggest[%s]'%TI_id : '',
        'formSubmit' : 'Save',
    }
    #print(payload)
    r = s.post(url, payload)
    if '#alert-pass' in r.text:
        print('\t\tsuccess')


def TI_fill_result_future(fs, many_cases, username='no one'):
    ret = {}

    for case in many_cases:
        TI_id, version, batch = case[1], case[3], case[4]
        #TI_type, NTI, fr_id, commnt = get_TI_result_from_excel_file(case)
        #import pdb; pdb.set_trace()
        TI_type = case[-5]
        NTI     = case[-4]
        fr_id   = case[-3]
        commnt  = case[-2][:100]

        print('fill TI result: ', '  '.join(case[2:6]))
        print(TI_type, NTI, fr_id, commnt)
        if TI_type=='':
          print('\t\tnot found matched result from datebase')
          continue

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
            'User_name[%s]'%TI_id : username,
            'auto_suggest[%s]'%TI_id : '',
            'formSubmit' : 'Save',
        }

        ret[TI_id] = fs.post(url, payload)

    print('\n\n' + '#'*80)
    for case in many_cases:
        TI_id, version, batch = case[1], case[3], case[4]
        TI_type = case[-5]
        NTI     = case[-4]
        fr_id   = case[-3]
        commnt  = case[-2][:100]
        if TI_type=='':
            continue

        print('verify TI result: ', '  '.join(case[2:6]))
        response = ret[TI_id].result()
        if response.status_code==200 and '#alert-pass' in response.text:
            print('\t\tsuccess')
        else:
            print('\tfailed')


@contextmanager
def webtia_session(username, password):
    print('login')
    #s = requests.Session()
    fs = FuturesSession()
    payload = {'redi': 'index.php', 'pid': username, 'password':password, 'btnsubmit': 'login'}
    r = fs.post("http://135.249.31.173/webtia/login.php", data=payload)
    r = r.result()
    if r.status_code== 200 and b'Authenticate successful' in r.content:
        print('===> login successful')
    else:
        print('===> login failed with %s %s' % (username, '*********'))
        exit()
    yield fs
    print('logout')




if __name__ == '__main__':

    exfile = os.path.basename(args.exfile)

    print('\n\n' + '#'*80)
    print('===> search TI result from excel file:')
    pending_case = get_TI_result_excel(args.exfile)

    for case in pending_case:
        print(case)

    print('\n\n' + '#'*80)
    username = input('please input your username:')
    password = getpass.getpass('password:')

    print('\n\n' + '#'*80)
    print('===> fill TI result to website:')

    #with webtia_session(username, password) as s:
    #    for case in pending_case:
    #        if case[5] in TI_result:
    #            TI_fill_result(s, case, username=username)

    with webtia_session(username, password) as s:
        TI_fill_result_future(s, pending_case, username=username)




