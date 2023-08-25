# Imports
import math
import re
import scrapy
from currency_converter import CurrencyConverter
from scrapy import Selector
from scrapy.spiders import CrawlSpider
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
from itertools import chain
from ..items import AsosScrapperItem

# Constants
FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear"]

LENGTH_KEYWORDS = ["length", "mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]

NEGLECT_CATEGORIES_LIST = ['New in', 'Joggers', 'Multipacks', 'new-in',
                           'Socks', 'Exclusives at ASOS', 'Tracksuits & Joggers',
                           "Sportswear", "co-ords", "exclusives", "shoes", "accessories",
                           "heels", "snickers", "earrings"]

DISALLOWED_KEYWORDS = ["jogger", "joggers", "sandals", "sandal", "shoe",
                       "shoes", "heels", "accessories", "earrings", "PROMOTION", "DESIGNER", "BRANDS", "snickers",
                       "earrings", "new-in"]

CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit',
                     'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}

CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}


WEBSITE_NAME = "asos"


class AsosSpider(CrawlSpider):
    name = 'asos'
    allowed_domains = ['asos.com']

    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--head')
        options.add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.currency_converter = CurrencyConverter()
        super().__init__(*a, **kw)

    def start_requests(self):
        url = "https://www.asos.com/"
        yield scrapy.Request(url=url, cookies={"browseCountry": "US"}, callback=self.parse_categories)

    # This function parse_categories and for each category we will yield request for each category
    def parse_categories(self, response):
        women_categories = response.xpath("(//ul[@class='_1PXCics'])[4] /li /a /@href").getall()
        # men_categories = response.xpath("(//ul[@class='_1PXCics'])[19] /li /a /@href").getall()
        links = women_categories
        for iterator in range(len(links)):
            if not self.in_neglected_categories(links[iterator]):
                yield scrapy.Request(url=links[iterator], callback=self.parse_pages)

    # This function parse_pages for each category
    def parse_pages(self, response):
        total_products = int(response.xpath('//p[@data-auto-id="productsProgressBar"] /text()').get().split(" ")[4].
                             replace(",", ""))
        pageno = 1
        for _ in range(0, total_products, 72):
            current_page = f"{response.request.url}&page={pageno}"
            pageno += 1
            yield scrapy.Request(url=current_page, callback=self.get_all_products)

    # This function, parse href of all products on current page
    def get_all_products(self, response):
        products = response.xpath('//div[@data-auto-id="productList"] /section /article /a /@href').getall()
        for product_url in products:
            if not self.in_neglected_categories(product_url):
                yield scrapy.Request(url=product_url, callback=self.parse_item)

    # this function parses product scrap
    def parse_item(self, response):
        url = response.request.url
        custom_response = self.get_custom_selector(response)
        meta = {}
        # Scrapping Data
        external_id = custom_response.css('div.product-code p::text').get()
        if not external_id:
            external_id = re.findall("\d+", response.request.url)
            if external_id:
                external_id = external_id[-1]
            else:
                external_id = ""

        name = response.css("div.product-hero>h1::text").get()
        if not name:
            name = response.css("div#asos-product h1::text").get()

        price = custom_response.css('span.product-prev-price::text').getall()
        sale_price = ""
        if price:
            price = ' '.join(price)
            price = ''.join(re.findall('(\d+)(.\d+)?', price)[0])
            price = self.convert_price(price)
            # Now we will find sale price
            sale_price = custom_response.css("span.current-price::text").get()
            if sale_price:
                sale_price = sale_price.split(" ")[-1].strip()
                sale_price = self.convert_price(sale_price)
                meta = {"sale_price": sale_price}
        else:
            price = custom_response.css("span.current-price::text").get()
            if price:
                price = price.strip()
                price = self.convert_price(price)

        sizes = custom_response.xpath("//select[@id='main-size-select-0'] /option /text()").getall()
        if not sizes:
            sizes = custom_response.xpath("//select[contains(@id, 'mixmatch-size-select-1')] /option /text()").getall()

        sizes = [size for size in sizes if
                 not re.search("\w*Out of stock", size) and not re.search("Please select", size)]
        sizes = [size.split("-")[0].strip() for size in sizes]
        details = response.css("div.product-description *::text").getall()
        popup_details = ""
        if not details:
            details_elem = self.driver.find_element(By.CSS_SELECTOR, "div.product-title")
            actionchains = ActionChains(self.driver)
            actionchains.move_to_element(details_elem).click().perform()
            time.sleep(2)
            details = self.driver.find_elements(By.XPATH,
                                                '//h4[contains(text(), "Product Details")] /parent::* //ul /li')
            details = [det.text for det in details]
            popup_details = self.driver.find_elements(By.XPATH, '//h4[contains(text(), "Product Details")] /parent::*')
            popup_details = [pd.text for pd in popup_details]
            fabric = self.find_fabric_from_details(popup_details)
        else:

            fabric_details = response.css(".about-me *::text").getall()
            fabric = self.find_fabric_from_details(fabric_details)

        details = self.clean_details(details)
        images = custom_response.xpath("//img[@class='gallery-image'] /@srcset").getall()
        if images:
            images = [image.split(",")[-1] for image in images]
            images = [image for image in images if re.search("1926w", image, re.IGNORECASE)]

        categories = []
        scrapped_categories = response.xpath("//nav[@aria-label='breadcrumbs'] /ol /li /a /text()").getall()[1:]
        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)

        colors = custom_response.css("span.product-colour::text").getall()
        if colors:
            colors = [color.strip() for color in colors]
            colors = list(set(colors))
        else:
            colors = []
        extra_details = response.css("div.brand-description *::text").getall()
        extra_details += response.css("div.size-and-fit *::text").getall()
        extra_details += details
        extra_details += popup_details
        fit = ' '.join(self.find_keywords_from_str(extra_details, FIT_KEYWORDS)).strip()
        neck_line = ' '.join(self.find_keywords_from_str(extra_details, NECK_LINE_KEYWORDS)).strip()
        length = ' '.join(self.find_keywords_from_str(extra_details, LENGTH_KEYWORDS)).strip()
        breadcrumbs = response.xpath("//nav[@aria-label='breadcrumbs'] /ol /li /a /text()").getall()
        # if re.search("women", ' '.join(breadcrumbs), re.IGNORECASE):
        #     gender = "women"
        # else:
        #     gender = "men"
        gender = "women"
        number_of_reviews = ""
        review_description = []
        top_best_seller = ""
        occasions = self.find_keywords_from_str(extra_details, OCCASIONS_KEYWORDS)
        style = self.find_keywords_from_str(extra_details, STYLE_KEYWORDS)

        # aesthetics = self.find_from_target_string_multiple(details, name, categories, AESTHETIC_KEYWORDS)

        item = AsosScrapperItem()
        item["url"] = response.request.url
        item["external_id"] = external_id
        item["categories"] = categories
        item["name"] = name
        item["price"] = price
        item["colors"] = colors
        item["sizes"] = sizes
        item["details"] = details
        item["fabric"] = fabric
        item["images"] = images
        item["fit"] = fit
        item["neck_line"] = neck_line
        item["length"] = length
        item["gender"] = gender
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = review_description
        item["top_best_seller"] = top_best_seller
        item["meta"] = meta
        item["occasions"] = occasions
        item["style"] = style
        item["website_name"] = WEBSITE_NAME
        # item["aesthetics"] = aesthetics
        if categories:
            if not self.in_disallowed_keywords(url, name, categories):
                yield item

    # Helpers

    def get_selector(self, url):
        self.driver.get(url)
        custom_selector = Selector(text=self.driver.page_source)
        return custom_selector

    def extract_last_page(self, response):
        pages_info = response.css('.XmcWz6U::text').get()
        if pages_info:
            get_numbers = re.findall(r'[\d,]+[,\d]', pages_info)
            rs = [int(s.replace(",", "")) for s in get_numbers]
            last_page = rs[1] / rs[0]
            return math.ceil(last_page)
        else:
            return 1

    def extract_info(self, details, keywords):
        for detail in details:
            if any(keyword in detail for keyword in keywords):
                return detail.strip()

    # This helper method clean details we have scrapped
    def clean_details(self, details):
        details = [detail.strip() for detail in details]
        return [detail for detail in details if detail != "" and
                not re.search("Model", detail, re.IGNORECASE) and
                not re.search("Show More", detail, re.IGNORECASE) and
                not re.search("Show less", detail, re.IGNORECASE) and
                not re.search("Product Details", detail, re.IGNORECASE) and
                not re.search("\.", detail, re.IGNORECASE) and
                not re.search("By", detail, re.IGNORECASE)]

    # This helper finds fabric from details and returns it
    def find_fabric_from_details(self, details):
        product_details = ' '.join(details)
        fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b|Polyurethane\b|Rubber\b|Lyocell\b)\)?""",
                                     product_details,
                                     flags=re.IGNORECASE | re.MULTILINE)
        fabric_tuples_joined = [''.join(tups) for tups in fabrics_founded]
        # Removing duplicates now if any
        fabrics_final = []
        for fabric in fabric_tuples_joined:
            if fabric not in fabrics_final:
                fabrics_final.append(fabric)

        return ' '.join(fabrics_final).strip()

    # This function scrolls product detail page to the bottom
    def scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    """
    this function returns upper limit of page, for example if we have total of 90 products with 20 products on each
    and page query is like 0 to 20, then 20 to 40 and so on, a time will come when we have 80 to 100 as a page query
    but products are only 90, so this function makes sure we have correct upper limit for pages query, in our case 80-90
    """

    def get_pages_upperlimit(self, current_page, total_pages):
        if (current_page + 72) > total_pages:
            return current_page + (total_pages - current_page)
        else:
            return current_page + 72

    def clean_category_name(self, name):
        if re.search("&", name):
            return name.split("&")
        else:
            return name

    # This function returns custom selector based on selenium request
    def get_custom_selector(self, response):
        self.driver.get(response.request.url)
        return Selector(text=self.driver.page_source)

    # This function checks for neglected categories
    def in_neglected_categories(self, category):
        for neglected_cat in NEGLECT_CATEGORIES_LIST:
            if re.search(neglected_cat, category, re.IGNORECASE):
                return True

        return False

    def in_disallowed_keywords(self, url, name, cats):
        print("Cats are: ", cats, ' name is: ', name, " url is: ", url)
        for keyword in DISALLOWED_KEYWORDS:
            if re.search(keyword, url, re.IGNORECASE) or re.search(keyword, name, re.IGNORECASE) or \
                    re.search(keyword, ' '.join(cats), re.IGNORECASE):
                return True
        return False

    def remove_duplicates_using_regex(self, keywords_list):
        finals = []
        for keyword in keywords_list:
            if not re.search(keyword, ' '.join(finals), re.IGNORECASE):
                finals.append(keyword)

        return finals

    def find_keywords_from_str(self, details, keywords):
        finals = []
        details = ' '.join(details)
        for keyword in keywords:
            if re.search(keyword, details, re.IGNORECASE):
                if keyword not in finals:
                    finals.append(keyword)

        return finals

    def convert_price(self, price):
        return "$" + str(
            round(self.currency_converter.convert(int(price.replace("£", "").split(".")[0]), 'GBP', 'USD')))

    def clean_categories(self, categories):
        categories = [cat for cat in categories if not re.search("women", cat, re.IGNORECASE) and
                      not re.search("men", cat, re.IGNORECASE)]
        categories = [cat.split(" ") for cat in categories]
        categories = list(chain.from_iterable(categories))
        categories = [cat for cat in categories if cat != "" and not re.search("Men", cat, re.IGNORECASE) and
                      not re.search("Women", cat, re.IGNORECASE)]
        categories = [cat for cat in categories if cat != ""]
        return self.remove_duplicates_using_regex(categories)


# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)
    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)
    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats
