import os
import re
import sys
import pdb
import get_summary_chart
import shutil
import argparse


parser = argparse.ArgumentParser()
parser.add_argument('-d', '--domain', dest='product', required=True, choices=['FTTU', 'PORTPROT'])
parser.add_argument('-v', '--version', required=True)
parser.add_argument('-w', '--week', required=True)
parser.add_argument('-s', '--slot', required=True)
args = parser.parse_args()
product, version, week, slot = args.product, args.version, args.week, args.slot
print(product, version, week, slot)

if int(slot)%2==0 and product=='PORTPROT':
  print('PORTPROT not run on slot 2 or slot 4')
  exit()


def check_pending_cases(version):
  url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=&sAtc=&sBoard=&sTiType=&sPt=%s'
  uu = url % (version, product)
  print(uu)
  try:
    import requests
    r = requests.get(uu)
    data = r.content
  except:
    import urllib2
    response = urllib2.urlopen(uu)
    data = response.read()

  data = data.decode('utf-8')
  result = re.findall('<tr><td>.*?</td></tr>', data)
  pending = []
  for case in result[::-1]:
      case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
      #print case_info
      if case_info[10]=='':
        if int(slot)%2==0 and case_info[4].startswith('SHA_NFXSD'):
          print( 'abort ' + '\t\t'.join(case_info[3:6]))
          continue
        #if 'SHA_CFXRA_CFNTB' in case_info[4]:
        #  continue
        print('\t\t'.join(case_info[3:6]))
        pending.append("%s____%s" % (case_info[3],case_info[4]))

  pending = list(set(pending))

  if len(pending)==0:
    print('===> all TI done.')
    return True
  else:
    return False


def get_latest_4_version(ver, product):
  build = ver.split('.')[0] + '.'
  url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=O&sAtc=&sBoard=&sTiType=&sPt=%s'
  url = url % (build, product)
  print(url)
  try:
    import requests
    r = requests.get(url)
    data = r.content.decode('utf-8')
  except:
    import urllib2
    response = urllib2.urlopen(url)
    data = response.read()

  result = re.findall('<tr><td>.*?</td></tr>', data)
  ver_list = []
  for case in result:
    case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
    ver_list.append("%s" % case_info[3])

  ver_list = list(set(ver_list))
  ver_list.sort()
  ver_list = [str(x) for x in ver_list if float(x)<float(ver)+0.0001]

  if ver not in ver_list:
    print('%s not found in the version list' % ver)
    ver_list.append(ver)

  if len(ver_list)<4:
    ver_list = ['', '', ''] + ver_list
  print(ver_list)
  return(ver_list[-4:])


def get_TI_report(ver_list):
  build = ver_list[-1]
  stream = 'ISR' + ver_list[-1].split('.')[0]
  url = 'http://135.249.31.173/webtia/graphview.php?strm=%s&bld=%s&tstype=Weekly&dmntype=%s&bld1=%s&bld2=%s&bld3=%s&bld4=%s'
  url = url % (stream, build, product, ver_list[0], ver_list[1], ver_list[2], build)
  print('===> report url:')
  print(url)
  return url


local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/atxuser/TI_logs'
local_rep_path = 'D:\\TI_reports\\' if os.name=='nt' else '/home/atxuser/TI_reports'
network_path = "\\135.251.206.152\pt\Automation\TI_report"

try:
  os.makedirs(local_log_path)
  os.makedirs(local_rep_path)
except:
  pass

if check_pending_cases(version):
  ver_list = get_latest_4_version(version, product)
  rep_url = get_TI_report(ver_list)
  stream = 'R' + version.split('.')[0]
  os.chdir(local_rep_path)
  sub_rep_path = '_'.join([week,slot,version])
  try:
    os.makedirs(sub_rep_path)
  except:
    pass
  os.chdir(sub_rep_path)
  print('===> enter report path: %s' % os.getcwd())
  filename = 'Week17%s-Slot%s-GPON_SB_TI_Summary-%s_%s' % (week,slot,version,product)
  get_summary_chart.get_pdf_report(filename, rep_url)
  get_summary_chart.get_webpage_screenshot(filename, rep_url)

  chart_name = filename + '_chart'+'.png'
  if os.path.exists(chart_name):
    print(    "generate %s successful" % chart_name)
  swfr_name = filename + '_SWFR'+'.png'
  if os.path.exists(swfr_name):
    print(    "generate %s successful" % swfr_name)
  pdf_name = filename + '.pdf'
  if os.path.exists(pdf_name):
    print(    "generate %s successful" % pdf_name)


  network_path += '/' + stream + '/' + version + '/'
  network_path2 = network_path + pdf_name

  if os.name!='nt':
    print('===> please copy pdf report to: \n%s' % network_path)
    exit(0)

  # for windows
  try:
    os.makedirs(network_path)
  except:
    pass

  print('===> copy pdf report to: \n%s' % network_path2)
  shutil.copy(pdf_name, network_path2)
  if os.path.exists(network_path2):
    print('     success')
  else:
    print('     fail.')