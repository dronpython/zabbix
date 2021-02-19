from pyzabbix import ZabbixAPI, ZabbixAPIException

template_id = '45250'    # Указать id шаблона, который необходимо добавить
url = 'zabbix_url'
login = 'login'
password = 'password'

zapi = ZabbixAPI(url)
zapi.login(login, password)
hosts_id = zapi.do_request('host.get', {
    'search': {'name': 'ora*'},  # Фильтр по названию серверов
    'searchWildcardsEnabled': 'true',  # Чтобы фильтр был доступен
    'output': ['hostid'] # Выводим только hostid
})['result']


if len(hosts_id) > 100:  # Если много узлов сети, то скрипт виснет. Необходимо обновлять частями.
    step = 100
    count_step = len(hosts_id) // step
    uncount = len(hosts_id) % step

    a = 0
    b = step
    unupdated_hosts = []
    for i in range(count_step):
        ids = []
        print('Шаг: ' + str(i + 1) + '\n' + str(a + 1) + ' - ' + str(b))
        for j in range(a, b):
            ids.append(hosts_id[j])
        a = a + step
        b = b + step
        try:
            updated = zapi.do_request('host.massadd', {
                'hosts': ids,
                'templates': [{'templateid': template_id}]
            })['result']
        except ZabbixAPIException as e:
            print('На шаге: ' + str(i) + ' возникла ошибка:\n' + str(e))
            unupdated_hosts.append(ids)
            pass
        print('Updating hosts: ' + str(ids) + 'completed')
    if uncount != 0:
        ids = []
        print('Шаг: ' + str(count_step + 1) + '\n' + str(len(hosts_id) - uncount + 1) + ' - ' + str(len(hosts_id)))
        for i in range(len(hosts_id) - uncount, len(hosts_id)):
            ids.append(hosts_id[i])
        try:
            updated = zapi.do_request('host.massadd', {
                'hosts': ids,
                'templates': [{'templateid': template_id}]
            })['result']
            print('Добавление шаблона успешно завершено')
        except ZabbixAPIException as e:
            print('На последнем шаге возникла ошибка:\n' + str(e))
            print('Необновленные узлы:' + str(unupdated_hosts))
            pass
    print('Добавление шаблона успешно завершено')
else:
    try:
        updated = zapi.do_request('host.massadd', {
            'hosts': hosts_id,
            'templates': [{'templateid': template_id}]
        })
    except ZabbixAPIException as e:
        print('Возникла ошибка: ' + str(e))
        print('Необновленные узлы:' + str(hosts_id))
    print('Шаблон с templateid: ' + str(template_id) + ' успешно добавлен к узлам: ' + str(hosts_id))
