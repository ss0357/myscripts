import pdb
import re
import getpass
from down_TI_logs import download_log
import down_TI_logs
from down_TI_logs import get_TI_result
from down_TI_logs import ver_in_range


batch_list = ['NFXSB_NANTE_FTTU_L3FWD_weekly',
              'NFXSE_FANTF_FTTU_L3FWD_weekly',
              'NFXSB_NANTE_FTTU_SETUP_weekly',
              'NFXSE_FANTF_FTTU_SETUP_weekly',
              'NFXSB_NANTE_FTTU_EQMT_weekly',
              'NFXSE_FANTF_FTTU_EQMT_weekly',
              'SHA_NFXSD_FANTF_FTTU_L3FWD_weekly',
              'SHA_NFXSD_FANTF_FTTU_SETUP_weekly',
              'SHA_NFXSD_FANTF_FTTU_EQMT_weekly'
              ]

batch_list = ['FTTU_L3FWD_weekly', 'FTTU_SETUP_weekly', 'FTTU_EQMT_weekly']

product = 'FTTU'
url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'

pending = []


for batch in batch_list:
    uu = url % (batch, product)
    print(uu)
    try:
      import requests
      r = requests.get(uu)
      data = r.content.decode('utf-8')
    except:
      import urllib2
      response = urllib2.urlopen(uu)
      data = response.read()

    result = re.findall('<tr><td>.*?</td></tr>', data)

    for case in result:
        case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
        if case_info[10]=='' and ver_in_range(case_info[3]):
            print(case_info[1:10])
            #pending.append("%s____%s____%s" % (case_info[1], case_info[3],case_info[4]))
            pending.append(case_info[:10])

#pending = list(set(pending))


# login to web tia site
if pending:
    username = input('please input your username:')
    password = getpass.getpass('password:')
    #username, password = 'svc_hetran', 'asb#2345'
    #username, password = args.username, args.password

    s = requests.Session()
    payload = {'redi': 'index.php', 'pid': username, 'password':password, 'btnsubmit': 'login'}
    r = s.post("http://135.249.31.173/webtia/login.php", data=payload)

    if r.status_code== 200 and b'Authenticate successful' in r.content:
        print('===> login successful')
    else:
        print('===> login failed with %s %s' % (username, '*********'))
        exit()


def TI_fill_result(TI_case):
    TI_id, version, batch = TI_case[1], TI_case[3], TI_case[4]
    print('fill TI result: ', '  '.join(TI_case))
    TI_type, NTI, fr_id, commnt = get_TI_result(TI_case)

    if not TI_type:
      print('not found matched result from datebase')
      return

    print('\t\t', TI_type, NTI, fr_id, commnt)
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
        'User_name[%s]'%TI_id : 'songsonl',
        'auto_suggest[%s]'%TI_id : '',
        'formSubmit' : 'Save',
    }
    #print(payload)
    r = s.post(url, payload)
    if '#alert-pass' in r.text:
        print('\t\tsuccess')



for case in pending:
    TI_fill_result(case)