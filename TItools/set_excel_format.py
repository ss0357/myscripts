import xlrd
import xlwt
from xlutils.copy import copy
from xlwt import *
import os
from log import logger



def set_excel_format(input_file, output_file):
    logger.info('===> format excel file: %s ---> %s' % (input_file, output_file))
    #os.chdir(r'D:\tmp')
    #input_file = 'FTTU_EQMT_raw.xls'
    #output_file = 'FTTU_EQMT.xls'
    rb = xlrd.open_workbook(input_file)

    #print (rb.sheet_names())
    sheet1_name = rb.sheet_names()[0]

    # 根据sheet索引或者名称获取sheet内容
    r_sheet = rb.sheet_by_index(0) # sheet索引从0开始
    #r_sheet1 = rb.sheet_by_name('sheet1')


    # sheet的名称，行数，列数
    #print (r_sheet.name,r_sheet.nrows,r_sheet.ncols)


    wb = copy(rb)
    w_sheet = wb.get_sheet(0)

    style = XFStyle()

    #Define the style for first row
    HeaderStyle = xlwt.XFStyle()
    HeaderFont = xlwt.Font()
    HeaderFont.bold = True
    HeaderFont.height= 200
    HeaderFont.name= u'微软雅黑'
    #"Times New Roman"
    #fnt.name = u'微软雅黑'
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

    for x in range(r_sheet.ncols):
        w_sheet.write_merge(0,0,x,x, r_sheet.row_values(0)[x], style=HeaderStyle)

    column_width = [1000, 2500, 2500, 2500, 11500, 7500, 2500, 2500, 2500, 2500, 2500, 2500, 3500, 12500, 1000]
    for x in range(r_sheet.ncols):
        w_sheet.col(x).width = column_width[x]


    #set backgroud colcor for Result column
    CellFont = xlwt.Font()
    CellFont.bold = False
    CellFont.height= 160
    CellFont.name= u'微软雅黑'

    CellBorder = xlwt.Borders()
    CellBorder.bottom = 1
    CellBorder.top = 1
    CellBorder.left = 3
    CellBorder.right = 3


    CellPattern0 = xlwt.Pattern()
    CellPattern0.pattern = 1
    CellPattern0.pattern_fore_colour = 1

    CellPattern1 = xlwt.Pattern()
    CellPattern1.pattern = 1
    CellPattern1.pattern_fore_colour = 22

    CellPattern2 = xlwt.Pattern()
    CellPattern2.pattern = 1
    CellPattern2.pattern_fore_colour = 47

    CellStyle0 = xlwt.XFStyle()
    CellStyle0.pattern = CellPattern0
    CellStyle0.font = CellFont
    CellStyle0.borders = CellBorder

    CellStyle1 = xlwt.XFStyle()
    CellStyle1.pattern = CellPattern1
    CellStyle1.font = CellFont
    CellStyle1.borders = CellBorder

    CellStyle2 = xlwt.XFStyle()
    CellStyle2.pattern = CellPattern2
    CellStyle2.font = CellFont
    CellStyle2.borders = CellBorder



    for x in range(r_sheet.ncols):
        for y in range(1, r_sheet.nrows):
            #logger.info('flag: %s' % r_sheet.row_values(y)[14])
            flag = int(r_sheet.row_values(y)[14])
            if flag==0:
                CellStyle = CellStyle0
            elif flag==1:
                CellStyle = CellStyle1
            elif flag==2:
                CellStyle = CellStyle2
            else:
                assert 0

            w_sheet.write_merge(y,y,x,x, r_sheet.row_values(y)[x], style=CellStyle)

            
    #for y in range(99):
    #    CellPattern1 = xlwt.Pattern()
    #    CellPattern1.pattern = 1
    #    CellPattern1.pattern_fore_colour = y
    #    CellStyle1.pattern = CellPattern1
    #    w_sheet.write_merge(y,y,14,14, label=str(y), style=CellStyle1)
            
            
    wb.save(output_file)