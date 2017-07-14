#!/usr/bin/python
import paramiko
import pexpect
import os
import re
import time
import sys
from pexpect import popen_spawn
import pdb

local_log_path = 'D:\\TI_logs\\' if os.name=='nt' else '/home/songsonl/TI_logs'

def download_log_rlab(version, batch):
    os.chdir(local_log_path)
    remotepath = '%s/%s' % (version, batch)
    if (os.path.exists(remotepath+'/apelogs/TS_focus.log1.gz')  \
            or os.path.exists(remotepath+'/apelogs/TS_focus.log1')) \
            and os.path.exists(remotepath+'/InstantStatus.html'):
        print('log for %s exist, abort download.' % remotepath)
        return

    t = paramiko.Transport(("172.21.128.21",22))
    t.connect(username = "rmtlab", password = "rmtlab")
    sftp = paramiko.SFTPClient.from_transport(t)
    localpath =  remotepath
    try:
        os.makedirs( remotepath + "/apelogs/Logs" )
        os.makedirs( remotepath + "/HTML_Temp" )
    except:
        pass

    file_list = [remotepath+'/apelogs/TS_focus.log1.gz',
                remotepath+'/InstantStatus.html',
                remotepath+'/AtcInfo.html']

    for ff in sftp.listdir(remotepath+'/apelogs/Logs'):
        file_list.append(remotepath+'/apelogs/Logs/'+ff)

    for ff in sftp.listdir(remotepath+'/HTML_Temp'):
        file_list.append(remotepath+'/HTML_Temp/'+ff)

    for ff in file_list:
        print('==> download file: %s' % ff)
        sftp.get(ff, ff)
    t.close()
    os.chdir(remotepath+'/apelogs/')
    os.system('gzip -d TS_focus.log1.gz')
    os.chdir(local_log_path)


def download_log_ASB(version, batch):
    os.chdir(local_log_path)
    localpath = '%s/%s' % (version, batch)
    if (os.path.exists(localpath+'/SB_Logs/apelogs/TS_focus.log1.gz')  \
            or os.path.exists(localpath+'/SB_Logs/apelogs/TS_focus.log1')) \
            and os.path.exists(localpath+'/SB_Logs/InstantStatus.html'):
        print('log for %s exist, abort download.' % localpath)
        return

    # search logs path on server
    ret = re.match('SHA_NFXSD_FANTF_FTTU_(.*)_weekly', batch)
    domain_name = ret.group(1)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect("135.251.206.171",22,"atxuser", "alcatel01")
    search_cmd = "find /tftpboot/atx/logs/ASB-NFXSD-FANTF-FTTU-GPON-WEEKLY*/SD_%s -name \"testsummary.log\" | xargs grep \"d %s\"" % (version, domain_name)
    stdin, stdout, stderr = ssh.exec_command(search_cmd)
    output = stdout.readlines()
    ret = re.match('(.*?SB_Logs)/testsummary.log', output[0])
    remotepath = ret.group(1)
    print (version, batch, domain_name, remotepath)
    ssh.close()

    # scp from server
    cmd = 'pscp -r atxuser@135.251.206.171:%s  %s' % (remotepath, localpath)
    print (cmd)
    try:
        os.makedirs(localpath)
    except:
        pass

    #child = pexpect.spawn(cmd)
    #pdb.set_trace()
    child = pexpect.popen_spawn.PopenSpawn(cmd, logfile=sys.stdout)
    index = child.expect([u"(?i)yes/no",u"(?i)password", pexpect.EOF, pexpect.TIMEOUT])
    if index==0:
        child.sendline('yes')
        child.expect(u'(?i)password')
        child.sendline('alcatel01')
    elif index==1:
        child.sendline('alcatel01')

    while 1:
        time.sleep(5)
        index = child.expect([u"(?i)100%",pexpect.EOF, pexpect.TIMEOUT])
        for line in child:
            print (line,)
        if index == 1:
            return

    return


def download_log(version, batch):
    if batch.startswith('SHA'):
        download_log_ASB(version, batch)
    else:
        download_log_rlab(version, batch)



if __name__ == '__main__':
    version, batch = sys.argv[1], sys.argv[2]
    download_log(version, batch)