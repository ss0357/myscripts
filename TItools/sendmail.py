class sendmail():
  def __init__(self,content="TI"):
    self.content = content

  def sending(self,content):
    self.content = content
    import smtplib
    from email.mime.text import MIMEText
    from email.header import Header
    sender = 'songsong.li@alcatel-sbell.com.cn'
    receivers = 'songsong.li@alcatel-sbell.com.cn'
    message = MIMEText(self.content, 'plain', 'utf-8')
    #message['From'] = Header("Yuefeng Sun@alcatel-sbell.com.cn", 'utf-8')
    #message['To'] =  Header("Yuefeng Sun", 'utf-8')
    message['Subject'] = Header(self.content, 'utf-8')

    try:
      smtpObj = smtplib.SMTP('135.251.206.35')
      smtpObj.sendmail(sender, receivers, message.as_string())
      print "Mail sent success!"
    except smtplib.SMTPException:
      print "Mail sent fail!"


if __name__ == '__main__':
  sm = sendmail()
  sm.sending('test')