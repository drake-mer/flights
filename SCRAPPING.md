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

A running script can be found in  the `cityjet_crawler/` folder.

You can do:

```
./jet.py --help
```

For accessing the documentation.

You need to get the list of available cities for this script,
you can have it by running:

```
./jet.py --airports
```

To get the available pricings for a round trip between
London and Amsterdam, run:

```
./jet.py --depart=YYYYMMDD --return=YYYYMMDD --from=London --to=Amsterdam
```

If you don't provide the return date, the script assumes that you want 
a one way ticket.

Have fun.
