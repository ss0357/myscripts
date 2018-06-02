import wmi


wmiService = wmi.WMI ()
for nic in wmiService.Win32_NetworkAdapterConfiguration (IPEnabled=1):
   print (nic.Caption, nic.IPAddress)

config = {}

config[1] = {'ip': ''}


