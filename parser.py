import re

import selenium.common.exceptions
from selenium import webdriver

from selenium.webdriver.firefox.options import Options
import gspread
from bs4 import BeautifulSoup as BS
from time import sleep


options = Options()
options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
options.headless = True

sa = gspread.service_account('service_account.json')
sh = sa.open('testing')

wks = sh.worksheet('sheet')
total = wks.row_count
articles = wks.get('H3:H'+str(total))
search_list = wks.get('F3:F'+str(total))
art_list = []
for art in articles:
   art_list.append(art[0])





def get_html_for_card_parse(url):
   current_scroll_position, new_height = 0, 1
   speed = 16
   driver = webdriver.Firefox(options=options)
   driver.get(url)


   driver.execute_script('window.scrollTo(0,1000)')

   # while current_scroll_position <= new_height:
   #    current_scroll_position += speed
   #    driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
   #    new_height = driver.execute_script("return document.body.scrollHeight")
   sleep(5)
   return driver.page_source, driver.quit()

def get_html_for_search_parse(url):
   current_scroll_position, new_height = 0, 1
   speed = 16
   driver = webdriver.Firefox(options=options)
   driver.get(url)

   driver.execute_script('window.scrollTo(0,1000)')

   while current_scroll_position <= new_height:
      current_scroll_position += speed
      driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
      new_height = driver.execute_script("return document.body.scrollHeight")
   return driver.page_source, driver.quit()







review_count_list = []
score_list = []
def parse_wb_reviews_and_score(art_list):


   for art in art_list:
      htmlpage = BS(get_html_for_card_parse(f'https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP')[0], 'html.parser')
      while True:
         try:
            review = htmlpage.select_one(".same-part-kt__count-review").text
            break
         except AttributeError:
            print('error')
            while True:
               try:
                  htmlpage = BS(get_html_for_card_parse(
                     f'https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP')[0], 'html.parser')
                  break
               except selenium.common.exceptions.WebDriverException:
                  pass

      review = re.sub(r'[^\w+]', ' ', review).strip()
      print(review)
      review_cell = []
      review_cell.append(review)
      review_count_list.append(review_cell)
      while True:
         try:
            score = htmlpage.select_one('.user-scores__score').text
            break
         except AttributeError:
            print('error')
            while True:
               try:
                  htmlpage = BS(
                     get_html_for_card_parse(f'https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP')[0],
                             'html.parser')
                  break
               except selenium.common.exceptions.WebDriverException:
                  pass

      score_cell = []
      score_cell.append(score)
      score_list.append(score_cell)
   else:
    wks.update('M3:M'+str(total),review_count_list)
    wks.update('L3:L'+str(total),score_list)


if __name__ == 'main':
   parse_wb_reviews_and_score(art_list)
