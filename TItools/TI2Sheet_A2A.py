#-*- coding: utf-8 -*-

import xlrd,xlwt,ftplib,re,os,sys,urllib2

#download tms file via ftp
#ftp_address = raw_input('please enter the ftp ip address:')
#ftp_user = raw_input('please enter the ftp username:')
#ftp_passwd = raw_input('please enter the ftp password:')

ftp_address = "172.21.128.21"
ftp_user = "rmtlab"
ftp_passwd = "rmtlab"

batch_info = raw_input('please enter the build id and batch name,like: \n57.071 NFXSB_NANTE_REDUND_PORTPROT_weekly \n57.071 NFXSE_FANTF_REDUND_PORTPROT_weekly \n\n')

batch_info = batch_info.split(" ")

ftp_path = "/storage/" + batch_info[0] + r"/" + batch_info[1] + r"/ARIES/RES_ROOT/focus/"

print ftp_path

ftp = ftplib.FTP()
timeout = 60
port = 21
ftp.connect(ftp_address,port,timeout)
ftp.login(ftp_user,ftp_passwd)
print ftp.getwelcome()

ftp.cwd(ftp_path)
#search the tms file
filelist = ftp.nlst()
for file in filelist:
    if re.match(r'(focus|temp).*\.tms',file):
        filename = file
        break

localtms = open('focus.tms', 'wb')
ftp.retrbinary('RETR ' + filename , localtms.write , 1024)
localtms.close()
ftp.quit()


#create a workboot and sheet
currentPath = sys.path[0]
workbook = xlwt.Workbook()
sheetname = 'A2A_WEEKLY'
sheet1 = workbook.add_sheet(sheetname,cell_overwrite_ok=True)

#Define the style for first row
HeaderStyle = xlwt.XFStyle()
HeaderFont = xlwt.Font()
HeaderFont.bold = True
HeaderFont.height= 200
HeaderFont.name= "Times New Roman"

HeaderPattern = xlwt.Pattern()
HeaderPattern.pattern = 1
HeaderPattern.pattern_fore_colour = 5

HeaderBorder = xlwt.Borders()
HeaderBorder.bottom = 1
HeaderBorder.top = 1
HeaderBorder.left = 1
HeaderBorder.right = 1

HeaderStyle.font = HeaderFont
HeaderStyle.pattern = HeaderPattern
HeaderStyle.borders = HeaderBorder

#write first row
TitleRow = ['Mnemonic','ONT Type','Result','Failed Steps','Execution Time','FR ID','ATC/SW/ENV','FR State','New TI','Comments']
col = len(TitleRow)

#set column width
sheet1.col(0).width= 9999
for i in range(1,col):
    sheet1.col(i).width = 2500

#write first row
i = 0
for tmpRow in TitleRow:
    sheet1.write(0, i, tmpRow, HeaderStyle)
    i += 1

#open the tms file
f = open('focus.tms', 'r')

#write case info to sheet
Rows = 1
for line in f:
    j = 0
    line = line.split(';')
    if line[6] == '':
        line[6] = 'None'
    CaseInfo = ( line[4], line[6], line[11], line[12], line[13])
    for info in CaseInfo:
        sheet1.write(Rows,j, info)
        j += 1
    Rows += 1

#set backgroud colcor for Result column
CellPattern1 = xlwt.Pattern()
CellPattern1.pattern = 1
CellPattern1.pattern_fore_colour = 3
CellPattern2 = xlwt.Pattern()
CellPattern2.pattern = 1
CellPattern2.pattern_fore_colour = 2

CellStyle1 = xlwt.XFStyle()
CellStyle1.pattern = CellPattern1
CellStyle2 = xlwt.XFStyle()
CellStyle2.pattern = CellPattern2

csvfilename = batch_info[0]+'_'+batch_info[1]+'.xls'
SaveFile = os.path.join(currentPath,csvfilename)
workbook.save(SaveFile)

book1 = xlrd.open_workbook(SaveFile)
sht1 = book1.sheet_by_index(0)

i = 1
while i < Rows:
    val_col = sht1.col_values(2, i, i+1)
    if val_col[0] == 'OK':
        sheet1.write(i, 2, 'OK', CellStyle1)
    else:
        sheet1.write(i, 2, 'TI', CellStyle2)
    i += 1

workbook.save(SaveFile)

