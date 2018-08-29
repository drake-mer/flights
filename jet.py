#!/usr/bin/env python3

import argparse
import datetime
import json
import os
import pprint
import shlex
import subprocess
import sys


def parse_options(
):
    parser = argparse.ArgumentParser(description="cli arguments for jetcity")
    parser.add_argument(
        '--depart', dest='depart_date',
        help='list flights at this date (YYYYMMDD format) [default=NOW + 10 days]',
    )
    parser.add_argument(
        '--return', dest='return_date',
        help='list return flights for this date (YYYYMMDD format) [default=None]',
    )
    parser.add_argument(
        '--from', dest='from_city', default='London',
        help='departure city (default: London)',
    )
    parser.add_argument(
        '--to', dest='to_city', default='Amsterdam',
        help='destination city (default: Amsterdam)',
    )
    parser.add_argument(
        '--routes', dest='routes', action='store_true',
        help='show the list of available pathes'
    )
    return parser.parse_args()


def launch_spider_and_stdout(spider_name, **kwargs):
    os.chdir(os.path.join(os.path.dirname(__file__), 'cityjet'))
    p = subprocess.Popen(
        shlex.split(
            # dont remove the jsonlines format because it will break
            # the full_scraping function (we need a json per line)
            'scrapy crawl -o {out_file_name} -t jsonlines --nolog {spider}'.format(
                spider=spider_name, out_file_name='-'
            ) + ''.join(
                ' -a {key}={value}'.format(key=key, value=value)
                for key, value in kwargs.items() if value
            )
        ),
        stdout=subprocess.PIPE
    )
    stdout, stderr = p.communicate()
    if stderr:
        print(stderr.decode, file=sys.stderr)
    return stdout.decode()


def request_flights(**kwargs):
    return launch_spider_and_stdout('cityjet', **kwargs)


def airports():
    import requests
    data = json.loads(requests.get(
        'https://www.cityjet.com/cgi-bin/eRetail/airports.json'
    ).content.decode('ascii').lstrip('function(').rstrip(');'))

    airports = {airport['code']: airport for airport in data['airports']}
    travels = [
        tuple(airports[code]['safe_name'] for code in route)
        for route in data['routes']
    ]
    return airports, travels


AIRPORTS, ROUTES = airports()


def check_dest(origin, destination):
    code_map = {
        AIRPORTS[code]['safe_name']: code for code in AIRPORTS
    }
    if origin not in code_map:
        return '{} is not a valid origin'.format(origin), False
    elif destination not in code_map:
        return '{} is not a valid destination'.format(destination), False
    elif (origin, destination) not in ROUTES:
        return 'No flight between {} and {}'.format(origin, destination), False
    else:
        return '', True


def issue_result(
    to_city=None,
    from_city=None,
    depart_date=None,
    kind=None
):
    msg, success = check_dest(from_city, to_city)
    if not success:
        print(msg)
        sys.exit(0)

    print(" {kind} ".format(kind=kind).center(80, '='))
    print(request_flights(**{
        'depart_date': depart_date,
        'from_city': from_city,
        'to_city': to_city,
    }), end='')


def full_scraping(start_date, days=30):
    output = []
    for delta in range(0, days):
        depart_date = start_date + datetime.timedelta(days=delta)
        for depart, arrival in ROUTES:
            for flight in request_flights(
                **{
                    'depart_date': depart_date.strftime("%Y%m%d"),
                    'from_city': depart,
                    'to_city': arrival,
                }
            ).splitlines():
                output.append(json.loads(flight))
    return output


if __name__ == '__main__':
    p = parse_options()
    if p.routes:
        pprint.pprint(ROUTES)
        sys.exit(0)

    issue_result(
        to_city=p.to_city, from_city=p.from_city,
        depart_date=p.depart_date, kind='DEPART'
    )

    if not p.return_date:
        sys.exit(0)

    issue_result(
        to_city=p.from_city, from_city=p.to_city,
        depart_date=p.return_date, kind='RETURN'
    )
