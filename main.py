import requests
import os

headers={"User-Agent" : "FlyRankInternship-A9/1.0 (+https://github.com/yamunarani27/A9-Scrapper)"}
url="https://books.toscrape.com/"
CACHE_PATH="cache/catalogue-page-1.html"

if os.path.exists(CACHE_PATH):
    with open(CACHE_PATH,"r",encoding="utf-8") as f:
        html=f.read()
    print(f"Cache HIT-size: {len(html)} bytes")
else:
    x=requests.get(url, headers=headers,timeout=5)

    statuscode=x.status_code
    if statuscode != 200:
        print(f"failed to fetch page:{statuscode}")
    else:
        html=x.text
        os.makedirs("cache",exist_ok=True)
        with open(CACHE_PATH,"w",encoding="utf-8") as f:
            f.write(html)
        print(f"FETCH - SIZE: {len(html)} bytes")