# gsmarena_scraper 

This script extract the mobile specs from all the phones available in gsmarena.com to a csv file (+ one for each brand).
To avoid spam detection, run with TOR (see below)

## Requirements

- requests
- beautifulsoup4
- lxml
- pandas

## Installation of the virtualenv (recommended)

```
pipenv install
```

## Usage

```
python gsmarena_scraper.py
```

## Run with tor

1. run `docker-compose up -d`
2. run `python gsmarena-scraper.py`

## Help

```
python gsmarena_scraper.py -h
```

```
usage: gsmarena-scraper.py [-h] [--debug]

Scraper gsmarena.

optional arguments:
  -h, --help  show this help message and exit
  --debug     Display debugging information
```
