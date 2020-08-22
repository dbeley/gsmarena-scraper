# gsmarena_scraper

This script extract the mobile specs from all the phones available in gsmarena.com to a csv file (+ one for each brand).

To avoid spam detection, run with TOR (see below).

## Requirements

- docker
- docker-compose

## Installation

Clone the repository
```
git clone https://github.com/dbeley/gsmarena-scraper
cd gsmarena-scraper
```

Install the python dependencies
```
pip install requests beautifulsoup4 lxml pandas pysocks steam
```

If you prefer, you can also install the requirements in a virtual environment with pipenv (in order to run the python script, you will need to use `pipenv run python gsmarena-scraper.py` instead of `python gsmarena-scraper.py`):
```
pipenv install
```

## Usage

Run the docker container containing the tor proxy (you can tweak the torrc configuration file if you want, but the defaults should be good):
```
docker-compose up -d
```

Run the script:
```
python gsmarena-scraper.py
```

After completion, you can stop the docker container with `docker-compose down`.

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
