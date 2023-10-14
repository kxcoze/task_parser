import os
import json
from datetime import datetime

import click
import seleniumwire.undetected_chromedriver as uc
import chromedriver_autoinstaller

from scraper import fetch_data_from_subcategory
from parsers.parser import parse_data_from_subcategory
from config import REGIONS, HOST


def get_json_from_subcategory(driver, URL, city):
    html, brands = fetch_data_from_subcategory(driver, URL, city)
    data_dict = parse_data_from_subcategory(html, brands, city)

    # Create result folder for all categories
    results_folder = os.path.join(os.pardir, "results")
    os.makedirs(results_folder, exist_ok=True)

    # Create category subfolder for result
    category_folder = data_dict["category"]
    print("Now let's create .json file for the parsed info")
    print("Create subfolder if not exists ->", category_folder)
    category_folder = os.path.join(results_folder, data_dict["category"])
    os.makedirs(category_folder, exist_ok=True)

    # We go through all subcategories
    for subcategory in data_dict["subcategories"]:
        subcategory_name = subcategory["subcategory"].replace(",", "").replace(" ", "_")

        # Generate current date
        cur_date = datetime.now().strftime("%d_%m_%Y")

        # Format of file will be "Колбасные_изделия_moscow_14_10_2023.json"
        file_name = f"{subcategory_name}_{city}_{cur_date}.json"
        # Creating .json file in category folder
        file_path = os.path.join(category_folder, file_name)
        with open(file_path, "w", encoding="utf-8") as json_file:
            json.dump(subcategory, json_file, indent=2, ensure_ascii=False)
        print(f"Created {file_path} file!")

    data_dict = json.dumps(data_dict, indent=2, ensure_ascii=False)
    return data_dict


@click.command()
@click.option('--autoinstall', default=1, help='Autoinstall chromedriver for you? Yes is 1 (Default), No is 0.')
def main(autoinstall):
    if autoinstall:
        chromedriver_autoinstaller.install()  # Install latest version of chromedriver
    regions = REGIONS.keys()

    # Init options
    chrome_options = uc.ChromeOptions()
    chrome_options.add_argument("--ignore-ssl-errors=yes")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--deny-permission-prompts")
    # Init undetectable_chromedriver
    # WARNING: headless mode doesn't provide a robust bypass of ANTI-BOT protection
    # for example, on Auchan.ru enabled QRATOR defense, so headless mode doesn't work
    # but for online.metro-cc.ru headless mode works just fine
    print("Browser loading...")
    driver = uc.Chrome(
        options=chrome_options,
    )

    URL = f"{HOST}/catalog/kolbasnye-izdeliya/kolbasy-vetchina/"
    for region in regions:
        print(get_json_from_subcategory(driver, URL, region)[:100])

    # Uncomment these lines if you wanna scrape also these urls
    # URL2 = f"{HOST}/catalog/syry/tverdye-i-polutverdye/"
    # for region in regions[::-1]:
    #     print(get_json_from_subcategory(driver, URL2, region)[:100])

    # URL3 = f"{HOST}/catalog/ovoschi-frukty-zelen-griby-yagody/seychas-sezon/"
    # for region in regions:
    #     print(get_json_from_subcategory(driver, URL3, region)[:100])

    driver.quit()


if __name__ == "__main__":
    main()
