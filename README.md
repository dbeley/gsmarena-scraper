# gsmarena_scraper

**This scraper was recently almost completely rewritten. It should now work fine.**

This script extract the mobile specs from all the phones available in gsmarena.com to a csv file (+ one for each brand).

## Requirements

- python + pip

## Installation

Clone the repository:
```
git clone https://github.com/dbeley/gsmarena-scraper
cd gsmarena-scraper
```

Install the python dependencies:
```
pip install requests beautifulsoup4 lxml pandas
```

## Usage

Run the script:
```
python gsmarena-scraper.py
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

## Files exported

The exported files will be placed in a folder named Exports. The `all-brands_exports.csv` will contain the data of all brands.
