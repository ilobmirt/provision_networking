## **PROVISION_NETWORKING**
* * *
provision_networking is a role designed to be run within an [ansible](https://www.ansible.com/) playbook. This role is responsible for configuring a custom tailored network for each node within the group listed in the provision_networking role. This role leverages NetworkManager to make this happen.

## Configuring the provision_networking role
* * *
This role is configured through the ***network_provision_playbook_config*** variable in the ***playbook.yml*** file. 
***network_provision_playbook_config*** is a dictionary object that will overlap changes with the actual variable used for the role - ***network_provision_role_config*** . ***network_provision_role_config*** is the full configuration for the role containing every detail about the project. It's not recommended you edit that variable.

## Example Project
* * *
In this example, we want to add a few vlans and bridge them so that these hosts can communicate amongst one another over those vlans. Therefore, we will use the **provision_networking** role to clean up the server and then reimplement the service under the new configuration.

**hosts.ini**
```ini
[network_hosts]
vnode3 ansible_host=█.█.█.3
vnode4 ansible_host=█.█.█.4
vnode5 ansible_host=█.█.█.5
vnode6 ansible_host=█.█.█.6
vnode7 ansible_host=█.█.█.7

[network_hosts:vars]
ansible_user=ansibleuser
ansible_python_interpreter=auto
```

**vars/provision_network.yml**
```yaml
network_provision_playbook_config:
  tasks:
    - PREREQ
    - PROVISION
  networks:
    - name: brvlan10
      type: bridge
      ipv4: disabled
      ipv6: disabled
      status: present
    - name: vlan10-eth0
      type: vlan
      dev: eth0
      ipv4: disabled
      ipv6: disabled
      vlan_id: 10
      master: brvlan10
      status: present
    - name: brvlan20
      type: bridge
      ipv4: disabled
      ipv6: disabled
      status: present
    - name: vlan20-eth0
      type: vlan
      dev: eth0
      ipv4: disabled
      ipv6: disabled
      vlan_id: 20
      master: brvlan20
      status: present
    - name: brvlan30
      type: bridge
      ipv4: disabled
      ipv6: disabled
      status: present
    - name: vlan30-eth0
      type: vlan
      dev: eth0
      ipv4: disabled
      ipv6: disabled
      vlan_id: 30
      master: brvlan30
      status: present
```

**playbook.yml**
```yaml
- hosts: network_hosts
  gather_facts: yes
  
  vars_files:
    - vars/provision_network.yml

  roles:
    - provision_networking
```

## Known Limitations:
***
The following are the current limitations of the role as of the time of this writing (2023-APR-01). Of course though, this code is open source. Feel free to play with this at your heart's content.

- No real fine-tuning with this role on a host-by-host basis

- vxlan + wifi have not been tested (anyone mind trying it out?)

- PREREQ task is Debian centric and does not have a handler that works with other linux families
