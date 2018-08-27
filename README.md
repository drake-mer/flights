# CityJet.com Scraping

The CityJet website relies heavily on javascript.

There is not a directly available API endpoint for fetching the data, thus
we need to reverse engineer the way the data are fetched.

We have basically two choices:

- use a headless browser to simulate the fetching of data (can result
  in heavy load since a lot of requests will be issued inside the browser).

- use a scraping application to emulate the HTTP browser (harder but
  the performance load is really low and the process of refining the
  data is much more controlled.

Let's start coding...

# After some coding

I decided to go with Scrapy as I don't have much experience with this tool,
so it has been really rewarding to work on this project.

# Dependencies


Running:

```bash
pip install --user scrapy
```

Should be enough to get started

This script is well tested with scrappy 1.5 and python 3.6 under Archlinux.

# Run the code

A script can be found in  the base folder of the project.

You can do:

```
./jet.py --help
```

For accessing the documentation.

# Available routes for the company

You can Get the list of available air routes (and
hence of valid arguments for the script) by doing:

```
./jet.py --routes
```

# Get travel prices for a given round trip

To get the available pricings for a round trip between
London and Amsterdam, you can run:

```
./jet.py --depart=YYYYMMDD --return=YYYYMMDD --from=London --to=Amsterdam
```

If you don't provide the return date, the script assumes that you want
a one way ticket.

# Full scraping

With the following snippet, I have been able to retrieve the whole
content of the website pricing for 30 days in a little bit less than
30 minutes.

The content of the scraping is in the `september_flights.json` file
(approximately 3000 pricings)

The work could be sped up also by parallelizing (for example, one
could launch a thread/process for each travel route, having thus approximately
10 runners fetching the data). In case of a parallelization, the data store
must then be accessed in a concurrent fashion (typically, we need a database).

```python
import datetime
import jet
start_date = datetime.datetime.now() + datetime.timedelta(days=5)
result = jet.full_scraping(start_date)
```

# Possibilities for additional work

- Store the results into a database with the air routes
- Store the result for the month to come on all the possible routes (30 x 12 x number of flights per day)
- Serve this through a convenient API and scrape periodically the data to keep the infos up to date.
