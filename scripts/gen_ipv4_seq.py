from typing import List, Dict, Any
import sys, yaml, math

# =================================================================================================#
# PYTHON - Generate IPv4 host numbers based on place of the host in the group                      #
# =================================================================================================#

'''
INPUT:

Pipe = should be plaintext YAML of of ....
    * input_hostname: {{ inventory_hostname }}
    * input_play_hosts: {{ ansible_play_hosts_all }}
    * role_data: {{ network_provision_role_config }}

Expect to find our data in ...

network_provision_role_config['networks'][network_index]

PROCCESSING:
Take note of base addresses and max values of IPv4 network

OUTPUT: 

YAML of network_provision_role_config
'''

stdin_raw : str = ''
stdin_dict : dict = {}

# stdin --> multi-line yaml string
with sys.stdin as stdin_yaml:
    yaml_raw = '\n'.join(stdin_yaml.readlines())

# multi-line yaml string --> dict
stdin_dict = yaml.safe_load(yaml_raw)

host_index : int = stdin_dict['input_play_hosts'].index(stdin_dict['input_hostname'])
network_index : int = 0

for current_network in stdin_dict['role_data']['networks']:
    # Skip if ipv4.address and ipv4.gateway nonexistant
    if 'ipv4' not in current_network.keys():
        continue
    if type(current_network['ipv4'])!=type({}):
        continue
    if ('address' not in current_network['ipv4'].keys()) and ('gateway' not in current_network['ipv4'].keys()):
        continue

    # Skip if not # to work with
    if ('#' not in f"{current_network['ipv4']['address']}") and ('#' not in f"{current_network['ipv4']['gateway']}"):
        continue

    # - - - Network is golden. let's work on it

    # This will be important later im sure
    network_index = stdin_dict['role_data']['networks'].index(current_network)
    network_result : list[int] = []

    # Add defaults if ipv4_network_mins is not defined
    if 'ipv4_network_mins' not in current_network:
        current_network.update({'ipv4_network_mins': [0,0,0,1]})
    if 'ipv4_network_maxs' not in current_network :
        current_network.update({'ipv4_network_maxs': [255,255,255,255]})

    # Work with Gateway
    if '#' in f"{current_network['ipv4']['gateway']}":
        gw_split : List[str] = current_network['ipv4']['gateway'].split('.')

        for curr_octet in range(len(gw_split)-1,0,-1):
            gw_split[curr_octet] = f"{gw_split[curr_octet]}".replace('#', f"{current_network['ipv4_network_mins'][curr_octet]}")

        current_network['ipv4']['gateway'] = '.'.join(gw_split)

    # Now work with addresses
    if '#' in f"{current_network['ipv4']['address']}":
        addr_split : List[str] = current_network['ipv4']['address'].split('.')
        network_diffs : List[int] = []
        network_offsets : List[int] = [0,0,0,host_index]
        network_final : List[int] = []
        overflow : int = 0
        calc_octet : int = 0

        # build network diffs
        for (curr_min_ip, curr_max_ip) in zip(current_network['ipv4_network_mins'], current_network['ipv4_network_maxs']):
            network_diffs.append(curr_max_ip-curr_min_ip)
        
        # build network offset
        for curr_octet in range(len(network_offsets)-1,0,-1):
            calc_octet = network_offsets[curr_octet]
            if calc_octet == 0:
                calc_octet = overflow
            if calc_octet == 0:
                break
            overflow = math.floor( calc_octet / network_diffs[curr_octet] )
            network_offsets[curr_octet] = calc_octet % network_diffs[curr_octet]

        # build final host address calc
        for (curr_min_ip, curr_offset_ip) in zip(current_network['ipv4_network_mins'], network_offsets):
            network_final.append(curr_min_ip+curr_offset_ip)

        # Replace the wildcards
        for curr_octet in range(len(addr_split)-1,0,-1):
            addr_split[curr_octet] = f"{addr_split[curr_octet]}".replace('#', f"{network_final[curr_octet]}")

        current_network['ipv4']['address'] = '.'.join(addr_split)

    #Omit the gateway if same
    if current_network['ipv4']['gateway'] == current_network['ipv4']['address']:
        current_network['ipv4'].pop('gateway')

    #We now must replace the old with the new
    stdin_dict['role_data']['networks'][network_index] = current_network

#We're done with the crunch. Lets push off a yaml structure
print(f"{yaml.safe_dump(stdin_dict['role_data'], indent=2)}")
