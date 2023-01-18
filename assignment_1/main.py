from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
import os.path as p
import socket
import struct

app = FastAPI()

# using dictionary in notes

classes={
'A': { 'network_bits': 7,
       'host_bits': 24 },

'B': { 'network_bits': 14,
      'host_bits': 16 },

'C': { 'network_bits': 21,
       'host_bits': 8 },

'D': { 'network_bits': 'N/A',
       'host_bits': 'N/A' },

'E': { 'network_bits': 'N/A',
       'host_bits': 'N/A' },
}

# -------------
# IP Calculator
# -------------

# Hard coded I know however it was my method of how I understood it most and didn't feel a need to apply classes or functions as all values are stable

class IPClass(BaseModel): # assigning inputs as strings
    address: str

# Ip Calc Class
@app.post("/ipcalc")
async def ipcalc(info: IPClass):
    d = {}

    ip = int(info.address.split(".")[0]) # assigning input as variable ip where ip is the first set of number

    # Addressing variables to classes in dictionary above

    A = classes['A']
    B = classes['B']
    C = classes['C']
    D = classes['D']
    E = classes['E']
    
    # if and else statements to determine values of each ip address

    if ip in range(0, 128): # if it is between 0 and 128
        d['class'] = 'A'
        d['num_networks'] = 2 ** A['network_bits']
        d['num_hosts'] = 2 ** A['host_bits']
        d['first_address'] = '0.0.0.0'
        d['last_address'] = '127.255.255.255'

    elif ip in range(128, 192): # if it is between 128 and 192
        d['class'] = 'B'
        d['num_networks'] = 2 ** B['network_bits']
        d['num_hosts'] = 2 ** B['host_bits']
        d['first_address'] = '128.0.0.0'
        d['last_address'] = '191.255.255.255'
        
    elif ip in range(192, 224): # if it is between 192 and 224
        d['class'] = 'C'
        d['num_networks'] = 2 ** C['network_bits']
        d['num_hosts'] = 2 ** C['host_bits']
        d['first_address'] = '192.0.0.0'
        d['last_address'] = '223.255.255.255'

    elif ip in range(224, 240): # if it is between 224 and 240
        d['class'] = 'D'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '224.0.0.0'
        d['last_address'] = '239.255.255.255'

    else: # if between 240 and 255
        d['class'] = 'E'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '240.0.0.0'
        d['last_address'] = '255.255.255.255'
    
    return d # return dictionary with outputs

# ------------------
# Subnet Calculator
# ------------------

class snClass(BaseModel): # assining inputs as strings
    address: str
    mask : str

# subnet Class

