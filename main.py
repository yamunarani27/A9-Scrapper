import requests

x=requests.get("https://books.toscrape.com/robots.txt")

if not x.ok:
    print("No robots file found")
    print(x.status_code)
else:
    print(x.text)