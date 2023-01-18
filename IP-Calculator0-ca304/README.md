# 1. Requirements

Your code will be run by pre-written test software, so adherence to this specification is **required**

- Your code should be in a single python file called `[main.py](http://main.py)`
- Your code should run on [localhost](http://localhost) (127.0.01) on port 8000
- For each endpoint pay attention to the sample JSON shown for the inputs and outputs, the test software will assume this is the JSON structure you are using and fail otherwise.
- Your code should perform the calculations itself. Libraries such as the [ipaddress library](https://docs.python.org/3/library/ipaddress.html) are not allowed.

# 2. Endpoints

## 2.1. IP Calculator

Write an endpoint called `ipcalc` that takes in *JSON* from a post request. The endpoint will take in a JSON object containing an IP address in decimal dot notation. The endpoint should then return:

- The class of the address
- The number of networks for the **class** of the address
- The number of hosts for the **class** of the address
- The first IP address for the class
- The last IP address for the class

### 2.1.1 Sample input JSON

```json
{
    "address":"136.206.18.7"
}
```

Here is an example of how the endpoint would be hit using CURL

```bash
curl --location --request POST '127.0.0.1:8000/ipcalc/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "address":"136.206.18.7"
}'
```

### 2.1.2 Sample output JSON

The endpoint should return the following json structure

```json
{
	"class": "B",
	"num_networks": 16384,
	"num_hosts": 65536,
	"first_address": "128.0.0.0",
	"last_address": "191.255.255.255"
}
```

Class D and class E addresses should return `"N/A"` for the `num_hosts` and `num_networks` field. 

## 2.2. Subnet Calculator

Write an endpoint called `subnet` which will take in a class C or class B address and a subnet mask. The endpoint will return

- The ip address in CIDR notation e.g. `192.168.10.0/26`
- The number of subnets on the network
- The number of addressable hosts per subnet
- The valid subnets
- The broadcast address of each subnet
- The valid hosts on each subnet

### 2.1.1 Sample input JSON

```json
{
	"address": "192.168.10.0",
	"mask": "255.255.255.192"
}
```

Here is an example of how the endpoint would be hit using CURL

```bash
curl --location --request POST '127.0.0.1:8000/subnet/' \
--header 'Content-Type: application/json' \
--data-raw '{
	"address": "192.168.10.0",
	"mask": "255.255.255.192"
}'
```

### 2.1.2 Sample output JSON

The endpoint will return the following json structure

```json
{
	"address_cidr" : "192.168.10.0/26",
	"num_subnets": 4,
	"addressable_hosts_per_subnet": 62,
	"valid_subnets": ["192.168.10.0", "192.168.10.64", "192.168.10.128", "192.168.10.192"],
	"broadcast_addresses": ["192.168.10.63","192.168.10.127","192.168.10.191","192.168.10.255"],
	"first_addresses": ["192.168.10.1","192.168.10.65","192.168.10.129","192.168.10.193"],
	"last_addresses": ["192.168.10.62","192.168.10.126","192.168.10.190","192.168.10.254"]
}
```

## 2.3. Supernet Calculator

Write an endpoint called `supernet` which will take a list of contiguous class C addresses which are to become a supernet.

The endpoint will return

- The network using CIDR notation e.g. `205.100.0.0/22` (the format is the first network number, folloed by a `/` followed by the number of network bits).
- The network mask

### 2.3.1 Sample input JSON

```json
{
    "addresses":["205.100.0.0","205.100.1.0","205.100.2.0","205.100.3.0"]
}
```

Here is an example of how this request would work using CURL

```json
curl --location --request POST '127.0.0.1:8000/supernet/' \
--header 'Content-Type: application/json' \
--data-raw '{
    "addresses":["205.100.0.0","205.100.1.0","205.100.2.0","205.100.3.0"]
}'
```

### 2.3.2 Sample output JSON

```json
{
	"address": "205.100.0.0/22",
	"mask": "255.255.252.0"
}
```
