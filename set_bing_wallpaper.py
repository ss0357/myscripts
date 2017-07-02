#coding:utf8
#环境要求:python2.7x,PIL,pywin32
#备注:只在win7系统试过正常
#创建时间:2015-1

#import Image
from PIL import Image
import win32api,win32con,win32gui
import re,os
import requests
import time
import random
import pdb

today = time.strftime('%Y_%m_%d',time.localtime(time.time()))

def get_wallpaper_from_bing(idx=0):

    os.chdir("D:\\bing_wallpaper")
    pic_name = today+ str(idx) + '.jpg'
    if os.path.exists(pic_name):
        return pic_name

    web = requests.get('http://cn.bing.com/HPImageArchive.aspx?idx=%d&n=1' % idx)
    ret = re.search('<url>(.*?.jpg)</url><urlBase>', str(web.content))
    pic_url = 'http://cn.bing.com' + ret.group(1)
    pic = requests.get(pic_url)

    with open(pic_name, 'wb') as file:
        file.write(pic.content)
    return pic_name


def get_wallpaper_from_plmeizi(idx=376):
    web = requests.get('http://bing.plmeizi.com/show/%d' % idx)
    ret = re.search('href=\"(http://bimgs.plmeizi.com/images/bing/.*?.jpg)\"', str(web.content))
    if not ret:
        return
    pic_url = ret.group(1)
    pic = requests.get(pic_url)
    os.chdir("D:\\bing_wallpaper")

    pic_name = today+ '_' + str(idx) + '.jpg'
    with open(pic_name, 'wb') as file:
        file.write(pic.content)
    return pic_name


def set_wallpaper_from_bmp(bmp_path):
    #打开指定注册表路径
    reg_key = win32api.RegOpenKeyEx(win32con.HKEY_CURRENT_USER,"Control Panel\\Desktop",0,win32con.KEY_SET_VALUE)
    #最后的参数:2拉伸,0居中,6适应,10填充,0平铺
    win32api.RegSetValueEx(reg_key, "WallpaperStyle", 0, win32con.REG_SZ, "2")
    #最后的参数:1表示平铺,拉伸居中等都是0
    win32api.RegSetValueEx(reg_key, "TileWallpaper", 0, win32con.REG_SZ, "0")
    #刷新桌面
    win32gui.SystemParametersInfo(win32con.SPI_SETDESKWALLPAPER,bmp_path, win32con.SPIF_SENDWININICHANGE)

def set_wallpaper(img_path):
    #把图片格式统一转换成bmp格式,并放在源图片的同一目录
    img_dir = os.path.dirname(img_path)
    bmpImage = Image.open(img_path)
    new_bmp_path = os.path.join(img_dir,'wallpaper.bmp')
    bmpImage.save(new_bmp_path, "BMP")
    set_wallpaper_from_bmp(new_bmp_path)

if __name__ == '__main__':
    os.chdir("D:\\bing_wallpaper")
    # set latest wallpaper

    #download all wallpaper, used for offline
    #for i in range(500):
    #    get_wallpaper_from_bing(i)

    #download all wallpaper, used for offline
    #for i in range(2, 377):
    #    print("==> %d" % i)
    #    get_wallpaper_from_plmeizi(i)

    try:
        set_wallpaper(get_wallpaper_from_bing(0))
    except:
        # random select a wallpaper
        all_list = os.listdir('.')
        set_wallpaper(random.choice(all_list))