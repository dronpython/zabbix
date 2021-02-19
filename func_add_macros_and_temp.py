
from pyzabbix import ZabbixAPI, ZabbixAPIException
import time

template_id = '10103'    # Указать id шаблона, который необходимо добавить
url = 'zbx_url'
login = 'login'
password = 'pwd'
macros = '{$macros}'
zapi = ZabbixAPI(url)
zapi.login(login, password)


def get_hosts():
    hosts_id = zapi.do_request('host.get',
                               {
                                   'search': {'name': '*'},  # Фильтр по названию серверов
                                   'searchWildcardsEnabled': 'true',
                                   "selectParentTemplates": ["templateid"],
                                   'output': ['parentTemplates']
                               }
                               )['result']
    return hosts_id


def get_interfaces(hosts):
    interfaces = [itf for itf in zapi.do_request('hostinterface.get',
                                                 {
                                                     'hostids': hosts,
                                                     'output': ['ip', 'main', 'hostid']
                                                 }
                                                 )['result'] if itf['main'] == '1']
    return interfaces


def templates_check(hosts_id, template_id):
    hosts = list()
    for host in hosts_id:
        templates = list()
        for template in host['parentTemplates']:
            templates.append(template['templateid'])
        if template_id not in templates:
            hosts.append(host['hostid'])
    return hosts


def host_new_ip(ip_list, value):   # Создаем словарь вида {id_host: ip_maininterface} и изменяем ip на +10
    host_ip_dict = dict()
    for i in ip_list:
        ip = i['ip'].split('.')
        last_oktet = int(ip[3]) + value
        new_ip = (str(ip[0]) + '.' + str(ip[1]) + '.' + str(ip[2]) + '.' + str(last_oktet))
        host_ip_dict[i['hostid']] = new_ip
    return host_ip_dict


def update_hosts(host_ip_dict, template_id):
    count = 0
    for host, ip in host_ip_dict.items():
        count += 1
        print('Обновлено ' + str(count) + 'из ' + str(len(host_ip_dict.keys())))
        if count == 2:
            all_time = round(time.time() - start_time) * len(host_ip_dict.keys())
            print('Примерное время выполнения скрипта:')
            print(time.strftime("%H:%M:%S", time.gmtime(all_time)))
        try:
            start_time = time.time()
            q = zapi.do_request('host.massadd', {
                'hosts': [host],  # Фильтр по названию серверов
                'macros': [{'macro': macros,
                            'value': ip}],
                'templates': [{'templateid': template_id}]})
        except ZabbixAPIException as e:
            print(f'Возникла ошибка при добавлении к hostid {host}: {e}')
    print('Updating complete')


if __name__ == "__main__":
    begin = time.time()
    hosts = get_hosts()
    hosts_wo_template = templates_check(hosts, template_id)
    all_interfaces = get_interfaces(hosts_wo_template)
    ip_host_dict = host_new_ip(all_interfaces, 10)
    update_hosts(ip_host_dict, template_id)
    all_time = time.time() - begin
    print(all_time)
