import time
import logging
import argparse
import requests
from bs4 import BeautifulSoup
import pandas as pd


logger = logging.getLogger()
temps_debut = time.time()


def main():
    args = parse_args()

    url_index = "https://www.gsmarena.com/makers.php3"
    html_doc_index = requests.get(url_index).content
    soup_index = BeautifulSoup(html_doc_index, features='lxml')
    smartphones_dict = dict()
    index_dict = 0
    for brand in soup_index.find('div', {'class': 'st-text'}).find_all('a'):
        index_page = 1
        brand = brand['href'].rsplit('-', 1)
        brand_name = brand[0]
        brand_number = brand[1].split('.')[0]
        print(f"Extracting {brand_name}")
        url_brand_base = f"https://www.gsmarena.com/{brand_name}-f-{brand_number}-0"

        working = True
        while(working):
            try:
                url_brand_page = f"{url_brand_base}-p{index_page}.php"
                logger.debug(url_brand_page)
                index_page = index_page + 1
                html_doc_page = requests.get(url_brand_page).content
                soup_page = BeautifulSoup(html_doc_page, features='lxml')

                if soup_page.find('div', {'class': 'section-body'}).select('li'):
                    for smartphone in soup_page.find('div', {'class': 'section-body'}).find_all('li'):
                        smartphone = smartphone.find('a')
                        smartphone_dict = dict()
                        href_smartphone = smartphone['href']
                        img_smartphone = smartphone.find('img')['src']
                        url_smartphone = f"https://www.gsmarena.com/{href_smartphone}"
                        logger.debug(url_smartphone)
                        smartphone_dict["Lien"] = url_smartphone
                        smartphone_dict["Image"] = img_smartphone
                        logger.debug("requests.get(url_smartphone)")
                        html_doc_smartphone = requests.get(url_smartphone).content
                        logger.debug("BeautifulSoup(html_doc_smartphone)")
                        soup_smartphone = BeautifulSoup(html_doc_smartphone, features='lxml')
                        name = str(soup_smartphone.find('h1').find_all(text=True, recursive=False)[0])
                        logger.debug(f"Name : {name}")
                        smartphone_dict["Nom"] = name

                        if soup_smartphone.select('td', {'class': 'nfo'}):
                            for spec in soup_smartphone.find_all('td', {'class': 'nfo'}):
                                try:
                                    type = str(spec['data-spec'])
                                    value = ''.join(spec.find_all(text=True, recursive=False))
                                    smartphone_dict[type] = value
                                    logger.debug(f"{type} : {value}")
                                except Exception:
                                    pass
                            smartphones_dict[index_dict] = smartphone_dict
                            index_dict = index_dict + 1
                        else:
                            logger.debug("soup_smartphone.select = False")
                            break
                else:
                    logger.debug("soup_page.select = False")
                    break
            except Exception:
                logger.debug(f"Page {url_brand_page} invalid")
                working = False

    logger.debug(smartphones_dict)
    df = pd.DataFrame.from_dict(smartphones_dict, orient='index')
    df.to_csv("smartphones.csv", sep=";")

    logger.debug("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper revuedepresse.')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
