import os
from pyzabbix import ZabbixAPI
from dotenv import load_dotenv

load_dotenv()

zabbix_ip = os.getenv("IP_SERVER-ZABBIX")

hosts_api = [
    {"ip": os.getenv("IP_BR-EDGE-01"), "name": "BR-EDGE-01"},
    {"ip": os.getenv("IP_HQ-CORE-01"), "name": "HQ-CORE-01"},
    {"ip": os.getenv("IP_HQ-ACC-01"), "name": "HQ-ACC-01"},
    {"ip": os.getenv("IP_INET-SIM-01"), "name": "INET-SIM-01"},
    {"ip": os.getenv("IP_HQ-FW-01"), "name": "HQ-FW-01"}
]

zapi = ZabbixAPI(f"http://{zabbix_ip}/zabbix")
try:
    zapi.login("Admin", "zabbix")
    print(f"Connecté à Zabbix {zapi.api_version()}")
except Exception as e:
    print(f"Erreur login : {e}")
    exit()

template_name = "Cisco IOS by SNMP"
template_data = zapi.template.get(filter={"host": [template_name]})
template_id = template_data[0]['templateid']

group_name = "Lab-Network"
group_id=''
group_data = zapi.hostgroup.get(filter={"name": [group_name]})
if not group_data:
    new_group = zapi.hostgroup.create(name=group_name)
    group_id = new_group['groupids'][0]
    print(f"Groupe créé : {group_name}")
else:
    group_id = group_data[0]['groupid']
    print(f"Utilisation du groupe existant : {group_name} (ID: {group_id})")

for device in hosts_api:
    if not device["ip"]:
        continue
    existing_hosts = zapi.host.get(filter={"host": device["name"]})

    if existing_hosts:
        print(f"L'hôte '{device['name']}' existe déjà (ID: {existing_hosts[0]['hostid']})...")
        continue
    try:
        host = zapi.host.create(
            host=device["name"],
            status=0,
            interfaces=[{
                "type": 2,
                "main": 1,
                "useip": 1,
                "ip": device["ip"],
                "dns": "",
                "port": "161",
                "details": {
                    "version": 2, 
                    "community": "ZBX-LAB-RO" 
                }
            }],
            groups=[{"groupid": group_id}],
            templates=[{"templateid": template_id}]
        )
        print(f" {device['name']} créé (ID: {host['hostids'][0]})")

    except Exception as e:
        print(f" Erreur sur {device['name']} : {e}")

zapi.user.logout()