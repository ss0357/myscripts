import os


slot_map = {
    '58.093': ('1806', '5'),
    '5801.261': ('1807', '1'),
    '5701.345': ('1807', '3'),
    '5202.612': ('1808', '3'),
    '5702.411': ('1808', '4'),
    '5602.573': ('1808', '5'),
    '5801.272': ('1809', '1'),
    '58.111':   ('1809', '2'),
    '5801.274': ('1809', '3'),
}


if os.name == 'nt':
    log_path = r'D:\tmp\check_TI.log'
    local_log_path = 'D:\\TI_logs\\'
    result_path = r'D:\TI_logs\result'
    report_path = r'D:\TI_reports'
else:
    log_path = '/home/atxuser/TI_logs/check_TI.log'
    #local_log_path = os.environ['HOME'] + '/TI_logs/'
    #result_path = os.environ['HOME'] + '/TI_logs/result'
    local_log_path = '/home/atxuser/TI_logs/'
    result_path = '/home/atxuser/TI_logs/result'
    report_path = r'/home/atxuser/TI_reports'

batch_list = {
    'FTTU': ['', ],
    'SETUP': ['FTTU_SETUP_weekly', ],
    'EQMT': ['FTTU_EQMT_weekly', ],
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
    'P2P': ['SHA_NFXSE_FANTG_P2P_A2A_weekly',
            'NFXSE_FANTF_PT_BATCH6_weekly',
            'SHA_NFXSE_FANTF_P2P_COMM_weekly',
            'P2P_weekly'],
}