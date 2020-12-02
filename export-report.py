#!/usr/bin/python
import sys, getopt
import requests
import csv
from datetime import datetime, timedelta

API_KEY = ''
DOMAIN = ''
EVENT = 'accepted'
LIMIT = 300
DATETIME_FORMAT = '%d %B %Y %H:%M:%S -0000'

def get_logs(start_date, end_date, next_url=None):
    if next_url:
        logs = requests.get(next_url,auth=("api", API_KEY))
    else:
        params = {
            "begin": start_date.strftime(DATETIME_FORMAT),
            "end": end_date.strftime(DATETIME_FORMAT),
            "ascending": "yes",
            "pretty": "yes",
            "limit": LIMIT,
            "event": EVENT,
        }
        logs = requests.get(
            'https://api.mailgun.net/v3/{0}/events'.format(DOMAIN),
            auth=("api", API_KEY),
            params=params
        )
    return logs.json()

def main(argv):
    try:
        opts, args = getopt.getopt(argv, 'k:s:e:d:ev:l', ['key=', 'start=', 'end=', 'domain=', 'event=', 'limit='])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)

    start = datetime.now() - timedelta(2)
    end = datetime.now() - timedelta(1)

    for o, a in opts:
        if o in ("-k", "--key"):
            global API_KEY
            API_KEY = a
        elif o in ("-s", "--start"):
            start = datetime(int(a.split('-')[2]), int(a.split('-')[1]), int(a.split('-')[0]))
        elif o in ("-e", "--end"):
            end = datetime(int(a.split('-')[2]), int(a.split('-')[1]), int(a.split('-')[0]))
        elif o in ("-d", "--domain"):
            global DOMAIN
            DOMAIN = a
        elif o in ("-ev", "--event"):
            global EVENT
            EVENT = a
        elif o in ("-l", "--limit"):
            global LIMIT
            LIMIT = int(a)

    log_items = []
    current_page = get_logs(start, end)

    while current_page.get('items'):
        items = current_page.get('items')
        log_items.extend(items)
        next_url = current_page.get('paging').get('next', None)
        current_page = get_logs(start, end, next_url=next_url)

    keys = log_items[0].keys()
    with open('{0}-{1}.csv'.format(DOMAIN, start.strftime('%Y-%M-%d')), 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(log_items)


if __name__ == "__main__":
   main(sys.argv[1:])
