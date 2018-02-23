import os


slot_map = {
    '58.093': ('1806', '5'),
    '5801.261': ('1807', '1'),
    '5701.345': ('1807', '3'),
}


if os.name == 'nt':
    log_path = r'D:\tmp\check_TI.log'
    local_log_path = 'D:\\TI_logs\\'
    result_path = r'D:\TI_logs\result'
else:
    log_path = os.environ['HOME'] + '/TI_logs/check_TI.log'
    local_log_path = os.environ['HOME'] + '/TI_logs/'
    result_path = os.environ['HOME'] + '/TI_logs/result'


batch_list = {
    'FTTU': ['', ],
    'SETUP': ['FTTU_SETUP_weekly', ],
    'EQMT': ['FTTU_L3FWD_weekly', 'FTTU_EQMT_weekly'],
    'L3FWD': ['FTTU_L3FWD_weekly',],
    'L2FWD': ['FTTU_L2FWD_weekly',],
    'QOS': ['FTTU_QOS_weekly',],
    'SUBMGMT': ['FTTU_SUBMGMT_weekly',],
    'MCAST': ['FTTU_MCAST_weekly',],
    'TRANSPORT': ['FTTU_TRANSPORT_weekly',],
    'MGMT': ['FTTU_MGMT_weekly',],
    'REDUND': ['NFXSD_FANTF_REDUND_weekly', ],
    'PORTPROT': ['', ],
    'A2A': ['NFXSB_NANTE_REDUND_PORTPROT_weekly', 'NFXSE_FANTF_REDUND_PORTPROT_weekly'],
}