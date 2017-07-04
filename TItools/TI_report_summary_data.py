import requests
from bs4 import BeautifulSoup
import re
import sys
import os
import time
import getpass

print('python %s product version week slot')
url_login = "http://135.249.31.173/webtia/login.php"
url_logout = 'http://135.249.31.173/webtia/logout.php'
local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/songsonl/TI_logs'
local_rep_path = 'D:\\TI_reports\\' if os.name=='nt' else '/home/songsonl/TI_reports'
today = time.strftime('%Y/%m/%d',time.localtime(time.time()))


product = sys.argv[1]
version = sys.argv[2]
week, slot = sys.argv[3], sys.argv[4]
ws = 'W%s slot %s' % (week, slot)


def get_batch_owner(batch):
    if 'SETUP' in batch or 'EQMT' in batch or 'L3FWD' in batch:
        return 'Li Songsong'
    elif 'QOS' in batch:
        return 'Wang Liyun'
    elif 'MCAST' in batch:
        return 'Yang Hong G'
    elif 'TRANSPORT' in batch or 'SUBMGMT' in batch:
        return 'Ma Hui C'
    elif 'MGMT' in batch and 'SUBMGMT' not in batch:
        return 'Zhang Jieming'
    elif 'L2FWD' in batch:
        return 'Lu Yuqin'
    elif 'NFXSD_FANTF_REDUN' in batch:
        return 'Wu Liulan'
    elif 'PORTPROT' in batch:
        if slot == '1':
            return 'Lu Luyun'
        elif slot == '3':
            return 'Zhou Yun C'
        elif slot == '5':
            return 'Yao Qingfen'
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
    if product == 'PORTPROT':
        batch_list = ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSD_FANTF_REDUND_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']
        if batch in batch_list:
            return True
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
    assert(len(result)>2)

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

    print('===> issue list:')
    for x in issue:
        print('     %s\t\t%s' % (x, issue[x]))

issue = {}
generate_issue_info(product)

#username = input('please input your username:')
#password = getpass.getpass('password:')
username, password = 'svc_hetran', 'asb#2345'

s = requests.Session()
payload = {'redi': 'index.php', 'pid': username, 'password':password, 'btnsubmit': 'login'}
r = s.post("http://135.249.31.173/webtia/login.php", data=payload)

if r.status_code== 200 and b'Authenticate successful' in r.content:
    print('===> login successful')
else:
    exit()

webtia_url = 'http://135.249.31.173/webtia/Presentation.php?strm=%s&bld=%s&tstype=Weekly'
strm = 'ISR' + version.split('.')[0]
print(webtia_url % (strm, version))
r = s.get(webtia_url % (strm, version))

if r.status_code== 200:
    print('===> get batch list info successful')
else:
    exit()


soup = BeautifulSoup(r.content)
a_list = soup.find_all('a')[3:]
batch_list = []

for i in range(0, len(a_list), 2):
    td1, td2 = a_list[i], a_list[i+1]
    batch = td1.button.contents[0].strip()

    if batch_belong_product(batch):
        total_case = int(td1.button.attrs['title'].split(':')[-1])
        fail_case = int(td2.contents[0])
        ok_case = total_case - fail_case
        owner =  get_batch_owner(batch)
        iss = issue.get(batch, '')
        dd = dict(batch=batch,total_case=total_case, fail_case=fail_case,ok_case=ok_case,owner=owner, iss=iss)
        #print(dd)
        batch_list.append(dd)

print('===> len of batch: %d' % len(batch_list))
for x in batch_list:
    print('     %s\t%d\t%d\t%d\t%s\t%s' % (x['batch'], x['total_case'], x['ok_case'], x['fail_case'], x['owner'], x['iss']))

r = s.get(url_logout)


os.chdir(local_rep_path)
sub_rep_path = '_'.join([week,slot,version])
try:
    os.makedirs(sub_rep_path)
except:
    pass

os.chdir(sub_rep_path)
print('===> enter report path: %s' % os.getcwd())

filename = 'Week17%s-Slot%s-GPON_SB_TI_Summary-%s_%s.csv' % (week,slot,version,product)
with open(filename, 'w') as ff:
    for x in batch_list:
        #ff.write('%s,%s,%s,%s,%d,%d,%d,%s,%s\n' % (today, ws, x['batch'],version, x['total_case'], x['ok_case'], x['fail_case'], x['iss'], x['owner']))
        ff.write('%s,%s,%s,%d,%d,%d,%s,%s\n' % (today, ws, x['batch'], x['total_case'], x['ok_case'], x['fail_case'], x['iss'], x['owner']))

