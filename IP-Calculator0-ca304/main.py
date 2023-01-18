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

class IPClass(BaseModel): 
    address: str

# Ip Calc Class
@app.post("/ipcalc")
async def ipcalc(info: IPClass):
    d = {}

    ip = int(info.address.split(".")[0])

    A = classes['A']
    B = classes['B']
    C = classes['C']
    D = classes['D']
    E = classes['E']

    if ip in range(0, 128):
        d['class'] = 'A'
        d['num_networks'] = 2 ** A['network_bits']
        d['num_hosts'] = 2 ** A['host_bits']
        d['first_address'] = '0.0.0.0'
        d['last_address'] = '127.255.255.255'

    elif ip in range(128, 192):
        d['class'] = 'B'
        d['num_networks'] = 2 ** B['network_bits']
        d['num_hosts'] = 2 ** B['host_bits']
        d['first_address'] = '128.0.0.0'
        d['last_address'] = '191.255.255.255'
        
    elif ip in range(192, 224):
        d['class'] = 'C'
        d['num_networks'] = 2 ** C['network_bits']
        d['num_hosts'] = 2 ** C['host_bits']
        d['first_address'] = '192.0.0.0'
        d['last_address'] = '223.255.255.255'

    elif ip in range(224, 240):
        d['class'] = 'D'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '224.0.0.0'
        d['last_address'] = '239.255.255.255'

    else:
        d['class'] = 'E'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '240.0.0.0'
        d['last_address'] = '255.255.255.255'
    
    return d

# ------------------
# Subnet Calculator
# ------------------

class snClass(BaseModel):
    address: str
    mask : str
@app.post("/subnet")
async def subnet(info: snClass):

    d = {}

    add = info
    address = info.address.split('.')
    subnetMask = info.mask.split('.')


    binary = '.'.join([bin(int(x)+256)[3:] for x in subnetMask])
    binaryList = [format(int(x), '08b') for x in subnetMask]
    binaryStr = "".join(binary) # join list to string

    CIDR = 0

    for num in binaryStr:
        if num == '1':
            CIDR += 1 

    if subnetMask[2] == "255":

        subnetBits = 0
        for num in binaryList[3]:
            if num == str(1):
                subnetBits += 1
        numSubnets = 2 ** subnetBits

        unmaskedBits = 0
        for num in binaryList[3]:
            if num == str(0):
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2)

        valid = []  
        mask = int(subnetMask[3])
        blockSize = (256 - mask)

        i = 0
        while i <= mask:
            address[3] = str(i)
            valid.append(".".join(address))
            i += blockSize

        broadcast = []

        x = blockSize - 1
        while x <= 255:
            address[3] = str(x)
            broadcast.append(".".join(address))
            x += blockSize 

        lastBroadcast = broadcast[-1].split('.')
        lastBroadcast[-1] = '255'
        broadcast[-1] = '.'.join(lastBroadcast)
        
        first = []

        y = blockSize + 1
        x = 1 
        
        address[3] = str(x)
        first.append('.'.join(address))

        while y <= 255:
            address[3] = str(y)
            first.append('.'.join(address))
            y += blockSize

        last = []

        p = hosts
        while p <= 255:
            address[3] = str(p) 
            last.append('.'.join(address))
            p += blockSize

    elif subnetMask[3] != "255":

        subnetBits = 0
        for num in binaryList[2]:
            if num == str(1):
                subnetBits +=  1
        numSubnets = 2 ** subnetBits
        
        unmaskedBits = 0
        for num in binaryList[2]:
            if num == str(0):
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2)

        address[-1] = '0'

        valid = []
        mask = int(subnetMask[2])
        blockSize = (256 - mask)

        i = 0
        while i <= mask:
            address[2] = str(i)
            valid.append(".".join(address))
            i += blockSize

        broadcast = []
        broadcast_bS = blockSize

        address[-1] = '255'

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x)
            broadcast.append(".".join(address))
            x += broadcast_bS

        lastBroadcast = broadcast[-1].split('.')
        lastBroadcast[-2] = '255'
        lastBroadcast[-1] = '255'
        broadcast[-1] = '.'.join(lastBroadcast)

        first = []
        first_block = blockSize

        y = first_block + 1
        
        address[-1] = '1'

        i = 0 
        while i <= 255:
            address[2] = str(i)
            first.append('.'.join(address))
            i += blockSize

        address[-1] = '254'

        last = []

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x)
            last.append('.'.join(address))
            x += blockSize

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
        
class supernetClass(BaseModel):
    addresses: List[str]

