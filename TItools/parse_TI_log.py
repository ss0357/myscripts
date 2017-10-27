import os
import sys
import re
import time
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-c', '--case', default='ALL')
parser.add_argument('-l', '--log', default='TS_focus.log1')
parser.add_argument('-H', '--html', action="store_true", default=False)
parser.add_argument('-f', '--filter', action="store_true", default=False)
args = parser.parse_args()



os.chdir('.')
if not os.path.exists('TS_focus_parsed'):
    os.mkdir('TS_focus_parsed')

os.chdir('TS_focus_parsed')
logfile = open('../%s' % args.log, 'r')

sublogname = 'testsuite.log'
case_num = 0
sublogfile = open(sublogname, 'w')
sublogfile.close()

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

        if case_name==args.case:
            print('===> case %d: %s' % (case_num, case_name))
        case_num = case_num + 1
        if not sublogfile.closed:
            print('close log file')
            sublogfile.close()

        if case_name==args.case:
            sublogfile = open('case%d_%s.log' % (case_num, case_name), 'w')
            print('start write sub log file')

    if not sublogfile.closed:
        if 'Step #' in line:
            line = line + '\n\n'
        sublogfile.write(line)

os.chdir('..')
if args.html:
    print('===> start parse case log to html:')
    for caselog in os.listdir('TS_focus_parsed'):
        if args.case in caselog and caselog.endswith('.log'):
            parse_html_cmd = 'tclsh /home/songsonl/myscripts/apme_tools/parseFocusLog_all.tcl -log TS_focus_parsed/%s' % caselog
            os.system(parse_html_cmd)



os.chdir('TS_focus_parsed')
if args.filter:
    print('===> start filter case log via ZY script:')
    for caselog in os.listdir('.'):
        if args.case in caselog and caselog.endswith('.log'):
            filter_cmd = 'tclsh /home/songsonl/myscripts/apme_tools/COMMAND_PARSE_ZhouYun_V4.1.tcl -LogPath %s -StcLog yes -PctaLog yes  -Alarms yes' % caselog
            os.system(filter_cmd)
