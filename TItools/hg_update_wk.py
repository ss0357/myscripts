import paramiko
import logging
import sys

log_path = r'D:\songsonl\hg_update.log'
logger = logging.getLogger("AppName")
formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
file_handler = logging.FileHandler(log_path)
file_handler.setFormatter(formatter)
console_handler = logging.StreamHandler(sys.stdout)
console_handler.formatter = formatter
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.setLevel(logging.INFO)

logger.info('#'*80)
logger.info('===> connect to work station...')
# 建立一个sshclient对象
ssh = paramiko.SSHClient()
# 允许将信任的主机自动加入到host_allow 列表，此方法必须放在connect方法的前面
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
# 调用connect方法连接服务器
ssh.connect(hostname='135.251.206.240', port=22, username='songsonl', password='soup.633')

# 执行命令

logger.info('#'*80)
logger.info('===> start hg pull -u:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/robot; hg pull -u')
logger.info(stdout.read().decode())

logger.info('===> start hg log -l 5:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/robot; hg log -l 5')
logger.info(stdout.read().decode())

logger.info('===> start hg head:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/robot; hg head')
logger.info(stdout.read().decode())

logger.info('#'*80)
logger.info('===> start hg pull -u:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/atc; hg pull -u')
logger.info(stdout.read().decode())

logger.info('===> start hg log -l 5:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/atc; hg log -l 5')
logger.info(stdout.read().decode())

logger.info('===> start hg head:')
stdin, stdout, stderr = ssh.exec_command('cd /repo1/songsonl/ATC_CODE/atc; hg head')
logger.info(stdout.read().decode())

# 关闭连接
ssh.close()