@app.post("/supernet")
async def supernet(info: supernetClass):

    d = {}
    ipAddresses = []
    mainList = []

    addressList = info.addresses

    for ips in addressList:
        ipAddresses = ips.split(".")
        Binary = '.'.join([bin(int(x)+256)[3:] for x in ipAddresses])
        binaryStr = "".join(Binary)
        mainList.append(binaryStr)

    prefix = p.commonprefix(mainList)

    networkMask = prefix.replace('0','1')

    CIDR = 0
    for num in networkMask:
        if num == '1':
            CIDR += 1

    netMask = socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - CIDR)) & 0xffffffff)) # using socket and inet_ntoa to convert the CIDR to netmask

    d['address'] = addressList[0] + '/' + str(CIDR)
    d['mask'] = netMask

    return d


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
'''from fastapi import FastAPI
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

class IPClass(BaseModel): 
    address: str

# Ip Calc Class
@app.post("/ipcalc")
async def ipcalc(info: IPClass):
    d = {}

    ip = int(info.address.split(".")[0])

    A = classes['A']
    B = classes['B']
    C = classes['C']
    D = classes['D']
    E = classes['E']

    if ip in range(0, 128):
        d['class'] = 'A'
        d['num_networks'] = 2 ** A['network_bits']
        d['num_hosts'] = 2 ** A['host_bits']
        d['first_address'] = '0.0.0.0'
        d['last_address'] = '127.255.255.255'

    elif ip in range(128, 192):
        d['class'] = 'B'
        d['num_networks'] = 2 ** B['network_bits']
        d['num_hosts'] = 2 ** B['host_bits']
        d['first_address'] = '128.0.0.0'
        d['last_address'] = '191.255.255.255'
        
    elif ip in range(192, 224):
        d['class'] = 'C'
        d['num_networks'] = 2 ** C['network_bits']
        d['num_hosts'] = 2 ** C['host_bits']
        d['first_address'] = '192.0.0.0'
        d['last_address'] = '223.255.255.255'

    elif ip in range(224, 240):
        d['class'] = 'D'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '224.0.0.0'
        d['last_address'] = '239.255.255.255'

    else:
        d['class'] = 'E'
        d['num_networks'] = 'N/A'
        d['num_hosts'] = 'N/A'
        d['first_address'] = '240.0.0.0'
        d['last_address'] = '255.255.255.255'
    
    return d

# ------------------
# Subnet Calculator
# ------------------

class snClass(BaseModel):
    address: str
    mask : str
@app.post("/subnet")
async def subnet(info: snClass):

    d = {}

    add = info
    address = info.address.split('.')
    subnetMask = info.mask.split('.')


    binary = '.'.join([bin(int(x)+256)[3:] for x in subnetMask])
    binaryList = [format(int(x), '08b') for x in subnetMask]
    binaryStr = "".join(binary) # join list to string

    CIDR = 0

    for num in binaryStr:
        if num == '1':
            CIDR += 1 

    if subnetMask[2] == "255":

        subnetBits = 0
        for num in binaryList[3]:
            if num == str(1):
                subnetBits += 1
        numSubnets = 2 ** subnetBits

        unmaskedBits = 0
        for num in binaryList[3]:
            if num == str(0):
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2)

        valid = []  
        mask = int(subnetMask[3])
        blockSize = (256 - mask)

        i = 0
        while i <= mask:
            address[3] = str(i)
            valid.append(".".join(address))
            i += blockSize

        broadcast = []

        x = blockSize - 1
        while x <= 255:
            address[3] = str(x)
            broadcast.append(".".join(address))
            x += blockSize 

        lastBroadcast = broadcast[-1].split('.')
        lastBroadcast[-1] = '255'
        broadcast[-1] = '.'.join(lastBroadcast)
        
        first = []

        y = blockSize + 1
        x = 1 
        
        address[3] = str(x)
        first.append('.'.join(address))

        while y <= 255:
            address[3] = str(y)
            first.append('.'.join(address))
            y += blockSize

        last = []

        p = hosts
        while p <= 255:
            address[3] = str(p) 
            last.append('.'.join(address))
            p += blockSize

    elif subnetMask[3] != "255":

        subnetBits = 0
        for num in binaryList[2]:
            if num == str(1):
                subnetBits +=  1
        numSubnets = 2 ** subnetBits
        
        unmaskedBits = 0
        for num in binaryList[2]:
            if num == str(0):
                unmaskedBits += 1
        hosts = (2 ** unmaskedBits - 2)

        address[-1] = '0'

        valid = []
        mask = int(subnetMask[2])
        blockSize = (256 - mask)

        i = 0
        while i <= mask:
            address[2] = str(i)
            valid.append(".".join(address))
            i += blockSize

        broadcast = []
        broadcast_bS = blockSize

        address[-1] = '255'

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x)
            broadcast.append(".".join(address))
            x += broadcast_bS

        lastBroadcast = broadcast[-1].split('.')
        lastBroadcast[-2] = '255'
        lastBroadcast[-1] = '255'
        broadcast[-1] = '.'.join(lastBroadcast)

        first = []
        first_block = blockSize

        y = first_block + 1
        
        address[-1] = '1'

        i = 0 
        while i <= 255:
            address[2] = str(i)
            first.append('.'.join(address))
            i += blockSize

        address[-1] = '254'

        last = []

        x = blockSize - 1
        while x <= 255:
            address[2] = str(x)
            last.append('.'.join(address))
            x += blockSize

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
        
class supernetClass(BaseModel):
    addresses: List[str]

@app.post("/supernet")
async def supernet(info: supernetClass):

    d = {}
    ipAddresses = []
    mainList = []

    addressList = info.addresses

    for ips in addressList:
        ipAddresses = ips.split(".")
        Binary = '.'.join([bin(int(x)+256)[3:] for x in ipAddresses])
        binaryStr = "".join(Binary)
        mainList.append(binaryStr)

    prefix = p.commonprefix(mainList)

    networkMask = prefix.replace('0','1')

    CIDR = 0
    for num in networkMask:
        if num == '1':
            CIDR += 1

    netMask = socket.inet_ntoa(struct.pack(">I", (0xffffffff << (32 - CIDR)) & 0xffffffff)) # using socket and inet_ntoa to convert the CIDR to netmask

    d['address'] = addressList[0] + '/' + str(CIDR)
    d['mask'] = netMask

    return d


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
