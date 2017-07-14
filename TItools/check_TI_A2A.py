import argparse
import re
from down_TI_logs import download_log


parser = argparse.ArgumentParser()
#parser.add_argument('-d', '--domain', dest='product', required=True, choices=['FTTU', 'PORTPROT'])
parser.add_argument('-v', '--version', required=True)
#parser.add_argument('-w', '--week', required=True)
#parser.add_argument('-s', '--slot', required=True)
args = parser.parse_args()


batch_list = ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly']

product = 'PORTPROT'
url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=%s&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'

pending = []


def ver_in_range(ver):
  v1, v2 = ver.split('.')
  v1 = int(v1)
  v2 = int(v2)
  if v1==5601 and v2>400:
    return True
  elif v1==56 and v2>170:
    return True
  elif v1==57:
    return True
  elif v1==5502 and v2>500:
    return True
  else:
    return False


for batch in batch_list:
    uu = url % (args.version, batch, product)
    print(uu)
    try:
      import requests
      r = requests.get(uu)
      data = r.content.decode('utf-8')
    except:
      import urllib2
      response = urllib2.urlopen(uu)
      data = response.read()

    result = re.findall('<tr><td>.*?</td></tr>', data)

    for case in result[]:
        case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
        if case_info[10]=='' and ver_in_range(case_info[3]):
            print(case_info[3:7])
            pending.append("%s____%s" % (case_info[3],case_info[4]))

pending = list(set(pending))

for x in pending:
    version, batch = x.split('____')
    download_log(version, batch)