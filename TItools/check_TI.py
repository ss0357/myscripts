
import re
from down_TI_logs import download_log_ASB,download_log

batch_list = ['NFXSB_NANTE_FTTU_L3FWD_weekly',
              'NFXSE_FANTF_FTTU_L3FWD_weekly',
              'NFXSB_NANTE_FTTU_SETUP_weekly',
              'NFXSE_FANTF_FTTU_SETUP_weekly',
              'NFXSB_NANTE_FTTU_EQMT_weekly',
              'NFXSE_FANTF_FTTU_EQMT_weekly',
              'SHA_NFXSD_FANTF_FTTU_L3FWD_weekly',
              'SHA_NFXSD_FANTF_FTTU_SETUP_weekly',
              'SHA_NFXSD_FANTF_FTTU_EQMT_weekly'
              ]

batch_list = ['FTTU_L3FWD_weekly', 'FTTU_SETUP_weekly', 'FTTU_EQMT_weekly']

product = 'FTTU'
url = 'http://135.249.31.114/cgi-bin/test/ti_info.cgi?sRelease=&sBuild=&sPlatform=%s&sAtc=&sBoard=&sTiType=&sPt=%s'

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
    uu = url % (batch, product)
    try:
      import requests
      r = requests.get(uu)
      data = r.content
    except:
      import urllib2
      response = urllib2.urlopen(uu)
      data = response.read()

    result = re.findall('<tr><td>.*?</td></tr>', data)

    for case in result[-50:]:
        case_info = [x.strip('</td>')  for x in case.split('<td align=left>')]
        if case_info[10]=='' and ver_in_range(case_info[3]):
            print(case_info[3:7])
            pending.append("%s____%s" % (case_info[3],case_info[4]))

pending = list(set(pending))

for x in pending:
    version, batch = x.split('____')
    if batch.startswith('SHA'):
      download_log_ASB(version, batch)
    else:
      download_log(version, batch)