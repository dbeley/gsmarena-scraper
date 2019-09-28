import time
import logging
import argparse
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path


logger = logging.getLogger()
temps_debut = time.time()


def extract_smartphone_infos(smartphone):
    smartphone_dict = dict()
    smartphone = smartphone.find("a")
    url_smartphone = f"https://www.gsmarena.com/{str(smartphone['href'])}"
    logger.debug("url_smartphone : %s", url_smartphone)
    smartphone_dict["Link"] = url_smartphone
    smartphone_dict["Image"] = str(smartphone.find("img")["src"])
    soup_smartphone = BeautifulSoup(
        requests.get(url_smartphone).content, features="lxml"
    )
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
    soup_smartphone.decompose()
    return smartphone_dict


def extract_brand_infos(brand):
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
        html_doc_page = requests.get(url_brand_page).content
        soup_page = BeautifulSoup(html_doc_page, features="lxml")
        logger.debug(f"Page URL : {url_brand_page}")

        if soup_page.find("div", {"class": "section-body"}).select("li"):
            smartphones = soup_page.find(
                "div", {"class": "section-body"}
            ).find_all("li")
            soup_page.decompose()
            for smartphone in smartphones:
                smartphone_dict = extract_smartphone_infos(smartphone)
                smartphone_list.append(smartphone_dict)
        else:
            soup_page.decompose()
            logger.error(
                "%s : td class=section-body not found", url_brand_page
            )
            return brand_name, smartphone_list


def main():
    args = parse_args()

    url_index = "https://www.gsmarena.com/makers.php3"
    soup_index = BeautifulSoup(
        requests.get(url_index).content, features="lxml"
    )
    brands = soup_index.find("div", {"class": "st-text"}).find_all("a")
    # logger.debug(brands)
    soup_index.decompose()
    Path("Exports").mkdir(parents=True, exist_ok=True)

    global_list_smartphones = []
    for brand in brands:
        brand_name, brand_dict = extract_brand_infos(brand)
        pd.DataFrame.from_records(brand_dict).to_csv(
            f"Exports/{brand_name}_export.csv", sep=";", index=False
        )
        global_list_smartphones += brand_dict
    # logger.debug(smartphones_dict)
    pd.DataFrame.from_records(global_list_smartphones).to_csv(
        "Exports/all_brands_export.csv", sep=";", index=False
    )

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

    logging.basicConfig(level=args.loglevel)
    return args


if __name__ == "__main__":
    main()