@app.post("/subnet")
async def subnet(info: snClass):

    d = {} # Dictionary to store outputs

    add = info.address # assigning the input address as add
    address = info.address.split('.') # assinging input split by . as address
    subnetMask = info.mask.split('.') # assigning input mask by . ass subnetMask


    binary = '.'.join([bin(int(x)+256)[3:] for x in subnetMask]) # convert mask to binary
    binaryList = [format(int(x), '08b') for x in subnetMask] # making a binary list
    binaryStr = "".join(binary) # join list to string

    # CIDR Calculator (works for all classes)

    CIDR = 0 # assign CIDR as 0

    for num in binaryStr: # if number in the binary string is 1, count CIDR + 1
        if num == '1': # if the digit 1 is found in binary add it to CIDR
            CIDR += 1 


    # if the subnet is class C

    if subnetMask[2] == "255":

        # number of subnets on the network calculator

        subnetBits = 0 # subnetBits variable to count number of subnets
        for num in binaryList[3]: # iterating through the last elements of the binary list
            if num == str(1): # if the num is equal to 1 add 1 to subnets
                subnetBits += 1
        numSubnets = 2 ** subnetBits # numSubnets variable is created to calculatre the number of subnets (2 to the power of the subnet bits)
    
        # number of addressable hosts per subnet calculator

        unmaskedBits = 0 # unmaskedBits variable created to keep count of unmasked bits
        for num in binaryList[3]:
            if num == str(0): # if the number is the digit 0 add 1 to variable unmaskedBits
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2) # hosts variable created to calculate number of addressable hosts (2 to the power of addressable bits then take away two)

        # valid subnets calculator

        valid = [] # list called valid made 
        mask = int(subnetMask[3]) # Displays lact element in the mask. E.g. 255.255.255.192 displays the lact elements which is 192
        blockSize = (256 - mask) # blockSize variable created to calculate the block size. E.g. 256 take away incremenate value. e.g. 256 - 192 = 64

        i = 0
        while i <= mask: # loop until last element in mask found
            address[3] = str(i) # assign last element of address as 0 (i)
            valid.append(".".join(address)) # place last current value in list called valid
            i += blockSize # keep looping through block size until mask value is reached
    
        # broacast addresses calculator

        broadcast = [] # list called broadcast is created to store broadcast addresses

        x = blockSize - 1 # assign correct block size value for broadcast addresses as x
        while x <= 255: # iterate through until the value of 255 is reached
            address[3] = str(x) # assign the last element of the address as x
            broadcast.append(".".join(address)) # after each iteration place it into the list broadcast
            x += blockSize # keep looping through the block size until 255 is reached

        # Last broadcast value is always 255 so we assign 255 to the last element of broadcast

        lastBroadcast = broadcast[-1].split('.') # split last eleemnt of broadcast by a .
        lastBroadcast[-1] = '255' # assign last value as 255
        broadcast[-1] = '.'.join(lastBroadcast) # join it back to the list by using a .

        # first address calculator
        
        first = [] # assign a list called first to store first addresses

        y = blockSize + 1 # assign new variable y as the correct block size to be used for first addresses
        x = 1 
        
        address[3] = str(x) # assign the last element of address to 1
        first.append('.'.join(address)) # place it into the list first

        while y <= 255: # itereate until 255 is reached by the block size
            address[3] = str(y) # assign first address value in loop as the block size
            first.append('.'.join(address)) # while itereating through values place into list
            y += blockSize # keep looping though until block size reaches 255

        # last address calculator

        last = [] # assign variable last as a list

        p = hosts  # assign p as last value of hosts that we calculated above
        while p <= 255: # itereate until hosts value reaches 255
            address[3] = str(p) # address third element as the hosts value
            last.append('.'.join(address)) # place into list
            p += blockSize # itterate through hosts plus the blocksizes until 255 is reached

    # if subnet is class B ( inputs used:
    #                                    "address": "144.89.250.123",
    #                                    "mask": "255.255.192.0"
    #                      )

    elif subnetMask[3] != "255":

        # number of subnets on the network calculator

        subnetBits = 0 # same as above however this time we iterate with the third element of the binary list
        for num in binaryList[2]:
            if num == str(1):
                subnetBits +=  1
        numSubnets = 2 ** subnetBits

        # number of addressable hosts per subnet calculator
        
        unmaskedBits = 0 # same as above however this time we iterate with the third element of the binary list
        for num in binaryList[2]:
            if num == str(0):
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2)

        # valid subnets calculator

        address[-1] = '0'

        valid = []
        mask = int(subnetMask[2]) # Displays third element in the mask. E.g. 255.255.192.000 displays the third elements which is 192
        blockSize = (256 - mask)


        i = 0
        while i <= mask:
            address[2] = str(i)
            valid.append(".".join(address))
            i += blockSize
        
        # broacast addresses calculator

        broadcast = []
        broadcast_bS = blockSize

        address[-1] = '255' # assign last element or last item in list as 255

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x) # same as above however this time we iterate with the third element 
            broadcast.append(".".join(address))
            x += broadcast_bS

        lastBroadcast = broadcast[-1].split('.') # get last element of broadcast address and split it by .
        lastBroadcast[-2] = '255' # assign second last element in broadcast address as 255
        lastBroadcast[-1] = '255' # assign last element in broadcast address as 255
        broadcast[-1] = '.'.join(lastBroadcast) # join back by a .

        # first address calculator

        first = []
        first_block = blockSize

        y = first_block + 1
        
        address[-1] = '1' # assign last value as 1 on all addresses

        i = 0 
        while i <= 255:
            address[2] = str(i) # same method as class C however this time we assign 0 to the third element of the address
            first.append('.'.join(address))
            i += blockSize

        # last address calculator

        address[-1] = '254' # assign last value as 254 on all addresses

        last = []

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x) # same method as class C however this time we assign x to the third element of the address
            last.append('.'.join(address))
            x += blockSize
        

    # Dictionary outputs

    d['address_cidr'] = str(add) + '/' + str(CIDR)
    d['num_subnets'] =  numSubnets
    d['addressable_hosts_per_subnet'] = hosts
    d['valid_subnets'] = valid
    d['broadcast_addresses'] = broadcast
    d['first_addresses'] = first
    d['last_addresses'] = last
    return d

# -------------------
# Supernet Calculator
# -------------------
        
class supernetClass(BaseModel): # assigning input as a list
    addresses: List[str]

# Supernet Class

@app.post("/supernet")
async def supernet(info: supernetClass):

    d = {} # Dictionary to store outputs
    ipAddresses = [] # List to store
    mainList = []

    addressList = info.addresses # assigning input as variable addressList

    for ips in addressList:
        ipAddresses = ips.split(".") # splitting by a .
        Binary = '.'.join([bin(int(x)+256)[3:] for x in ipAddresses]) # converting ip address to a binary
        binaryStr = "".join(Binary) # lists are joined to a string
        mainList.append(binaryStr)

    prefix = p.commonprefix(mainList) # using common prefix method to gather the longest prefix in order to calculate mask

    networkMask = prefix.replace('0','1') # replace all 0's with 1's in order to get network mask

    # CIDR calculator

    CIDR = 0
    for num in networkMask:
        if num == '1':
            CIDR += 1

    # Netmask calculator

    netMask = socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - CIDR)) & 0xffffffff)) # using socket and inet_ntoa to convert the CIDR to netmask

    # Dictionary outputs

    d['address'] = addressList[0] + '/' + str(CIDR)
    d['mask'] = netMask

    return d # return dictionary


''' 
- Resources Used to Complete Project - 
https://codehandbook.org/post-data-fastapi/
https://codehandbook.org/post-json-fastapi/
https://python.plainenglish.io/rest-api-for-beginners-with-python-fastapi-86fa84fcda42
https://www.kite.com/python/answers/how-to-remove-quotes-from-a-string-in-python#:~:text=replace()%20to%20remove%20all,all%20quotes%20from%20the%20string.
https://erikberg.com/notes/networks.html
https://newbedev.com/convert-ip-address-string-to-binary-in-python
https://stackoverflow.com/questions/19744206/converting-dot-decimal-ip-address-to-binary-python
https://stackoverflow.com/questions/63262197/extract-a-list-from-the-request-body-sent-to-fastapi-application
https://stackoverflow.com/questions/61788169/how-to-get-common-prefix-of-strings-in-a-list
https://stackoverflow.com/questions/30919275/inserting-period-after-every-3-chars-in-a-string
https://pythontic.com/modules/socket/inet_ntoa
https://stackoverflow.com/questions/23352028/how-to-convert-a-cidr-prefix-to-a-dotted-quad-netmask-in-python
'''