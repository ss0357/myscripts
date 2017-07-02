import os
import re
import sys
import pdb

local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/songsonl/TI_logs'

product = 'PORTPROT'
url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=&sAtc=&sBoard=&sTiType=&sPt=%s'

version = sys.argv[1]

if version=='':
  print('input version number')
  exit()

def check_pending_cases(version):
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

  result = re.findall('<tr><td>.*?</td></tr>', data)
  pending = []
  for case in result[::-1]:
      case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
      #print case_info
      if case_info[10]=='':
          print('\t\t'.join(case_info[3:6]))
          pending.append("%s____%s" % (case_info[3],case_info[4]))

  pending = list(set(pending))

  if len(pending)==0:
    print('===> all TI done.')
    return True
  else:
    return False


def get_latest_4_version(ver):
  build = ver.split('.')[0] + '.'
  url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=PORTPROT&sAtc=&sBoard=&sTiType=&sPt=PORTPROT'
  url = url % build
  print(url)
  try:
    import requests
    r = requests.get(url)
    data = r.content
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
  print(ver_list)
  i2 = ver_list.index(ver) + 1
  i1 = i2 - 4
  assert i1 > 0
  print(ver_list[i1:i2])
  return ver_list[i1:i2]


def get_TI_report(ver_list):
  build = ver_list[-1]
  stream = 'ISR' + ver_list[-1].split('.')[0]
  url = 'http://135.249.31.173/webtia/graphview.php?strm=%s&bld=%s&tstype=Weekly&dmntype=PORTPROT&bld1=%s&bld2=%s&bld3=%s&bld4=%s'
  url = url % (stream, build, ver_list[0], ver_list[1], ver_list[2], build)
  print('===> report url:')
  print(url)
  #try:
  #  import requests
  #  r = requests.get(url)
  #  data = r.text
  #except:
    #import urllib2
    #response = urllib2.urlopen(url)
    #data = response.read()
    #pass
    #
    #
  return
  import urllib2
  response = urllib2.urlopen(url)
  data = response.read()

  #pdb.set_trace()
  os.chdir(local_log_path)
  logfile = 'Week17XX-GPON_SB_TI_Summary-%s_PORTPROT.html' % build
  with open(logfile, 'w') as ff:
    ff.write(data)


if check_pending_cases(version):
  ver_list = get_latest_4_version(version)
  get_TI_report(ver_list)