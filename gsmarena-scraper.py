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
    brands = soup_index.find('div', {'class': 'st-text'}).find_all('a')
    # logger.debug(brands)
    soup_index.decompose()
    for brand in brands:
        index_page = 1
        brand = brand['href'].rsplit('-', 1)
        brand_name = str(brand[0])
        brand_id = str(brand[1].split('.')[0])
        print(f"Brand : {brand_name}")
        url_brand_base = f"https://www.gsmarena.com/{brand_name}-f-{brand_id}-0"

        while(True):
            url_brand_page = f"{url_brand_base}-p{index_page}.php"
            # logger.debug(url_brand_page)
            index_page = index_page + 1
            html_doc_page = requests.get(url_brand_page).content
            soup_page = BeautifulSoup(html_doc_page, features='lxml')
            print(f"Page URL : {url_brand_page}")

            if soup_page.find('div', {'class': 'section-body'}).select('li'):
                smartphones = soup_page.find('div', {'class': 'section-body'}).find_all('li')
                soup_page.decompose()
                for smartphone in smartphones:
                    smartphone = smartphone.find('a')
                    smartphone_dict = dict()
                    href_smartphone = str(smartphone['href'])
                    img_smartphone = str(smartphone.find('img')['src'])
                    url_smartphone = f"https://www.gsmarena.com/{href_smartphone}"
                    logger.debug(f"url_smartphone : {url_smartphone}")
                    smartphone_dict["Link"] = url_smartphone
                    smartphone_dict["Image"] = img_smartphone
                    html_doc_smartphone = requests.get(url_smartphone).content
                    soup_smartphone = BeautifulSoup(html_doc_smartphone, features='lxml')
                    name = str(soup_smartphone.find('h1').find_all(text=True, recursive=False)[0])
                    print(f"Model : {name}")
                    smartphone_dict["Name"] = name

                    if soup_smartphone.select('td', {'class': 'nfo'}):
                        smartphone_dict["Fans"] = str(soup_smartphone.find('li', {'class': 'help-fans'}).find('strong').find(text=True))
                        smartphone_dict["Popularity"] = str(soup_smartphone.find('li', {'class': 'help-popularity'}).find_all(text=True)[2])
                        smartphone_dict["Hits"] = str(soup_smartphone.find('li', {'class': 'help-popularity'}).find_all(text=True)[4])
                        ecran = soup_smartphone.find('li', {'class': 'help-display'}).find_all(text=True)
                        if ecran:
                            try:
                                # logger.debug(f"Screen : {ecran}")
                                smartphone_dict["Screen_size"] = str(ecran[2])
                                smartphone_dict["Scree_resolution"] = str(ecran[3])
                            except Exception as e:
                                # logger.debug(f"Screen : {e}")
                        ram = soup_smartphone.find('li', {'class': 'help-expansion'}).find_all(text=True)
                        if ram:
                            try:
                                # logger.debug(f"RAM : {ram}")
                                smartphone_dict["RAM"] = ' '.join([ram[i] for i in [3, 4]])
                                smartphone_dict["SOC"] = str(ram[-1])
                            except Exception as e:
                                # logger.debug(f"RAM : {e}")
                        batterie = soup_smartphone.find('li', {'class': 'help-battery'}).find_all(text=True)
                        if batterie:
                            try:
                                # logger.debug(f"Battery : {batterie}")
                                smartphone_dict["Battery"] = ' '.join([batterie[i] for i in [3, 4]])
                            except Exception as e:
                                # logger.debug(f"Battery : {e}")
                        for spec in soup_smartphone.find_all('td', {'class': 'nfo'}):
                            try:
                                type = str(spec['data-spec'])
                                value = ''.join(spec.find_all(text=True, recursive=False))
                                smartphone_dict[type] = value
                                # logger.debug(f"{type} : {value}")
                            except Exception:
                                pass
                        smartphones_dict[index_dict] = smartphone_dict
                        index_dict = index_dict + 1
                    else:
                        logger.error(f"{name} : td class=nfo not found")
                    soup_smartphone.decompose()
            else:
                soup_page.decompose()
                logger.error(f"{url_brand_page} : td class=section-body not found")
                break

    # logger.debug(smartphones_dict)
    df = pd.DataFrame.from_dict(smartphones_dict, orient='index')
    df.to_csv("smartphones.csv", sep=";")

    print("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description='Scraper gsmarena.')
    parser.add_argument('--debug', help="Display debugging information", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.INFO)
    args = parser.parse_args()

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == '__main__':
    main()
