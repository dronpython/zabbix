from clickhouse_driver import Client
from sshtunnel import SSHTunnelForwarder
import psycopg2
import logging


def zabbix_stores(ts):
    with SSHTunnelForwarder(
            ('ip', 22),
            ssh_username="login",
            ssh_password="password",
            remote_bind_address=('host', port)
    ) as server:
        server.start()
        local_port = str(server.local_bind_port)
        db_credentials = {
            'host': 'localhost',
            'user': 'zabbix',
            'password': 'pass',
            'database': 'zabbix',
            'port': local_port
        }
        try:
            group_id = '44' if ts == 'TCK' else '42'

            connection = psycopg2.connect(**db_credentials)
            cursor = connection.cursor()
            cursor.execute(f'''select split_part(host, '-', 2) from hosts
where hostid in (select hg1.hostid from hosts_groups hg1
join hosts_groups hg2 on hg1.hostid=hg2.hostid
where hg1.groupid = 41 
and hg2.groupid = {group_id})''')
            data = cursor.fetchall()
            if len(data) > 0:
                tcx = [store_id[0] for store_id in data]
                return tcx
            else:
                print('No data')
        except Exception as e:
            print("Catch error while connecting: {}".format(e))
        finally:
            cursor.close()
            connection.close()


def ch_operations(ts, operation, stores_id=None):

    # with open_tunnel(
    #         ('ip', port),
    #         ssh_username="user",
    #         ssh_password="pass",
    #         remote_bind_address=('ip', port)
    # ) as server:
    client = Client('db_ip', port, password='pass', compression=True)

    if operation == 'insert':
        for store_id in stores_id:
            try:
                client.execute('''INSERT INTO X5_BMS_RAW.GKBF_STORES VALUES ('{0}', '{1}', '')'''.format(store_id, ts))
            except Exception as e:
                print(str(id) + ' - Catch error {}'.format(e))

    elif operation == 'select':
        data = client.execute(f"select STORE_ID from X5_BMS_RAW.GKBF_STORES WHERE TS = '{ts}' ")
        if len(data) > 0:
            stores = [store_id[0] for store_id in data]
            return stores
        else:
            print('No data')
            return []

    elif operation == 'delete':
        client.execute('''ALTER TABLE X5_BMS_RAW.GKBF_STORES_P ON CLUSTER 'x5_bms_sharded' DELETE 
        WHERE TS = '{0}' AND STORE_ID in {1}'''.format(ts, tuple(stores_id)))

    else:
        print('Support only: select, insert, delete')


def main():
    # Config logs
    log_file_name = 'actualizer.log'
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        filename=log_file_name, level=logging.INFO)
    logging.info('Запуск актуализатора...')

    zabbix_tcx_id = zabbix_stores('TCX')
    zabbix_tck_id = zabbix_stores('TCK')
    tck_stores_gkbf = ch_operations('TCK', 'select')
    tcx_stores_gkbf = ch_operations('TCX', 'select')
    
    # Добавляем новые store_id TCK
    new_id_tck = set(zabbix_tck_id) - set(tck_stores_gkbf)
    if new_id_tck:
        logging.info('Найдено новых магазинов TCK: {}\n SAP_ID: {} \n'.format(len(new_id_tck), new_id_tck))
        ch_operations('TCK', 'insert', new_id_tck)
    else:
        logging.info("Новые магазины TCK не найдены")

    # Добавляем новые store_id TCX
    new_id_tcx = set(zabbix_tcx_id) - set(tcx_stores_gkbf)
    if new_id_tcx:
        logging.info('Найдено новых магазинов TCK: {}\n SAP_ID: {} \n'.format(len(new_id_tcx), new_id_tcx))
        ch_operations('TCX', 'insert', new_id_tcx)
    else:
        logging.info('Новые магазины TCX не найдены')

    # Удаляем лишние store_id TCK
    tck_to_delete = set(tck_stores_gkbf) - set(zabbix_tck_id)
    if tck_to_delete:
        logging.info('Магазины TCK под удаление: {}\n SAP_ID: {} \n'.format(len(tck_to_delete), tck_to_delete))
        ch_operations('TCK', 'delete', tck_to_delete)
    else:
        logging.info('Магазины под удаление не найдены')

    # Удаляем лишние store_id TCX
    tcx_to_delete = set(tcx_stores_gkbf) - set(zabbix_tcx_id)
    if tcx_to_delete:
        logging.info('Магазины TCX под удаление: {}\n SAP_ID: {} \n'.format(len(tcx_to_delete), tcx_to_delete))
        ch_operations('TCX', 'delete', tcx_to_delete)
    else:
        logging.info('Магазины TCX под удалениене найдены')


if __name__ == '__main__':
    main()
