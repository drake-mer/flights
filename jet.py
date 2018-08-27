#!/usr/bin/env python3

import argparse
import os
import shlex
import subprocess
import sys
import tempfile


def parse_options(
):
    parser = argparse.ArgumentParser(description="cli arguments for jetcity")
    parser.add_argument(
        '--depart', dest='depart', action='store_const',
        help='list flights at this date (YYYYMMDD format) [default=NOW + 10 days]',
    )
    parser.add_argument(
        '--return', dest='return', action='store_const',
        help='list return flights for those dates (YYYYMMDD format) [default=None]',
    )
    parser.add_argument(
        '--from', dest='from_city', action='store_const',
        help='departure city (default: London)',
    )
    parser.add_argument(
        '--to', dest='to_city', action='store_const',
        help='destination city (default: Amsterdam)',
    )
    return parser.parse_args()


def launch_spider_and_stdout(spider_name, **kwargs):
    with tempfile.NamedTemporaryFile() as f:
        p = subprocess.Popen(
            shlex.split(
                'scrapy crawl -o {out_file_name} -t jsonlines --nolog {spider}'.format(
                    spider=spider_name, out_file_name='-'
                ) + ''.join(' -a {key}={value}'.format(key=key, value=value) for key, value in kwargs)
            ),
            stdout=subprocess.PIPE
        )
        stdout, stderr = p.communicate()
        if stderr:
            print(stderr.decode, file=sys.stderr)
        return stdout.decode()


show_flights = lambda date: launch_spider_and_stdout('cityjet', date=date)

# TODO: implement command line option parsing

if __name__ == '__main__':
    os.chdir(os.path.join(os.path.dirname(__file__), 'cityjet'))
    output = launch_spider_and_stdout('cityjet')
    print(output, file=sys.stderr, end='')
