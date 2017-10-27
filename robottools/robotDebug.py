#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Li Songsong <ss0357@outlook.com>
# This software is licensed under the New BSD License. See the LICENSE
# file in the top distribution directory for the full license text.

'''[summary]

[description]
'''

from robot.libraries.BuiltIn import BuiltIn
from robot.conf.settings import RobotSettings
from robot.errors import HandlerExecutionFailed
from robot.api.deco import keyword
from robot.variables import is_var
import re
import os
import subprocess
import pdb

cwd = os.path.split(os.path.realpath(__file__))[0]

class robotDebug(object):

    suite_name = ''
    case_name = ''
    backtrace = []
    kw_level = 0
    ROBOT_LISTENER_API_VERSION = 2
    pause_step = False
    pause_step_over = False
    pause_step_out = False
    old_user_cmd = ''
    robot_debug_file = ''
    KEYWORD_SEP = re.compile('  +|\t')
 
    def __init__(self, test_name = ''):
        self.test_name = test_name
        self.user_cmd = ''
        self.rf_bi = BuiltIn()
        os.system('echo \'def dbg():\n    pass\n\' > /tmp/dbg.py')


    def run_kw(self, kw):
        keyword = self.KEYWORD_SEP.split(kw)
        return self.rf_bi.run_keyword(*keyword)


    def get_robot_debug_file(self):
        self.robot_debug_file = self.run_kw('Get Variable Value  ${DEBUG FILE}')
        self.output_file = self.run_kw('Get Variable Value  ${OUTPUT FILE}')


    def start_keyword(self, name, attrs):

        self.backtrace.append(attrs['kwname'])
        self.kw_level += 1

        if self.pause_step or self.pause_step_over or self.pause_step_out:
            print('\nstart run keyword: %s     %s' % (name, attrs['args']) )
            #print('\nstart run keyword: %s     %s' % (name, attrs) )

        if self.pause_step or attrs['kwname']=='Dbg':
            self.enter_debug_shell()

        if self.pause_step_over and self.kw_level <= self.old_kw_level:
            self.enter_debug_shell()

        if self.pause_step_out and self.kw_level < self.old_kw_level:
            self.enter_debug_shell()

        if self.pause_step_out and self.kw_level == 1:
            self.enter_debug_shell()


    def end_keyword(self, name, attrs):
        self.backtrace.pop()
        self.kw_level -= 1

        if os.environ.has_key('PAUSE_AT_FAIL'):
            if os.environ['PAUSE_AT_FAIL']=='1' and attrs['status']=='FAIL':
                self.enter_debug_shell()



    def start_suite(self, name, attrs):
        self.suite_name = name
        self.run_kw('import library  /tmp/dbg.py')
        if self.robot_debug_file=='':
            self.get_robot_debug_file()
            self.show_debug_window()

    def show_debug_window(self):
        #return
        try:
            output = subprocess.check_output('ps uT | grep songsonl_robot_log | grep -v grep', shell=True)
            # print("\n%s" % output)
            ret = re.search('songsonl +([0-9]+) ', output)
            kill_cmd = 'kill -9 %s' % ret.group(1)
            subprocess.check_output(kill_cmd, shell=True)
        except subprocess.CalledProcessError as e:
            pass

        subprocess.Popen('xterm -title songsonl_robot_log -e tail -f %s' % self.robot_debug_file, shell=True)

    def print_backtrace(self):
        print('-'*80)
        for kw in self.backtrace[::-1]:
            print('kword > %s' % kw)
        print('case  > %s' % self.case_name)
        print('suite > %s' % self.suite_name)
        print('-'*80)

    #def close(self):
    #    #subprocess.call("sz -y -v /tmp/log.html /tmp/report.html /tmp/output.xml",shell=True)
    #    output_file = self.run_kw('Get Variable Value  ${OUTPUT FILE}')
    #    subprocess.call("python filter_robot_output.py %s CLI PCTA" % output_file, shell=True)

    def start_test(self, name, attrs):
        self.case_name = name

    def log_file(self, path):
        print(path.replace('/var/www/html', 'http://135.252.240.214:8080'))
        pass

    def report_file(self, path):
        if self.output_file:
            subprocess.call("python %s/filter_robot_output.py %s CLI PCTA" % (cwd, self.output_file), shell=True)
        pass

    def enter_debug_shell(self):
        print('\n')
        while 1:
            self.user_cmd = raw_input('RDB > ')
            #self.user_cmd = self.user_cmd.lower()

            if self.user_cmd != '':
                self.old_user_cmd = self.user_cmd

            if self.user_cmd == '' and self.old_user_cmd == '':
                continue

            if self.user_cmd == '' and self.old_user_cmd != '':
                self.user_cmd = self.old_user_cmd

            if self.user_cmd == 'c':
                self.pause_step = False
                self.pause_step_over = False
                self.pause_step_out = False
                return
            elif self.user_cmd == 's':
                self.pause_step = True
                return
            elif self.user_cmd == 'stepover':
                self.old_kw_level = self.kw_level
                self.pause_step_over = True
                return
            elif self.user_cmd == 'stepout':
                self.old_kw_level = self.kw_level
                self.pause_step_out = True
                return
            elif self.user_cmd == 'bt':
                self.print_backtrace()
            elif self.user_cmd == 'h':
                print('''
                    s    step run
                    c    continue
                    bt   print backtrace
                    h    print help
                    ''')
            else:
                # run given keyword
                try:
                    u_command = self.user_cmd.decode("utf-8")
                    keyword = self.KEYWORD_SEP.split(u_command)
                    variable_name = keyword[0].rstrip('= ')

                    if is_var(variable_name):
                        variable_value = self.rf_bi.run_keyword(*keyword[1:])
                        self.rf_bi._variables.__setitem__(variable_name,
                                                          variable_value)
                        print('< ', variable_name, '=', repr(variable_value))
                    else:
                        result = self.rf_bi.run_keyword(*keyword)
                        if result:
                            print('< ', repr(result))

                except HandlerExecutionFailed as exc:
                    print('< keyword: %s' % self.user_cmd)
                    print('! %s' % exc.full_message)
                except Exception as exc:
                    print('< keyword: %s' % self.user_cmd)
                    print('! FAILED: %s' % repr(exc))




