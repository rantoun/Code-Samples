## File with lists of review sites and call to Flipkart scraper ##
## If run for all printer, laptop, tablet sites listed here - this will crawl through and scrape upwards of 200 web pages ##

import pandas as pd
from Flipkart import flipkart_revs


# List of review sites to start from for these HP Laptops
laptop_reviews = [
"http://www.flipkart.com/hp-15-g049au-notebook-apu-quad-core-a8-4gb-500gb-win8-1-k5b45pa/product-reviews/ITMEY7HHAURTCZHA?pid=COMEY34HEHBBH9TV&type=all",
"http://www.flipkart.com/hp-compaq-15-s009tu-notebook-4th-gen-ci3-4gb-500gb-win-8-1-j8c08pa/product-reviews/ITMDYFS3GGTRR8HX?pid=COMDYFRXDSJ7FJ5G&type=all",
"http://www.flipkart.com/hp-compaq-15-s104tu-notebook-4th-gen-ci3-4gb-1tb-win8-1-k8t60pa/product-reviews/ITMEFWZFFT4MXUFA?pid=COMEFWNTFRVGX5NZ&type=all",
"http://www.flipkart.com/hp-1000-1b10au-notebook-apu-dual-core-a4-2gb-500gb-free-dos-k5b65pa/product-reviews/ITMEY7HKHZHBGAQF?pid=COMEY34H4BH7JF9A&type=all"
]

# List of review sites to start from for these HP Printers
printer_reviews = [
"http://www.flipkart.com/hp-deskjet-ink-advantage-4515-all-in-one-wireless-printer/product-reviews/ITMDZQG7CZYHFDCT?pid=PRNDZQCARXB4NPWQ&type=all",
"http://www.flipkart.com/hp-deskjet-ink-advantage-3545-all-in-one-wireless-printer/product-reviews/ITME27E4T9ZQECEB?pid=PRNDZQCAWNUG2ZRS&type=all",
"http://www.flipkart.com/hp-deskjet-1510-multifunction-inkjet-printer-low-cartridge-cost/product-reviews/ITMDZSMBXMDB2DAZ?pid=PRNDZSMB8FDBWN6J&type=all",
"http://www.flipkart.com/hp-deskjet-ink-advantage-1515-all-in-one-printer/product-reviews/ITMDZKW2W3FNZWPQ?pid=PRNDZKS3YFQFWZBY&type=all",
"http://www.flipkart.com/hp-laserjet-1136-multi-function-laser-printer/product-reviews/ITMD4Z5XSYYRKG7S?pid=PRND4Z5Q3JR46KNZ&type=all",
"http://www.flipkart.com/hp-laserjet-1020-plus-single-function-laser-printer/product-reviews/ITMDFNYZRGYHT9NF?pid=PRNDFNYNGYCMNN8Y&type=all",
"http://www.flipkart.com/hp-deskjet-ink-advantage-2545-all-in-one-wireless-printer/product-reviews/ITMDZQG7TZZNVSBY?pid=PRNDZQCAFGWUCHHB&type=all"
]

# List of review sites to start from for these HP Tablets
tablet_reviews = [
"http://www.flipkart.com/hp-7-voice-tab/product-reviews/ITMEYFHFDXXJYYXK?pid=TABEYFGTKPZHUVHP&type=all",
"http://www.flipkart.com/hp-10-tablet/product-reviews/ITMDSYE5U97VT4ZY?pid=TABDSAZZ2DBJQQDX&type=all",
"http://www.flipkart.com/hp-slate-7-voice-tab/product-reviews/ITMDU4SGZWTCV3HR?pid=TABDU4SGZWTCV3HR&type=all",
"http://www.flipkart.com/hp-slate-7-tablet/product-reviews/ITMDSW9YTXRHY8GE?pid=TABDSW86BBEKNRVH&type=all"
]


# Scrape reviews for each of the products in the lists
# Create pandas dataframes from dictionaries to quickly write to CSV
printers = flipkart_revs(printer_reviews)
flip_printer_df = pd.DataFrame.from_dict(printers)
flip_printer_df.to_csv("FlipKart_HP_Printers.csv")

laptops = flipkart_revs(laptop_reviews)
flip_laptop_df = pd.DataFrame.from_dict(laptops)
flip_laptop_df.to_csv("FlipKart_HP_Notebooks.csv")

tablets = flipkart_revs(tablet_reviews)
flip_tablet_df = pd.DataFrame.from_dict(tablets)
flip_tablet_df.to_csv("FlipKart_HP_Tablets.csv")