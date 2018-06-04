import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import getpass
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--domain', dest='product', required=True, choices=['FTTU', 'PORTPROT', 'P2P'])
parser.add_argument('-v', '--version', required=True)
parser.add_argument('-w', '--week', default='')
parser.add_argument('-s', '--slot', default='')
parser.add_argument('-u', '--username', default='')
parser.add_argument('-p', '--password', default='')
parser.add_argument('-c', '--coverage', default='Weekly')
args = parser.parse_args()

if args.week=='' or args.slot=='':
    from settings import slot_map
    args.week, args.slot = slot_map[args.version]

product, version, week, slot = args.product, args.version, args.week, args.slot
ws = 'W%s slot %s' % (week, slot)
print(product, version, week, slot)

if int(slot)%2==0 and product=='PORTPROT':
  print('PORTPROT not run on slot 2 or slot 4')
  exit()


url_login = "http://135.249.31.173/webtia/login.php"
url_logout = 'http://135.249.31.173/webtia/logout.php'
local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/atxuser/TI_logs'
local_rep_path = 'D:\\TI_reports\\' if os.name=='nt' else '/home/atxuser/TI_reports'
today = time.strftime('%Y/%m/%d',time.localtime(time.time()))


def get_batch_owner(batch):
    if  'EQMT' in batch:
        return 'Li Songsong'
    elif 'QOS' in batch:
        return 'Wang Liyun'
    elif 'L3FWD' in batch:
        return 'Wu Liulan'
    elif 'MCAST' in batch or 'SETUP' in batch:
        return 'Yang Hong G'
    elif 'SUBMGMT' in batch:
        return 'Fang Ling'
    elif 'TRANSPORT' in batch:
        return 'Zhang Xiaohang'
    elif 'MGMT' in batch and 'SUBMGMT' not in batch:
        return 'Zhang Jieming'
    elif 'L2FWD' in batch:
        return 'He Qun'
    elif 'NFXSD_FANTF_REDUN' in batch:
        return 'Wu Liulan'
    elif 'PORTPROT' in batch:
        if slot == '1':
            return 'Li Songsong'
        elif slot == '3':
            return 'Zhou Yun C'
        elif slot == '5':
            return 'Zhang Xiaohang'
    elif 'VOIP' in batch:
        return 'Zhou Qian'
    else:
        return ''


def batch_belong_product(batch):
    if batch == 'CFXRA__GPON_suite-FTTU_weekly':
        return False
    if product == 'FTTU':
        if 'FTTU' in batch and 'LP' not in batch:
            return True
        if batch in ['NFXSB_NANTE_REDUND_daily', 'NFXSD_FANTF_REDUND_daily']:
            return True
    if product == 'PORTPROT':
        batch_list = ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSD_FANTF_REDUND_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']
        if batch in batch_list:
            return True
    if product == 'P2P':
        batch_list = ['SHA_NFXSE_FANTG_P2P_A2A_weekly',
                      'NFXSE_FANTF_PT_BATCH6_weekly',
                      'SHA_NFXSE_FANTF_P2P_COMM_weekly',
                      'SHA_NFXSE_FANTF_P2P_weekly']
        return batch in batch_list
    return False


def generate_issue_info(product):
    global issue
    issue = {}
    url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=&sAtc=&sBoard=&sTiType=&sPt=%s'

    uu = url % (version, product)
    print(uu)
    r = requests.get(uu)
    data = r.content.decode('utf-8')

    result = re.findall('<tr><td>.*?</td></tr>', data)
    assert(len(result)>=0)

    for case in result:
        case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]

        if 'SW' in case_info[10] or 'ENV' in case_info[10]:
            ll = []
            for x in [case_info[10], case_info[12], case_info[13]]:
                if x != '':
                    ll.append(x)
            iss = ' '.join(ll)

            if case_info[4] not in issue:
                issue[case_info[4]]  = iss
            elif case_info[4] in issue and iss not in issue[case_info[4]]:
                issue[case_info[4]] += '; ' + iss

        NEWTI.setdefault(case_info[4], 0)
        if 'YES' == case_info[11]:
            NEWTI[case_info[4]] += 1

    print('===> issue list:')
    for x in issue:
        print('     %s\t\t%s' % (x, issue[x]))
    print('===> new TI list:')
    for x in NEWTI:
        print('     %s\t\t%d' % (x, NEWTI[x]))


issue = {}
NEWTI = {}
generate_issue_info(product)

if args.username == '':
    username = input('please input your CSL username:')
    password = getpass.getpass('password:')
    #username, password = 'svc_hetran', 'asb#2345'
else:
    username, password = args.username, args.password

s = requests.Session()
payload = {'redi': 'index.php', 'pid': username, 'password':password, 'btnsubmit': 'login'}
r = s.post("http://135.249.31.173/webtia/login.php", data=payload)

if r.status_code== 200 and b'Authenticate successful' in r.content:
    print('===> login successful')
else:
    print('===> login failed with %s %s' % (username, '*********'))
    exit()

webtia_url = 'http://135.249.31.173/webtia/Presentation.php?strm=%s&bld=%s&tstype=%s'
strm = 'ISR' + version.split('.')[0]
print(webtia_url % (strm, version, args.coverage))
r = s.get(webtia_url % (strm, version, args.coverage))

if r.status_code== 200:
    print('===> get batch list info successful')
else:
    exit()


soup = BeautifulSoup(r.content)
a_list = soup.find_all('a')[3:]
batch_list = []

if args.coverage == 'Daily':
    a_list = a_list[1:]

for i in range(0, len(a_list), 2):
    td1, td2 = a_list[i], a_list[i+1]
    print('@@@@@@@@ td1: %s' % td1)
    #import pdb
    #pdb.set_trace()
    batch = td1.button.contents[0].strip()

    if batch_belong_product(batch):
        total_case = int(td1.button.attrs['title'].split(':')[-1])
        fail_case = int(td2.contents[0])
        ok_case = total_case - fail_case
        owner =  get_batch_owner(batch)
        iss = issue.get(batch, '')
        new_ti = str(NEWTI.get(batch, 0))
        dd = dict(batch=batch,total_case=total_case, fail_case=fail_case,ok_case=ok_case,owner=owner, iss=iss, new_ti=new_ti)
        #print(dd)
        batch_list.append(dd)

print('===> len of batch: %d' % len(batch_list))
for x in batch_list:
    print('     %s\t%d\t%d\t%d\t%s\t%s\t%s' % (x['batch'], x['total_case'], x['ok_case'], x['fail_case'], x['owner'], x['iss'], x['new_ti']))

r = s.get(url_logout)


os.chdir(local_rep_path)
sub_rep_path = '_'.join([week,slot,version])
try:
    os.makedirs(sub_rep_path)
except:
    pass

os.chdir(sub_rep_path)
print('===> enter report path: %s' % os.getcwd())

if args.coverage == 'Daily':
    product += '_Daily'
filename = 'Week%s-Slot%s-GPON_SB_TI_Summary-%s_%s.csv' % (week,slot,version,product)
with open(filename, 'w') as ff:
    for x in batch_list:
        #ff.write('%s,%s,%s,%s,%d,%d,%d,%s,%s\n' % (today, ws, x['batch'],version, x['total_case'], x['ok_case'], x['fail_case'], x['iss'], x['owner']))
        ff.write('%s,%s,%s,%d,%d,%d,%s,%s,%s\n' % (version, ws, x['batch'], x['total_case'], x['ok_case'], x['fail_case'], '"%s\"' % x['iss'], x['owner'], x['new_ti']))

