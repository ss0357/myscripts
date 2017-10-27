import os
import sys
import re
import time



parser = argparse.ArgumentParser()
parser.add_argument('-c', '--case', default='ALL')
parser.add_argument('-l', '--log', default='TS_focus.log1')
parser.add_argument('-l', '--log', default='TS_focus.log1')
parser.add_argument('-H', '--html', action="store_true", default=False)
parser.add_argument('-f', '--filter', action="store_true", default=False)


args = parser.parse_args()
log_file = args.log


os.chdir('.')
if not os.path.exists('TS_focus_parsed'):
    os.mkdir('TS_focus_parsed')

os.chdir('TS_focus_parsed')
logfile = open('../%s' % logfile_name, 'r')

sublogname = 'testsuite.log'
case_num = 0
sublogfile = open(sublogname, 'w')


while(1):
    line = logfile.readline()
    
    if line=='':
        print('===> parse finish.')
        break

    #ret = re.findall(': [0-9]* (.*)', line)
    #if ret:
    #    line = ret[0]+'\n'

    #if len(line.split(' ')) > 2 and len(line.split(' ')[0])<13:
    #    len_tag = len(line.split(' ')[0])
    #    line = ' '*(13-len_tag) + line

    if 'proc TP_IsamTopLevelTest medium' in line:
        ret = re.findall('-test .*/(.*?).ars', line)
        case_name = ret[0]
        print('===> case %d: %s' % (case_num, case_name))
        case_num = case_num + 1
        sublogfile.close()
        sublogfile = open('case%d_%s.log' % (case_num, case_name), 'w')

    if 'Step #' in line:
        line = line + '\n\n'
    sublogfile.write(line)

