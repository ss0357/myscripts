from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from PIL import Image
import shutil

dcap = dict(DesiredCapabilities.PHANTOMJS)
dcap["phantomjs.page.settings.userAgent"] = (
    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/53.0.2785.116 Safari/537.36"
)


def get_webpage_screenshot(filename, url):

    if os.path.exists(filename+ '_chart' +'.png'):
        os.remove(filename+ '_chart' +'.png')
    if os.path.exists(filename+ '_SWFR' +'.png'):
        os.remove(filename+ '_SWFR' +'.png')

    driver = webdriver.PhantomJS(desired_capabilities=dcap)
    driver.set_window_size(2000, 4000)
    driver.maximize_window()
    driver.get(url)
    driver.get_screenshot_as_file(filename+'.png')
    table = driver.find_element_by_id('graphicalppt_summarychart')
    left = table.location['x']
    top = table.location['y'] - 20
    right = table.location['x'] + table.size['width']
    bottom = table.location['y'] + table.size['height']

    im = Image.open(filename+'.png')
    im = im.crop((left, top, right, bottom))
    im.save(filename+ '_chart' +'.png')
    im.close()

    table = driver.find_element_by_id('graphicalppt_table1')
    left = table.location['x']
    top = table.location['y'] - 30
    right = table.location['x'] + table.size['width']
    bottom = table.location['y'] + table.size['height']
    im = Image.open(filename+'.png')
    im = im.crop((left, top, right, bottom))
    im.save(filename+ '_SWFR' +'.png')
    im.close()

    driver.quit()
    #graphicalppt_table1


def execute(script, args):
    global driver
    driver.execute('executePhantomScript', {'script': script, 'args' : args })


def get_pdf_report(filename, url):
    global driver
    driver = webdriver.PhantomJS('phantomjs')

    # hack while the python interface lags
    driver.command_executor._commands['executePhantomScript'] = ('POST', '/session/$sessionId/phantom/execute')
    driver.get(url)

    # set page format
    # inside the execution script, webpage is "this"
    pageFormat = '''this.paperSize = {format: "A4", orientation: "portrait", margin: "1cm" };'''
    execute(pageFormat, [])

    # render current page
    render = '''this.render("test.pdf")'''
    execute(render, [])
    shutil.copy('test.pdf', filename+'.pdf')


if __name__ == '__main__':
    url = 'file:///D:/TI_logs/Week17XX-GPON_SB_TI_Summary-57.035_FTTU_chrome.html'
    get_webpage_screenshot('57.035_FTTU', url)
    get_pdf_report('57.035_FTTU', url)