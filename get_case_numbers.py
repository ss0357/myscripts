import requests
import re


url_okcase = 'http://135.249.31.173/webtia/TIA/TIAResults.php?build=57.024&atc=&board=&platform=NFXSE_FANTF_FTTU_SETUP_weekly'

res = requests.get(url_okcase)

case_table = re.findall('<thead><tr><th>ATC</th><th>Board</th><th>Platform</th><th>57.024</th></tr></thead><tbody><tr>(.*?)</tbody></table><b>Total Records', res.content)

case_list = re.findall('<tr><td>.*?</td></tr>', case_table[0])



