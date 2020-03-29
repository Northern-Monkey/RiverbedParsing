'''
This script takes a list of Riverbed Steelheads, and pulls the optimisation stats.
The resulting data is parsed and fed in to a csv file for review. Individual host files 
are created in the same directory as the script and runtime files that contain more info
that is useful to assess the performance of the SH.
Created by Phil Lees
'''

from getpass import getpass # Need this to obfuscate the PW
import netmiko # Need this for SSH
import re # Need this to use the IP regex
import textfsm # Need this for parsing the output

# Connect function
def make_connection (ip, username, password):
        return netmiko.ConnectHandler(device_type='cisco_ios', ip=ip, username=username, password=password)

# Make sure its an ip
def get_ip (input):
     return(re.findall(r'(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?).){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)', input))

# Read the list of Riverbed IP's
def get_ips (file_name):
     for line in open(file_name, 'r').readlines():
        line = get_ip(line)
        for ip in line:
          ips.append(ip)

ips = []
get_ips("steelheads.txt")

#Login creds
username = input('Enter the Username: ')
password = getpass()

# Once parsed, push the results to the output file
outfile_name = open("outfile.csv", "w+")
outfile = outfile_name

# Open the FSM template
template = open("BandwidthTemplate")

# Create the csv column headers
outfile.write("WAN Data (Bytes);LAN Data(Bytes);Reduction (%);Reduction-Peak (%);Reduction Peak Date;Capacity Increase (Mutiplier);Host\n")

# Loop through all the Steelheads
for ip in ips:
    try:
        print ('Connecting to Steelhead IP: ' + str(ip))
        net_connect = make_connection(ip, username, password)
# First just collect the optimisation stuff
        band = net_connect.send_command('show stats bandwidth all bi-directional month')
# Get FSM to parse the results using the template
        re_table = textfsm.TextFSM(template)
        fsm_results = re_table.ParseText(band)
# Start writing the results to csv
        counter = 0
        for row in fsm_results:
            print(row)
            for s in row:
                outfile.write("%s;" %s)
            outfile.write(str(ip) + "\n")
            counter += 1
# Log some info to console        
        print("Write %d records" % counter)
# Whilst were here, collect some other useful stuff
        opt = net_connect.send_command('show stats traffic opti bi month')
        passthru =  net_connect.send_command('show stats traffic pass month')
        bandw = net_connect.send_command('show stats bandwidth all bi-directional month')
# Write it to a text file using IP address as the filename
        f= open(ip + '.txt','w+')
        f.write('Optimized Traffic\r\n' + str(opt) + '\r\n' + 'Passthrough Traffic\r\n' + str(passthru) + '\r\n' + 'All Bandwidth\r\n' + str(bandw))
        f.close()
# End the SSH session
        net_connect.disconnect()
# Bit more console logging
        print('Stats collected Successfully')
# If its a dodgy host, let me know
    except Exception:
          print ("******* Couldn't connect to: " + str(ip) + " *******")
          pass
    
