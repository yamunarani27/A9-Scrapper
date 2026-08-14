import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin

headers={"User-Agent" : "FlyRankInternship-A9/1.0 (+https://github.com/yamunarani27/A9-Scrapper)"}
url="https://books.toscrape.com/"
all_books=[]
discovered = 0        # total links found, including duplicates
pages_visited = 0

for i in range(1,4):
    CACHE_PATH=f"cache/catalogue-page-{i}.html"
    
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH,"r",encoding="utf-8") as f:
            html=f.read()
        print(f"Cache HIT-size: {len(html)} bytes")
    else:
        x=requests.get(url, headers=headers,timeout=5)

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
    pages_visited +=1

    books=soup.find_all("article",class_="product_pod")
    for book in books:
        if book is not None:
            relative_url=book.h3.a["href"]
            absolute_url=urljoin(url,relative_url)
            discovered+=1
            if absolute_url not in all_books:
                all_books.append(absolute_url)
            
            
    next_link=soup.find("li",class_="next")
    if next_link is not None:
        next_url=next_link.a["href"]
        url=urljoin(url,next_url)

        
print(f"Unique urls= {len(all_books)},Catalogue pages={pages_visited},discovered={discovered}")
    