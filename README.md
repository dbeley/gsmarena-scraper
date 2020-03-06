# gsmarena_scraper

**DEPRECATED** : gsmarena has a much less permissive anti-spam detection now. You will be banned very quickly and the script can't extract more than the first ~100 smartphones (the ban lasts for several days).

This script extract the mobile specs from all the phones available in gsmarena.com to a csv file (+ one for each brand).

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
