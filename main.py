import requests
import os
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import datetime
from pydantic import BaseModel, HttpUrl, ValidationError
from typing import Optional
import json
import time

headers={"User-Agent" : "FlyRankInternship-A9/1.0 (+https://github.com/yamunarani27/A9-Scrapper)"}
current_url="https://books.toscrape.com/"
all_books=[]
seen_urls=set()
discovered = 0  
failed_pages=0
max_retry=1
pages_fetched=0
cache_hits=0


start_time=datetime.datetime.now(datetime.timezone.utc)




#Pydantic model
class BookRecord(BaseModel):
        product_url:HttpUrl
        title:str
        price_text:str
        availability_text:str
        rating_text:str
        description: Optional[str] =None
        source_page:str
        fetched_at:str
        price_gpb:float

def fetch_with_retry(fetch_url,headers,timeout=5):
    attempt=0
    while attempt <= max_retry:
        try:
            response=requests.get(fetch_url, headers=headers,timeout=timeout)
            response.encoding="utf-8"
        except requests.exceptions.Timeout:
            print(f"Timeout fetching {fetch_url} attempt: {attempt +1}")
            attempt += 1
            time.sleep(2)
            continue
        except requests.exceptions.RequestException as e:
            print(f"Request failed for {fetch_url} : {e}")
            return None

        if response.status_code ==200:
            return response
        elif response.status_code in (403,404):
            print(f"Non-retryable status {response.status_code} for {fetch_url}")
            return None
        elif 500 <= response.status_code <= 600:
            print(f"Server error {response.status_code} for {fetch_url} (attempt {attempt + 1})")
            attempt += 1
            time.sleep(2)
            continue
        else:
            print(f"Unexpected status {response.status_code} for {fetch_url}")
            return None

    print(f"Giving up on {fetch_url} after {max_retry + 1} attempts")
    return None

for i in range(1,4):
    CACHE_PATH=f"cache/catalogue-page-{i}.html"
    
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH,"r",encoding="utf-8") as f:
            html=f.read()
        print(f"Cache HIT-size: {len(html)} bytes")
        cache_hits += 1
    else:
        x=fetch_with_retry(current_url,headers)
        
        if x is None:
            print(f"failed to fetch page:{current_url},skipping this page")
            failed_pages +=1
            break
        else:
            html=x.text
            os.makedirs("cache",exist_ok=True)
            with open(CACHE_PATH,"w",encoding="utf-8") as f:
                f.write(html)
            print(f"FETCH - SIZE: {len(html)} bytes")
            pages_fetched +=1

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
                cache_hits +=1
            else:
                book_resp=fetch_with_retry(absolute_url,headers=headers)

                if book_resp is not None:
                    book_html=book_resp.text
                    with open(BOOK_CACHE_PATH,"w",encoding="utf-8") as f:
                        f.write(book_html)
                    pages_fetched += 1
                else:
                    print(f"Failed to fetch book page {absolute_url}")
                    failed_pages +=1
                    book_html = None

            if book_html is None:
                print(f"Skipping {absolute_url} - no detail page data")
                continue

            book_soup=BeautifulSoup(book_html,"html.parser")

            description=None
            desc_header = book_soup.find("div", id="product_description")
            if desc_header is not None:
                desc_p = desc_header.find_next_sibling("p")
                if desc_p is not None:
                    description = desc_p.text.strip()
            book_description=description

            availability=book_soup.find("p",class_="instock")
            book_availability=availability.text.strip() if availability is not None else None
            if book_availability is None:
                print(f"Skipping {absolute_url} — missing availability.")
                continue      
                

            book_title=book.h3.a["title"]

            price_tag=book.find("p",class_="price_color") 
            book_price=price_tag.text if price_tag is not None else None
            if book_price is None:
                print(f"Skipping {absolute_url} — missing price.")
                continue
            price_gpb=float(book_price.replace("£","").strip())


            ratingclass=book.find("p",class_="star-rating")
            if ratingclass is None:
                    print(f"Skipping {absolute_url} — missing rating.")
                    continue
               
            rating=ratingclass.get("class")
            book_rating=rating[1]

            book_source=CACHE_PATH
            fetch_info=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

            book_data={"product_url":absolute_url,"title":book_title,"price_text":book_price,"availability_text":book_availability,
                       "rating_text":book_rating,"description":book_description,"source_page":book_source,"fetched_at":fetch_info,"price_gpb":price_gpb}

            discovered +=1
            if absolute_url not in seen_urls:
                seen_urls.add(absolute_url)
                all_books.append(book_data)
            
                 
    next_link=soup.find("li",class_="next")
    if next_link is not None:
        next_url=next_link.a["href"]
        current_url=urljoin(current_url,next_url)

validated_records=[]
bad_records=[]
    
for record in all_books:
    try:
        validated=BookRecord(**record)
        validated_records.append(validated)
    except ValidationError as e:
        bad_records.append(
        {"record":record,"reason":str(e)} )

os.makedirs("output", exist_ok=True)

with open("output/books.json","w",encoding="utf-8") as f:
    json.dump([json.loads(r.model_dump_json()) for r in validated_records],f,indent=2,ensure_ascii=False)

with open("errors.json","w",encoding="utf-8") as f:
    json.dump(bad_records,f,indent=2,ensure_ascii=False)


with open("output/books.json", "r", encoding="utf-8") as f:
    data = json.load(f)

print(f"Total records: {len(data)}")

# Check every price_gbp is a number
bad_prices = [r["product_url"] for r in data if not isinstance(r["price_gpb"], (int, float))]
print(f"Records with bad price_gbp type: {len(bad_prices)}")
if bad_prices:
    print(bad_prices)

# Check every product_url starts with https://
bad_urls = [r["product_url"] for r in data if not r["product_url"].startswith("https://")]
print(f"Records with bad URL prefix: {len(bad_urls)}")
if bad_urls:
    print(bad_urls)

end_time=datetime.datetime.now(datetime.timezone.utc)
duration_seconds=(end_time-start_time).total_seconds()

run_report={
    "start_time":start_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
    "duration":duration_seconds,
    "pages_fetched":pages_fetched,
    "cache_hits":cache_hits,
    "valid_records":len(validated_records),
    "invalid_records":len(bad_records),
    "failed_pages":failed_pages,
}

with open("output/run-report.json","w",encoding="utf-8") as f:
    json.dump(run_report,f,indent=2,ensure_ascii=False)

print(f"Run report: {run_report}")
