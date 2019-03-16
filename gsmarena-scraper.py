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
        print(f"Brand : {brand_name}")
        url_brand_base = f"https://www.gsmarena.com/{brand_name}-f-{brand_number}-0"

        while(True):
            url_brand_page = f"{url_brand_base}-p{index_page}.php"
            # logger.debug(url_brand_page)
            index_page = index_page + 1
            html_doc_page = requests.get(url_brand_page).content
            soup_page = BeautifulSoup(html_doc_page, features='lxml')
            print(f"Page URL : {url_brand_page}")

            if soup_page.find('div', {'class': 'section-body'}).select('li'):
                for smartphone in soup_page.find('div', {'class': 'section-body'}).find_all('li'):
                    smartphone = smartphone.find('a')
                    smartphone_dict = dict()
                    href_smartphone = smartphone['href']
                    img_smartphone = smartphone.find('img')['src']
                    url_smartphone = f"https://www.gsmarena.com/{href_smartphone}"
                    logger.debug(f"url_smartphone : {url_smartphone}")
                    smartphone_dict["Lien"] = url_smartphone
                    smartphone_dict["Image"] = img_smartphone
                    html_doc_smartphone = requests.get(url_smartphone).content
                    soup_smartphone = BeautifulSoup(html_doc_smartphone, features='lxml')
                    name = str(soup_smartphone.find('h1').find_all(text=True, recursive=False)[0])
                    print(f"Model : {name}")
                    smartphone_dict["Nom"] = name

                    if soup_smartphone.select('td', {'class': 'nfo'}):
                        smartphone_dict["Fans"] = soup_smartphone.find('li', {'class': 'help-fans'}).find('strong').find(text=True)
                        smartphone_dict["Popularité"] = soup_smartphone.find('li', {'class': 'help-popularity'}).find_all(text=True)[2]
                        smartphone_dict["Hits"] = soup_smartphone.find('li', {'class': 'help-popularity'}).find_all(text=True)[4]
                        # smartphone_dict["Hits"] = soup_smartphone.find('li', {'class': 'help-popularity'}).find('span').find(text=True)
                        ecran = soup_smartphone.find('li', {'class': 'help-display'}).find_all(text=True)
                        if ecran:
                            try:
                                logger.debug(f"Écran : {ecran}")
                                smartphone_dict["Taille_écran"] = ecran[2]
                                smartphone_dict["Définition_écran"] = ecran[3]
                            except Exception as e:
                                logger.debug(f"ecran : {e}")
                        ram = soup_smartphone.find('li', {'class': 'help-expansion'}).find_all(text=True)
                        if ram:
                            try:
                                logger.debug(f"RAM : {ram}")
                                smartphone_dict["RAM"] = ' '.join([ram[i] for i in [3, 4]])
                                smartphone_dict["SOC"] = ram[-1]
                            except Exception as e:
                                logger.debug(f"ram : {e}")
                        batterie = soup_smartphone.find('li', {'class': 'help-battery'}).find_all(text=True)
                        if batterie:
                            try:
                                logger.debug(f"Batterie: {batterie}")
                                smartphone_dict["Batterie"] = ' '.join([batterie[i] for i in [3, 4]])
                            except Exception as e:
                                logger.debug(f"batterie : {e}")
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
                        logger.error(f"{name} : td class=nfo not found")
            else:
                logger.error(f"{name} : td class=nfo not found")
                break

    # logger.debug(smartphones_dict)
    df = pd.DataFrame.from_dict(smartphones_dict, orient='index')
    df.to_csv("smartphones.csv", sep=";")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper revuedepresse.')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
