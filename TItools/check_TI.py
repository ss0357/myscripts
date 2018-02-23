
import argparse
import getpass
import requests
import log
import logging
from autoTI import AutoTI


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--domain', default='EQMT')
parser.add_argument('-v', '--version', default='')
parser.add_argument('-c', '--compare', default='')
parser.add_argument('-D', '--download', action="store_true", default=False)
parser.add_argument('-A', '--autofill', action="store_true", default=False)
parser.add_argument('-U', '--update_excel', action="store_true", default=False)
parser.add_argument('-X', '--debug', action="store_true", default=False)


args = parser.parse_args()
print(args)
if args.debug:
    log.logger.setLevel(logging.DEBUG)


ATI = AutoTI(domain=args.domain, version=args.version, compare=args.compare)

if args.compare != '':
    ATI.get_pending_TI()
    ATI.get_old_result()
    ATI.save_compare_result()
    exit()

if args.update_excel:
    ATI.get_pending_TI()
    ATI.update_excel_file()

if args.download:
    ATI.download_log()

if args.autofill:
    ATI.fill_TI_result()
