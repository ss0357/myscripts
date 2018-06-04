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
parser.add_argument('-W', '--week', default='18xx')
parser.add_argument('-S', '--slot', default='x')


args = parser.parse_args()
print(args)
if args.debug:
    log.logger.setLevel(logging.DEBUG)


ATI = AutoTI(domain=args.domain, version=args.version,
            compare=args.version, week=args.week, slot=args.slot)
ATI.get_pending_TI()

if ATI.pending:
    print('===> TI not done.')
    exit(-1)

ATI.get_old_result()
ATI.save_old_result()
