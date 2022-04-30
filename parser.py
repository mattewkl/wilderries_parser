
import re
from datetime import datetime
import selenium.common.exceptions
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
import gspread
from bs4 import BeautifulSoup as BS
from time import sleep

# globals
cur_day = datetime.now().day
date_dict = {1: 'R', 2: 'X', 3: 'AD', 4: 'AJ', 5: 'AP', 6: 'AV', 7: 'BB',
             8: 'BH', 9: 'BN', 10: 'BT', 11: 'BZ', 12: 'CF', 13: 'CL', 14: 'CR',
             15: 'CX', 16: 'DD', 17: 'DJ', 18: 'DP', 19: 'DV', 20: 'EB', 21: 'EH',
             22: 'EN', 23: 'ET', 24: 'EZ', 25: 'FF', 26: 'FL', 27: 'FR', 28: 'FX',
             29: 'GD', 30: 'GJ', 31: 'GP'}

sa = gspread.service_account('service_account.json')
sh = sa.open('testing')
wks = sh.worksheet('sheet')



# options, binary_location = r'path\to\firefox.exe'
firefox_options = Options()
firefox_options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
firefox_options.headless = False


# functions
def get_row_content_from_google_sheet(worksheet, row_letter: str, range_start: int, range_end: int, is_search_row:bool=False) -> list:
    total = wks.row_count
    if len(row_letter) < 3 and row_letter.isalpha():
        row_letter = row_letter.capitalize()
    else:
        raise ValueError('This is not a valid letter')
    if range_start < 3:
        range_start = 3
    if range_end > total:
        range_end = total
    range_string = f'{row_letter}{range_start}:{row_letter}{range_end}'
    row_list = worksheet.get(range_string)
    if is_search_row:
        row_content = []
        for value in row_list:
            try:
                text = value[0].split()
                text = ' '.join(text)
                row_content.append(re.sub(r'[\s]', '+', text))
            except IndexError:
                row_content.append('none')
        else:
            return  row_content
    row_content = [item for sublist in row_list for item in sublist]
    return row_content

def get_html_for_card_parse(url):
    driver = webdriver.Firefox(options=firefox_options)
    driver.get(url)
    driver.execute_script('window.scrollTo(0,1000)')
    sleep(5)
    return driver.page_source, driver.quit()


def scroll_page(driver, speed=35):
    current_scroll_position, new_height = 0, 1
    while current_scroll_position <= new_height:
        current_scroll_position += speed
        driver.execute_script("window.scrollTo(0, {});".format(current_scroll_position))
        new_height = driver.execute_script("return document.body.scrollHeight")

def parse_wb_search_position(range_start:int, range_end:int):
    position_list = []
    search_list = get_row_content_from_google_sheet(wks, 'F', range_start, range_end, is_search_row=True)
    art_list = get_row_content_from_google_sheet(wks, 'H', range_start, range_end, is_search_row=False)

    for table_position in range(len(search_list)):
        print(position_list)
        position = 0
        if search_list[table_position] == 'none':
            position_list.append(['Нет условий для поиска'])
            break
        url = f'https://www.wildberries.ru/catalog/0/search.aspx?sort=popular&search={search_list[table_position]}'
        while True:
            try:
                driver = webdriver.Firefox(options=firefox_options)
                driver.get(url)
                sleep(5)
                break
            except selenium.common.exceptions.WebDriverException:
                pass
        for page in range(1, 10):
            urls_list = []
            try:
                scroll_page(driver)
                htmlpage = BS(driver.page_source, 'html.parser')
                for soup_object in htmlpage.select('.product-card-list > div > div > a'):
                    urls_list.append(soup_object['href'])
                if len(urls_list) > 100:
                    position -= 2
                url = 'https://www.wildberries.ru/catalog/' + str(
                    art_list[table_position] + '/detail.aspx?targetUrl=XS')
                position += urls_list.index(url)
                position += (page - 1) * 100
                position_cell = []
                position_cell.append(position)
                position_list.append(position_cell)
                driver.close()
                break
            except ValueError:
                print('good not found')
                while True:
                    try:
                        elem = driver.find_element(by='css selector', value='.pagination-next')
                        break
                    except selenium.common.exceptions.NoSuchElementException:
                        while True:
                            try:
                                driver.refresh()
                                scroll_page(driver)
                                break
                            except selenium.common.exceptions.WebDriverException:
                                pass
                            pass
                elem.click()
                pass
        else:
            position_list.append(['1000+'])
    else:
        placeholder = f'{date_dict.get(cur_day)}{range_start}:{date_dict.get(cur_day)}{range_end}'
        wks.update(placeholder, position_list)


def parse_wb_reviews_and_score(range_start: int, range_end: int):
    art_list = get_row_content_from_google_sheet(wks,'H',range_start, range_end)
    review_count_list = []
    score_list = []
    for art in art_list:

        htmlpage = BS(get_html_for_card_parse(f'https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP')[0],
                      'html.parser')
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
                            get_html_for_card_parse(
                                f'https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP')[0],
                            'html.parser')
                        break
                    except selenium.common.exceptions.WebDriverException:
                        pass
        score_cell = []
        score_cell.append(score)
        score_list.append(score_cell)
    else:
        wks.update(f'M{range_start}:M{range_end}', review_count_list)
        wks.update(f'L{range_start}:L{range_end}', score_list)





