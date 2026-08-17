import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime

headers={"User-Agent" : "FlyRankInternship-A9/1.0 (+https://github.com/yamunarani27/A9-Scrapper)"}
current_url="https://books.toscrape.com/"
all_books=[]
discovered = 0        

for i in range(1,4):
    CACHE_PATH=f"cache/catalogue-page-{i}.html"
    
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH,"r",encoding="utf-8") as f:
            html=f.read()
        print(f"Cache HIT-size: {len(html)} bytes")
    else:
        x=requests.get(current_url, headers=headers,timeout=5)

        statuscode=x.status_code
        if statuscode != 200:
            print(f"failed to fetch page:{statuscode}")
            break
        else:
            html=x.text
            os.makedirs("cache",exist_ok=True)
            with open(CACHE_PATH,"w",encoding="utf-8") as f:
                f.write(html)
            print(f"FETCH - SIZE: {len(html)} bytes")

    soup = BeautifulSoup(html, 'html.parser')
    
    books=soup.find_all("article",class_="product_pod")
    for book in books:
        if book is not None:
            relative_url=book.h3.a["href"]
            absolute_url=urljoin(current_url,relative_url)
            bookname=absolute_url.split("/")[-2]
            BOOK_CACHE_PATH=f"cache/book-{bookname}.html"
            if os.path.exists(BOOK_CACHE_PATH):
                with open(BOOK_CACHE_PATH,"r",encoding="utf-8") as f:
                    book_html=f.read()
            else:
                book_resp=requests.get(absolute_url,headers=headers,timeout=5)
                if book_resp.status_code == 200:
                    book_html=book_resp.text
                    with open(BOOK_CACHE_PATH,"w",encoding="utf-8") as f:
                        f.write(book_html)
                else:
                    book_html = None

            description=None
            if book_html is not None:
                book_soup=BeautifulSoup(book_html,"html.parser")
                book_price=(book_soup.find("p",class_="price_color")).text
                availability=book_soup.find("p",class_="instock")
                book_availability=availability.text.strip()       
                desc_header = book_soup.find("div", id="product_description")
                if desc_header is not None:
                    desc_p = desc_header.find_next_sibling("p")
                    if desc_p is not None:
                       description = desc_p.text.strip()

            book_description=description
            book_title=book.h3.a["title"]
            book_price=(book.find("p",class_="price_color")).text
            ratingclass=book.find("p",class_="star-rating")
            rating=ratingclass.get("class")
            book_rating=rating[1]
            book_source=CACHE_PATH
            fetch_info=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            book_data={"product_url":absolute_url,"title":book_title,"price_text":book_price,"availability_text":book_availability,
                       "rating_text":book_rating,"description":book_description,"source_page":book_source,"fetched_at":fetch_info}
            discovered +=1
            all_books.append(book_data)
            
                 
    next_link=soup.find("li",class_="next")
    if next_link is not None:
        next_url=next_link.a["href"]
        current_url=urljoin(current_url,next_url)

print(f"detail_pages={discovered},Raw_record={all_books[1]}")
    