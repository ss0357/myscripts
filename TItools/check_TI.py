
import argparse
import getpass
import requests
import down_TI_logs as ATI

excel_file = r'D:\tmp\FTTU_EQMT.xlsx'

parser = argparse.ArgumentParser()
parser.add_argument('-d', '--domain', default='FTTU', choices=['FTTU', 'PORTPROT', 'A2A'])
parser.add_argument('-v', '--version', default='')
parser.add_argument('-D', '--download', action="store_true", default=False)
parser.add_argument('-A', '--autofill', action="store_true", default=False)
parser.add_argument('-U', '--update_excel', action="store_true", default=False)


args = parser.parse_args()
if args.domain == 'A2A':
    args.domain = 'PORTPROT'
print(args)

# pending = ATI.get_pending_TI(args.domain, args.version)
pending = ATI.get_pending_TI_2(args.domain, args.version)

if args.update_excel:
    ATI.update_excel_file(excel_file, pending)


if args.download:
    for x in pending:
        version, batch = x[3], x[4]
        try:
            ATI.download_log(version, batch)
        except:
            print('===> down log for %s %s failed' % (version, batch))


if args.autofill and pending:
    username = input('please input your username:')
    password = getpass.getpass('password:')
    #username, password = 'svc_hetran', 'asb#2345'
    #username, password = args.username, args.password

    with ATI.webtia_session(username, password) as fs:
            ATI.TI_fill_result(fs, pending, username=username)
























if 0:
    # login to web tia site
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

    for case in pending:
        ATI.TI_fill_result(s, case)
        print('\n\n')