import time
import logging
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from stem import Signal
from stem.control import Controller

logger = logging.getLogger("gsmarena-scraper")
temps_debut = time.time()


class tor_network:
    def __init__(self):
        self.session = requests.session()
        self.session.proxies = {
            "http": "socks5h://localhost:9050",
            "https": "socks5h://localhost:9050",
        }
        self.ntries = 0

    def get_soup(self, url):
        while True:
            try:
                self.ntries += 1
                soup = BeautifulSoup(
                    self.session.get(url).content, features="lxml"
                )
                if soup.find("title").text.lower() == "too many requests":
                    logger.info(f"Too many requests.")
                    self.request_new_ip()
                elif soup or self.ntries > 30:
                    self.ntries = 0
                    break
                logger.debug(
                    f"Try {self.ntries} : Problem with soup for {url}."
                )
            except Exception as e:
                logger.debug(f"Can't extract webpage {url}.")
                self.request_new_ip()
        return soup

    def request_new_ip(self):
        logger.info("Requesting new ip address.")
        with Controller.from_port(port=9051) as controller:
            controller.authenticate(password="my password")
            controller.signal(Signal.NEWNYM)
        self.session = requests.session()
        self.session.proxies = {
            "http": "socks5h://localhost:9050",
            "https": "socks5h://localhost:9050",
        }
        self.ntries = 0


def extract_smartphone_infos(network, smartphone):
    smartphone_dict = dict()
    smartphone = smartphone.find("a")
    url_smartphone = f"https://www.gsmarena.com/{str(smartphone['href'])}"
    logger.debug("url_smartphone : %s", url_smartphone)
    smartphone_dict["Link"] = url_smartphone
    smartphone_dict["Image"] = str(smartphone.find("img")["src"])
    soup_smartphone = network.get_soup(url_smartphone)
    smartphone_dict["Name"] = str(
        soup_smartphone.find("h1").find_all(text=True, recursive=False)[0]
    )
    logger.info(f"Processing model {smartphone_dict['Name']}")

    if soup_smartphone.select("td", {"class": "nfo"}):
        smartphone_dict["Release date"] = soup_smartphone.find(
            "span", {"data-spec": "released-hl"}
        ).text.strip()
        smartphone_dict["Weight"] = soup_smartphone.find(
            "span", {"data-spec": "body-hl"}
        ).text.strip()
        smartphone_dict["OS"] = soup_smartphone.find(
            "span", {"data-spec": "os-hl"}
        ).text.strip()
        smartphone_dict["Storage"] = soup_smartphone.find(
            "span", {"data-spec": "storage-hl"}
        ).text.strip()
        smartphone_dict["Fans"] = str(
            soup_smartphone.find("li", {"class": "help-fans"})
            .find("strong")
            .find(text=True)
        ).strip()
        smartphone_dict["Popularity"] = str(
            soup_smartphone.find("li", {"class": "help-popularity"}).find_all(
                text=True
            )[2]
        ).strip()
        smartphone_dict["Hits"] = str(
            soup_smartphone.find("li", {"class": "help-popularity"}).find_all(
                text=True
            )[4]
        ).strip()
        ecran = soup_smartphone.find("li", {"class": "help-display"}).find_all(
            text=True
        )
        if ecran:
            try:
                logger.debug("Screen : %s", ecran)
                smartphone_dict["Screen_size"] = str(ecran[2]).strip()
                smartphone_dict["Screen_resolution"] = str(ecran[3]).strip()
            except Exception as e:
                logger.debug("Screen : %s", e)
        ram = soup_smartphone.find("li", {"class": "help-expansion"}).find_all(
            text=True
        )
        if ram:
            try:
                logger.debug("RAM : %s", ram)
                smartphone_dict["RAM"] = " ".join(
                    [ram[i].strip() for i in [2, 3]]
                )
                smartphone_dict["SOC"] = str(ram[-1]).strip()
            except Exception as e:
                logger.debug(f"RAM : %s", e)
        batterie = soup_smartphone.find(
            "li", {"class": "help-battery"}
        ).find_all(text=True)
        if batterie:
            try:
                logger.debug("Battery : %s", batterie)
                smartphone_dict["Battery"] = " ".join(
                    [batterie[i].strip() for i in [2, 3, 4]]
                )
            except Exception as e:
                logger.debug("Battery : %s", e)
        for spec in soup_smartphone.find_all("td", {"class": "nfo"}):
            try:
                type = str(spec["data-spec"].strip())
                value = "".join(
                    [
                        x.strip()
                        for x in spec.find_all(text=True, recursive=False)
                    ]
                )
                smartphone_dict[type] = value.replace("\n", " ").replace(
                    "\r", " "
                )
                logger.debug("%s : %s", type, value)
            except Exception:
                pass
    else:
        logger.error("%s : td class=nfo not found", smartphone_dict["Name"])
        network.request_new_ip()
    soup_smartphone.decompose()
    return smartphone_dict


def extract_brand_name(brand):
    return brand["href"].rsplit("-", 1)[0]


def extract_brand_infos(network, brand):
    index_page = 1
    brand = brand["href"].rsplit("-", 1)
    brand_name = str(brand[0])
    brand_id = str(brand[1].split(".")[0])
    logger.info(f"Processing brand {brand_name}")
    url_brand_base = f"https://www.gsmarena.com/{brand_name}-f-{brand_id}-0"
    smartphone_list = []

    while True:
        url_brand_page = f"{url_brand_base}-p{index_page}.php"
        logger.debug(url_brand_page)
        index_page = index_page + 1
        soup_page = network.get_soup(url_brand_page)
        logger.debug(f"Page URL : {url_brand_page}")

        if soup_page.find("div", {"class": "section-body"}).select("li"):
            smartphones = soup_page.find(
                "div", {"class": "section-body"}
            ).find_all("li")
            soup_page.decompose()
            for smartphone in smartphones:
                smartphone_dict = extract_smartphone_infos(network, smartphone)
                smartphone_list.append(smartphone_dict)
        else:
            soup_page.decompose()
            logger.error(
                "%s : td class=section-body not found", url_brand_page
            )
            return smartphone_list


def main():
    args = parse_args()

    network = tor_network()

    url_index = "https://www.gsmarena.com/makers.php3"
    soup_index = network.get_soup(url_index)

    brands = soup_index.find("div", {"class": "st-text"}).find_all("a")
    soup_index.decompose()
    Path("Exports").mkdir(parents=True, exist_ok=True)

    global_list_smartphones = pd.DataFrame()
    for brand in brands:
        brand_name = extract_brand_name(brand)
        brand_export_file = f"Exports/{brand_name}_export.csv"
        # If file doesn't already exists, extract smartphone informations.
        if not Path(brand_export_file).is_file():
            brand_dict = pd.DataFrame.from_records(
                extract_brand_infos(network, brand)
            )
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
