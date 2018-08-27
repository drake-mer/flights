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

Try to upgrade in case of trouble.


# Run the code

A script can be found in  the base folder of the project.

You can do:

```
./jet.py --help
```

For accessing the documentation.

# Available Airports for the Company

TODO: this feature is not implemented yet

Get the list of available airports by doing:
```
./jet.py --airports
```

# pricings

To get the available pricings for a round trip between
London and Amsterdam, run:

```
./jet.py --depart=YYYYMMDD --return=YYYYMMDD --from=London --to=Amsterdam
```

If you don't provide the return date, the script assumes that you want 
a one way ticket.

# Possibilities for additional work

Store the results into a database. Get the total list of the flights for
this company on the next month and store this in a database with the
appropriate model. Write an API to serve this, schedule the scraping jobs.
