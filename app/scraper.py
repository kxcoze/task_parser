import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import Select


from config import REGIONS


def is_element_visible_in_viewpoint(driver, element) -> bool:
    # Custom check for vision of element
    return driver.execute_script(
        "var elem = arguments[0],                 "
        "  box = elem.getBoundingClientRect(),    "
        "  cx = box.left + box.width / 2,         "
        "  cy = box.top + box.height / 2,         "
        "  e = document.elementFromPoint(cx, cy); "
        "for (; e; e = e.parentElement) {         "
        "  if (e === elem)                        "
        "    return true;                         "
        "}                                        "
        "return false;                            ",
        element,
    )


def fetch_data_from_subcategory(driver, url, city):
    # Load remote resource
    print("Trying to access:", url)
    driver.get(url)
    # Waiting for loading
    time.sleep(5)
    print(f"Page {driver.title} has been loaded")
    # possible_amount_products = driver.find_element(By.CSS_SELECTOR, '.css-1vpxcja')[1:-1]
    # print('We can possibly get this amount of products from this page:', possible_amount_products)
    # Region changing if passed `city` argument doesn't match user region on the site
    # WARNING: this check implementation doesn't work for mobile resolution
    button_region_change = driver.find_element(By.ID, "currentRegionName")
    if REGIONS[city] != button_region_change.text:
        print(
            f"Quered region <{REGIONS[city]}> doesn't match with current {button_region_change.text}"
        )
        print("Changing...")
        button_region_change.click()
        # Wait for loading
        time.sleep(2)
        # Select needed element
        select_region = Select(driver.find_element(By.ID, "regions"))
        select_region.select_by_visible_text(REGIONS[city])
        time.sleep(1)
        # Confirm change
        driver.find_element(By.ID, "selectShop").click()
        time.sleep(5)
        button_region_change = driver.find_element(By.ID, "currentRegionName")
        print(f"Current region is {button_region_change.text}")
    # Get brand names section
    print("Now let's get all brand names...")
    filter_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "css-v7s87w"))
    )
    # Scroll to filter button
    while not is_element_visible_in_viewpoint(driver, filter_button):
        filter_button.location_once_scrolled_into_view
    print(f"Clicked on {filter_button.text} button")
    filter_button.click()
    time.sleep(3)
    # Get all filters
    list_of_filters = driver.find_elements(By.CSS_SELECTOR, "div.css-y19ghj")
    brand_button = None
    print("Searching 'Бренд' section on filter...")
    for ftr in list_of_filters:
        if ftr.text == "Бренд":
            print("Found 'Бренд' button!")
            brand_button = ftr

    time.sleep(2)
    # If "Бренд" button was found then click on it
    brand_names = []
    if brand_button:
        while not is_element_visible_in_viewpoint(driver, brand_button):
            brand_button.location_once_scrolled_into_view
        print("Clicked on {brand_button.text} button")
        brand_button.click()
        time.sleep(2)
        # Get all brand names from window
        brands = driver.find_element(By.CLASS_NAME, "checkbox-group__items").children()
        brand_names = [brand.text for brand in brands]
        time.sleep(2)
    # After collection of brands exit from filter menu
    exit_filter = driver.find_element(By.CLASS_NAME, "css-1iubadi")
    while not is_element_visible_in_viewpoint(driver, exit_filter):
        exit_filter.location_once_scrolled_into_view
    exit_filter.click()
    print("Exiting filter section...")

    # Render products while the button 'Показать ещё' is accessible
    print("Let's load all possible pages...")
    cnt = 1
    try:
        while True:
            time.sleep(3)
            element = WebDriverWait(driver, 15).until(
                EC.presence_of_element_located((By.ID, "showMoreButton"))
            )
            print(f"Located {element.text} ")
            while not is_element_visible_in_viewpoint(driver, element):
                element.location_once_scrolled_into_view
            print(f"Loading next {(cnt:=cnt+1)} page...")
            element.click()
    except TimeoutException:
        # So there are no buttons to press...
        print("All possible 'Показать ещё' have been pressed!")
        print("Waiting for rendering all products...")
        time.sleep(5)
        elements = driver.find_elements(By.CLASS_NAME, "css-n9ebcy-Item")
        print(f"Found {len(elements)} products!")
        print("Get html code for further parsing")
        html = driver.page_source

    return html, brand_names
