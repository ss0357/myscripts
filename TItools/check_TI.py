
import argparse
import getpass
import requests
from autoTI import AutoTI


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


ATI = AutoTI(domain=args.domain, version=args.version)

if args.update_excel:
    ATI.get_pending_TI()
    ATI.update_excel_file()

if args.download:
    ATI.download_log()

if args.autofill:
    ATI.fill_TI_result()
