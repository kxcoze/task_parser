from bs4 import BeautifulSoup as BS4

from config import REGIONS


def format_price(price):
    return price.replace(",", ".").replace(" ", "")


def parse_data_from_subcategory(html, brands, city):
    URL = "https://auchan.ru"
    print("Parsing received data...")
    soup = BS4(html, "lxml")
    product_category = soup.find("li", class_="css-yo0k09").text
    product_subcategory = soup.find("h1", id="catalogSubCategoryName").text
    # Find parent div for all products
    upper_div = soup.find("main", class_="css-i3pbo").find(
        "div", class_="css-j6iz2w css-3nngaf-Layout"
    )
    products = list(upper_div)
    result = {"category": product_category, "count": 0, "subcategories": []}
    subcategory = {
        "subcategory": product_subcategory,
        "count": 0,
        "region": REGIONS[city],
        "products": [],
    }
    for product in products:
        product_id = int(product.attrs["data-offer-id"])
        product_a = product.find("a", class_="linkToPDP active css-do8div")
        if product_a is None:
            # Not in stock, skip?
            # product_a = product.find('a', class_='linkToPDP hidden css-do8div')
            continue

        # product_name = product.find('p', class_='css-1bdovxp').text
        product_name = product_a.text
        product_link = product_a.attrs["href"]

        pre_product_promo = product.find("div", class_="active css-1hxq85i")
        pre_product_price = format_price(
            product.find("div", class_="active css-xtv3eo").text[:-2]
        )
        if pre_product_promo is not None:
            product_promo = pre_product_price
            product_price = format_price(pre_product_promo.text)
        else:
            product_promo = None
            product_price = pre_product_price

        product_brand = None
        for brand in brands:
            if brand != "-" and brand.lower() in product_name.lower():
                product_brand = brand
                break
        subcategory["products"].append(
            {
                "id": product_id,
                "name": product_name,
                "link": f"{URL}{product_link}",
                "price": product_price,
                "promo_price": product_promo,
                "brand": product_brand,
            }
        )

    subcategory["count"] = len(subcategory["products"])

    result["count"] += subcategory["count"]
    result["subcategories"].append(subcategory)
    print(f"Parsing is ended, we have gathered {result['count']} products")
    return result
