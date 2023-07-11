import time
import logging
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path

logger = logging.getLogger("gsmarena-scraper")
temps_debut = time.time()


def get_soup(url):
    ntries = 0
    while True:
        try:
            ntries += 1
            soup = BeautifulSoup(requests.get(url).content, features="lxml")
            time.sleep(3)
            if soup.find("title").text.lower() == "too many requests":
                logger.info("Too many requests. Waiting for 60 seconds.")
                time.sleep(60)
            elif soup or ntries > 30:
                break
            logger.debug(f"Try {ntries} : Problem with soup for {url}.")
        except Exception:
            logger.debug(f"Can't extract webpage {url}.")
    return soup


def extract_smartphone_infos(smartphone):
    smartphone_dict = {}
    smartphone = smartphone.find("a")
    url_smartphone = f"https://m.gsmarena.com/{smartphone['href']}"
    logger.debug("url_smartphone: %s", url_smartphone)
    smartphone_dict["link"] = url_smartphone
    smartphone_dict["image"] = str(smartphone.find("img")["src"])
    soup_smartphone = get_soup(url_smartphone)
    smartphone_dict["name"] = str(
        soup_smartphone.find("h1").find_all(string=True, recursive=False)[0]
    )
    logger.info(f"Processing model {smartphone_dict['name']}")

    for main_field in soup_smartphone.select("span[data-spec],td[data-spec]"):
        smartphone_dict[main_field["data-spec"]] = main_field.text.strip()

    soup_smartphone.decompose()
    return smartphone_dict


def extract_brand_name(brand):
    return brand["href"].split("-phones")[0]


def extract_brand_infos(brand):
    index_page = 1
    url_page = f"https://m.gsmarena.com/{brand['href']}"
    logger.info(f"Processing brand {brand.text}")
    smartphone_list = []

    while True:
        logger.info(f"Processing brand {brand.text} - Page {index_page}")
        logger.debug(f"Page URL: {url_page}")
        soup_page = get_soup(url_page)
        next_page = soup_page.select("a.left")[-1]
        next_page_available = "disabled" not in next_page["class"]
        url_page = f"https://m.gsmarena.com/{next_page['href']}"
        index_page = index_page + 1

        smartphones = soup_page.select("div.general-menu li")
        soup_page.decompose()
        for smartphone in smartphones:
            smartphone_dict = extract_smartphone_infos(smartphone)
            smartphone_list.append(smartphone_dict)

        if not next_page_available:
            return smartphone_list


def main():
    parse_args()

    url_index = "https://m.gsmarena.com/makers.php3"
    soup_index = get_soup(url_index)

    brands = soup_index.select("div#list-brands a")
    soup_index.decompose()
    Path("Exports").mkdir(parents=True, exist_ok=True)

    global_list_smartphones = pd.DataFrame()
    for brand in brands:
        brand_name = extract_brand_name(brand)
        brand_export_file = f"Exports/{brand_name}_export.csv"
        # If file doesn't already exists, extract smartphone informations.
        if not Path(brand_export_file).is_file():
            brand_dict = pd.DataFrame.from_records(extract_brand_infos(brand))
            brand_dict.to_csv(brand_export_file, sep=";", index=False)
            global_list_smartphones = pd.concat(
                [global_list_smartphones, brand_dict], sort=False
            )
        # Otherwise, read the file.
        else:
            logger.warning(
                "Skipping %s, %s already exists. Its content will be added to the global export file.",
                brand_name,
                brand_export_file,
            )
            brand_dict = pd.read_csv(brand_export_file, sep=";")
            global_list_smartphones = pd.concat(
                [global_list_smartphones, brand_dict], sort=False
            )
    all_export_file = "Exports/all_brands_export.csv"
    logger.info("Exporting all smartphone to %s.", all_export_file)
    global_list_smartphones.to_csv(all_export_file, sep=";", index=False)

    logger.info("Runtime : %.2f seconds" % (time.time() - temps_debut))


def parse_args():
    parser = argparse.ArgumentParser(description="Scraper gsmarena.")
    parser.add_argument(
        "--debug",
        help="Display debugging information",
        action="store_const",
        dest="loglevel",
        const=logging.DEBUG,
        default=logging.INFO,
    )
    args = parser.parse_args()

    logger.setLevel(args.loglevel)
    handler = logging.StreamHandler()
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    return args


if __name__ == "__main__":
    main()
