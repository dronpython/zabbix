#!python

import requests
import sys
import logging


def send_message(alert):
    token = 'token'
    url = 'http://telegram_or_proxy_url/bot{}/sendMessage'.format(token)
    try:
        r = requests.post(url, alert)
        if r.status_code == 200:
            logging.info('Message successfully sent')
        else:
            logging.error('Got {} error_code. Info: \n{}'.format(r.status_code, r.text))
    except Exception as e:
        logging.error('Error while sending message {}'.format(e))


if __name__ == '__main__':
    log_file_name = 'telegram_alert.log'
    logging.basicConfig(format=u'%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                        filename=log_file_name, level=logging.INFO)
    logging.info('Parsing arguments..')
    to, head, message = sys.argv[1:]
    logging.info('Arguments:{}, {}, []'.format(to, head, message))
    alert = {'chat_id': to, 'text': '''*{}*\n{}'''.format(str(head), str(message)), 'parse_mode': 'markdown'}
    logging.info('Sending message..')
    send_message(alert)
