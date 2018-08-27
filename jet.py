#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys


def parse_options(
):
    parser = argparse.ArgumentParser(description="cli arguments for jetcity")
    parser.add_argument(
        '--depart', dest='depart',
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
    return parser.parse_args()


def launch_spider_and_stdout(spider_name, **kwargs):
    p = subprocess.Popen(
        shlex.split(
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


if __name__ == '__main__':
    p = parse_options()
    os.chdir(os.path.join(os.path.dirname(__file__), 'cityjet'))
    print(" DEPARTS ".center(80, '='))
    print(request_flights(**{
        'depart_date': p.depart,
        'from_city': p.from_city,
        'to_city': p.to_city,
    }), end='')
    if not p.return_date:
        sys.exit(0)
    print(" RETURNS ".center(80, '='))
    print(request_flights(**{
        'depart_date': p.return_date,
        'from_city': p.to_city,
        'to_city': p.from_city,
    }), end='')
