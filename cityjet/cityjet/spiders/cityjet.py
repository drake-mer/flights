#!/usr/bin/env python3

import datetime
import json


import scrapy
import scrapy.spiders
import scrapy.http


class SpiderError(Exception):
    pass


class CityJetSpider(scrapy.Spider):
    name = "cityjet"

    airports_url = "https://www.cityjet.com/cgi-bin/eRetail/airports.json"
    first_form_page = "https://www.cityjet.com"

    def __init__(
        self,
        from_city='London',
        to_city='Amsterdam',
        depart_date=None,
        return_date=None,
        *args, **kwargs
    ):
        super(CityJetSpider, self).__init__(*args, **kwargs)

        self.from_city = from_city
        self.to_city = to_city
        self.depart_date = (
            (datetime.datetime.now() + datetime.timedelta(days=10)) if not depart_date
            else datetime.datetime.strptime(depart_date, "%Y%m%d")
        )
        self.return_date = None  # disable this option for now
        self.options = None

    def start_requests(self):
        yield scrapy.Request(
            self.airports_url,
            callback=self._parse_airports_and_fill_request_options
        )
        yield scrapy.Request(
            self.first_form_page,
            callback=self._submit_first_form
        )

    def _parse_available_flights(self, response):
        try:
            data = json.loads(
                response.xpath(
                    '//script[contains(., "var generatedJSon")]'
                ).re(r'generatedJSon.*String\(\'(.*)\'\)')[0]
            )
        except (json.JSONDecodeError, IndexError):
            raise SpiderError("Missing data after getting the list of flights"
                              "One of the requests probably failed.")

        yield from _parse_data_set(data)

    def _submit_second_form(self, response):
        yield scrapy.http.FormRequest.from_response(
            response,
            formxpath='//form['
                '@action="'
                'https://book.cityjet.com/plnext/CityJetairlines/Override.action'
            '"]',
            callback=self._parse_available_flights
        )

    def _submit_first_form(self, response):
        yield scrapy.http.FormRequest.from_response(
            response,
            formxpath='//form[@action="https://www.cityjet.com/book/go/"]',
            formdata=self.options,
            callback=self._submit_second_form
        )

    def _parse_airports_and_fill_request_options(self, response):
        data = json.loads(
            response.body.decode('ascii').lstrip('function(').rstrip(');')
        )
        self.airports = {
            ar['code']: ar for ar in data['airports']
        }
        airport_mapping = {
            v['shortname']: k  for k, v in self.airports.items()
        }
        self.options = self._fill_api_options(airport_mapping)

    def _fill_api_options(self, airport_mapping):
        # fill missing values for the form
        # content is huge but heh, nevermind
        if (
            self.from_city not in airport_mapping
            or self.to_city not in airport_mapping
        ):
            raise SpiderError("One of the required cities is not available")

        return {
            'triptype': 'return' if self.return_date else 'oneway',
            '_from': airport_mapping[self.from_city],
            '_to': airport_mapping[self.to_city],
            '_auto_from': self.from_city,
            '_auto_to': self.to_city,
            '_depart': self.depart_date.strftime("%d/%m/%y"),
            '_return': (
                '' if not self.return_date
                else self.return_date.strftime("%d/%m/%y")
            ),
            '_depday': self.depart_date.strftime("%d"),
            '_depmonthyear': self.depart_date.strftime("%Y-%m"),
            '_retday': (
                self.return_date.strftime("%d") if self.return_date
                else ''
            ),
            '_retmonthyear': (
                self.return_date.strftime("%Y-%m") if self.return_date
                else ''
            ),
            'B_ANY_TIME_1': 'TRUE',
            'B_ANY_TIME_2': 'TRUE',
            'B_DATE_1': self.depart_date.strftime("%Y%m%d0000"),
            'B_DATE_2': (
                self.return_date.strftime("%Y%m%d0000") if self.return_date
                else ''
            ),
            'B_FLOW': 'flight',
            'B_LOCATION_1': airport_mapping[self.from_city],
            'E_LOCATION_1': airport_mapping[self.to_city],
            'TRIP_TYPE': 'R' if self.return_date else 'O',
            'flexMyDates': '0'  # dont put flexible depart date at all
        }


def _parse_data_set(data):
    """Just parse the weird CityJet JSON."""
    def flight_number(flight):
        # list_segment is just a correspondance
        return '+'.join(
            f['airline']['code'] + f['flight_number']
            for f in flight['list_segment']
        )

    def ticket_class(pricing):
        return pricing['fare_family']['brand_name']

    def flight_dates(flight):
        first_segment = flight['list_segment'][0]
        last_segment = flight['list_segment'][-1]
        departure = first_segment['b_date_date'] + first_segment['b_date_time']
        arrival = last_segment['e_date_date'] + last_segment['e_date_time']
        return departure, arrival

    def origin(flight):
        return flight['list_segment'][0]['b_location']['location_name']

    def destination(flight):
        return flight['list_segment'][-1]['e_location']['location_name']

    def price(pricing):
        return pricing['list_pnr'][0]['list_pnr_price'][0]['total_amount']

    def currency(pricing):
        return pricing['list_pnr'][0]['list_pnr_price'][0]['currency']['code']

    data_set = data['list_tab']
    all_the_flights = []
    for flight_list in data_set['list_proposed_bound']:
        all_the_flights += flight_list['list_flight']

    flight_dict = {f['flight_id']: f for f in all_the_flights}

    for pricing in data_set['list_recommendation']:
        possible_flights = []
        for possible_bound in pricing['list_bound']:
            possible_flights += possible_bound['list_flight']

        for flight in possible_flights:
            flight = flight_dict[flight['flight_id']]
            departure, arrival = flight_dates(flight)
            yield FlightTicket(
                flight_number=flight_number(flight),
                ticket_class=ticket_class(pricing),
                depart_date=departure,
                arrival_date=arrival,
                origin=origin(flight),
                destination=destination(flight),
                pricing=price(pricing),
                currency=currency(pricing),
            )


class FlightTicket(scrapy.Item):
    flight_number = scrapy.Field()
    ticket_class = scrapy.Field()
    depart_date = scrapy.Field()   # local time in YYYYMMDDHHMM format
    arrival_date = scrapy.Field()  # local time in YYYYMMDDHHMM format
    origin = scrapy.Field()
    destination = scrapy.Field()
    pricing = scrapy.Field()
    currency = scrapy.Field()


