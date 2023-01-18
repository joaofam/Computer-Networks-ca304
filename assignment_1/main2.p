from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Test Code

@app.get("/")
def root():
    return {"message": "Hello World"}

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

# -------------------------------------------------------------------
# IP Calculator

class IPClass(BaseModel):
    address: str

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

# -------------------------------------------------------------------
# Subnet Calculator
# Get ip and mask address and remove . and turn into octest and binary.
# count amount of 1's in binary to form CIDR 

class snClass(BaseModel):
    address: str
    mask : str

@app.post("/subnet")
async def subnet(info: snClass):

    d = {}

    add = info.address
    address = info.address.split('.')
    subnetMask = info.mask.split('.')

    octets = info.address.split('.')

    Binary = '.'.join([bin(int(x)+256)[3:] for x in subnetMask]) # convert mask to binary
    BinaryList = [format(int(x), '08b') for x in subnetMask]




    BinaryStr = "".join(Binary) # join list to string
    CIDR = 0

    for num in BinaryStr:
        if num == '1':
            CIDR = CIDR + 1

    # -------------
    # num of subnets is the mask address turned o binary. Get the last octet and count how many 1's. Then 2 to the power of the amount of 1's
    subnet_bits = 0
    for num in BinaryList[3]:
        if num == str(1):
            subnet_bits = subnet_bits + 1
    num_subnets = 2**subnet_bits
    
    #--------
    # num of addressable hosts per subnet
    unmasked_bits = 0
    for num in BinaryList[3]:
        if num == str(0):
            unmasked_bits = unmasked_bits + 1
    hosts = (2**unmasked_bits - 2)
    
    # -------
    # valid subnets
    valid = []
    mask = int(subnetMask[3]) # 255.255.255.192 displays the lact octet which is 192
    blockSize = (256 - mask) # 256 - 192 = 64

    i = 0
    while i <= mask:
        address[3] = str(i)
        valid.append(".".join(address))
        i = i + blockSize
    
    # ---------
    # broacast addresses

    broadcast = []
    broadcast_bS = blockSize

    x = 63
    while x <= 255:
       address[3] = str(x)
       broadcast.append(".".join(address))
       x = x + broadcast_bS

    last_bc = broadcast[3].split('.')
    last_bc[3] = '255'
    broadcast[3] = '.'.join(last_bc)

    broadcast[3] = broadcast[3][:-3] + '254'

    # ------
    # return dictionary

    d['address_cidr'] = str(add) + '/' + str(CIDR)
    d['num_subnets'] =  num_subnets
    d['addressable_hosts_per_subnet'] = hosts
    d['valid_subnets'] = valid
    d['broadcast_addresses'] = broadcast
    return d



































# Resources
# https://codehandbook.org/post-data-fastapi/
# https://codehandbook.org/post-json-fastapi/
# https://python.plainenglish.io/rest-api-for-beginners-with-python-fastapi-86fa84fcda42
# https://www.kite.com/python/answers/how-to-remove-quotes-from-a-string-in-python#:~:text=replace()%20to%20remove%20all,all%20quotes%20from%20the%20string.
# https://erikberg.com/notes/networks.html
# https://newbedev.com/convert-ip-address-string-to-binary-in-python
# https://stackoverflow.com/questions/19744206/converting-dot-decimal-ip-address-to-binary-python

# @app.post("/getInformation")


# async def getInformation(info: InfoClass):
#    octets = info.address.split('.')
#    
#    return {
#        "octets": octets[0],
#    }