#close and remove file
f.close()
os.remove('focus.tms')

#start mapping known ti
ti_flag = raw_input(r'Do you want to map known TI(yes/no):')
if ti_flag == 'yes':
    tmp_filename = raw_input(r'please enter the existing xls file name:')
    filename2 = os.path.join(currentPath, tmp_filename)
    book2 = xlrd.open_workbook(filename2)
    sht2 = book2.sheet_by_index(0)

    i = 1
    val_col_1 = {}
    val_col_2 = {}
    fr_list = []
    while i < Rows:
        val_col_1['Result'] = sht1.cell_value(i,2)
        #search ti case in sheet1
        if val_col_1['Result'] == 'TI':
            val_col_1['Name'] = sht1.cell_value(i,0)
            val_col_1['Steps'] = sht1.cell_value(i,3)
            #search the case info in sheet2
            j = 1
            while j < sht2.nrows:
                val_col_2['Name'] = sht2.cell_value(j, 0)
                if val_col_1['Name'] == val_col_2['Name']:
                    val_col_2['Result'] = sht2.cell_value(j,2)
                    val_col_2['Steps'] = sht2.cell_value(j,3)
                    #same fr
                    if val_col_2['Result'] == 'TI' and val_col_1['Steps'] == val_col_2['Steps']:
                        val_col_2['Fr'] = sht2.cell_value(j,5)
                        val_col_2['Fr_type'] = sht2.cell_value(j,6)
                        val_col_2['Comments'] = sht2.cell_value(j, 9)
                        sheet1.write(i, 5, val_col_2['Fr'])
                        sheet1.write(i, 6, val_col_2['Fr_type'])
                        sheet1.write(i, 9, val_col_2['Comments'])
                        if re.match(r'^ALU[0-9]{8,8}$', val_col_2['Fr']) and val_col_2['Fr'] not in fr_list:
                            fr_list.append(val_col_2['Fr'])
                        break
                    else:
                        print "case %s in sheet1 TI steps is %s" % (val_col_1['Name'], val_col_1['Steps'])
                        print "case %s in sheet2 TI steps is %s" % (val_col_2['Name'], val_col_2['Steps'])
                        sheet1.write(i, 8, 'yes')
                j += 1
            if j == sht2.nrows:
                sheet1.write(i, 8, 'yes')
        i += 1
    #must save file after any modification
    workbook.save(SaveFile)
    print "known fr list is %s" % fr_list

    link_value = "http://aww.sh.bel.alcatel.be/tools/dslam/cq/cgi-bin/cqReport.cgi?type=FR_IR&display=id,state&"
    i = 0
    for fr_id in fr_list:
        if i == 0:
            link_value = link_value + 'filter=id%20eq%20' + fr_id
            i += 1
        else:
            link_value = link_value + '%20or%20id%20eq%20' + fr_id

    link_value = link_value + '&format=csv'
    print "link is %s" % link_value

    web_username = raw_input('please enter your CIL:')
    web_passwd = raw_input('please enter your CIL password:')   
    
    
    # 创建一个密码管理者
    password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
    top_level_url = "http://aww.sh.bel.alcatel.be"
    # 添加用户名和密码
    password_mgr.add_password(None, top_level_url, web_username,web_passwd)
    # 创建了一个新的handler
    handler = urllib2.HTTPBasicAuthHandler(password_mgr)
    # 创建 "opener" (OpenerDirector 实例)
    opener = urllib2.build_opener(handler)

    #open the link
    response = opener.open(link_value)
    response = response.read()
    response = response.split('\n')
    response.remove('')

    FR_State = {}
    for line in response:
        line = line.split('\t')
        Fr_id = line[0].strip('"')
        Fr_stats = line[1].strip('"')
        FR_State[Fr_id] = Fr_stats

    print FR_State

    #need read sheet again before update fr state
    book1 = xlrd.open_workbook(SaveFile)
    sht1 = book1.sheet_by_index(0)

    #update fr state in excel
    i = 1
    while i < Rows:
        tmp_frid = sht1.cell_value(i, 5)
        if tmp_frid in fr_list:
            sheet1.write(i, 7, FR_State[tmp_frid])
        i += 1

    workbook.save(SaveFile)

#print sht1.nrows
#print sht1.ncols

print 'workbook created ok '+csvfilename


