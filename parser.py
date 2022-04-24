import gspread
from bs4 import BeautifulSoup as BS
from requests import request
from time import sleep
sa = gspread.service_account('service_account.json')
sh = sa.open('testing')

wks = sh.worksheet('sheet')
total = wks.row_count
articles = wks.get('H3:H'+str(total))
art_list = []
for art in articles:
   art_list.append(art[0])



review_count_list = []
for art in art_list:
   sleep(3)
   r = request('GET', f"https://www.wildberries.ru/catalog/{art}/detail.aspx?targetUrl=SP")
   htmlpage = BS(r.content, 'html.parser')
   for el in htmlpage.select(".same-part-kt__count-review "):
      review_count_list.append(list(el.text))
      break

print(review_count_list)