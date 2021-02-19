from pyzabbix import ZabbixAPI

macros_name = '{$PROXYPATH}'
url = "http://msk-dpro-app351"
login = 'Andrey.Yablochkin'
password = 'Qwerty357'
zapi = ZabbixAPI(url)
zapi.login(login, password)

proxys = {
    'zabbix-proxy05.x5.ru': '90061',
    'msk-dpro-app348.x5.ru': '10257',
    'msk-dpro-app350.x5.ru': '10259',
    'msk-dpro-app349.x5.ru': '10258',
    'msk-kltn-zbx005.x5.ru': '147600',
    'msk-dpro-apl650.x5.ru': '161781',
    'msk-dpro-apl651.x5.ru': '161782'
}

proxys_old = {
    '90061': 'zabbix-proxy05.x5.ru',
    '10257': 'msk-dpro-app348.x5.ru',
    '10258': 'msk-dpro-app349.x5.ru',
    '10259': 'msk-dpro-app350.x5.ru',
    '147600': 'msk-kltn-zbx005.x5.ru',
    '161781': 'msk-dpro-apl650.x5.ru',
    '161782': 'msk-dpro-apl651.x5.ru'
}
wrong_hosts = {
    '90061': [],
    '10257': [],
    '10258': [],
    '10259': [],
    '147600': [],
    '161781': [],
    '161782': []
}
# Получаем id хостов, которым нужно добавить макрос
all_proxy = zapi.do_request('proxy.get', {'output': ['host']})['result']
for proxy in all_proxy:
    hosts_id = zapi.do_request('host.get',
    {
        'search': {'name': 'CC*'},  # Фильтр по названию серверов
        'searchWildcardsEnabled': 'true',
        'proxyids': proxy["proxyid"],
        'output': ['hostid'],
        # 'limit': 1
    })['result']

    all_macros = zapi.do_request('usermacro.get', {
        "hostids": [h["hostid"] for h in hosts_id],
        "searchWildcardsEnabled": True,
        "search": {"macro": "{$PROXYPATH}"},
        "output": ["value", "hostid"]
    })["result"]

    for macros in all_macros:
        if macros["value"] != proxys_old[proxy["proxyid"]]:
            wrong_hosts[proxys[macros['value']]].append(macros['hostid'])

for wrong_proxy, wrong_host in wrong_hosts.items():
    hosts_id = zapi.do_request('host.massupdate',
                               {"hosts": [{"hostid": h} for h in wrong_host],
                                "proxy_hostid": wrong_proxy})
