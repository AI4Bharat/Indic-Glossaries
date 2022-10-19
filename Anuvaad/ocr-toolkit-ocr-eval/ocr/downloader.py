import pandas as pd
import requests
from bs4 import BeautifulSoup
import requests
import csv
from lxml import html
import time
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import os

# This file downloads all the pdfs off the cstt website.
# Run after cstt_scraper.py

domains = {
    "science": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20science&search55=Submit",
    "engineering-technology": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20eng&search55=Submit",
    "medical science": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20medical&search55=Submit",
    "humanities-social-science": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20humanities&search55=Submit",
    "agriculture-veterinary-science": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=agricul%20vet%20science%20&search55=Submit",
    "administrative": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20at&search55=Submit",
    "departmental": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=departmental&search55=Submit",
    "learners": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20learner&search55=Submit",
    "fundamentals": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=fundamental&search55=Submit",
    "miscellaneous": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=glo%20misc&search55=Submit",
    "agriculture": "http://www.csttpublication.mhrd.gov.in/english/result.php?search=Shabdh%20Sangrah%20Brahat&search55=Submit",
    
}
session = requests.Session()
retry = Retry(connect=3, backoff_factor=0.5)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)
ctr = 0
titles = []
try:
    os.mkdir(f'glossary_downloaded')
except:
    pass
for domain in domains.keys():
    try:
        os.mkdir(f'glossary_downloaded/{domain}')
    except:
        pass
    df = pd.read_csv(f'glossary/{domain}.tsv', index_col=None, header=0, sep='\t')
    df["pages"].astype("int")
    books = [x for x in df["title"]]
    urls = [x for x in df["url"]]
    pages = [x for x in df["pages"]]
    for i in range(len(books)):
        ctr += 1
        if books[i] in titles:
            continue
        titles.append(books[i])
        print(books[i], flush=True)
        images = [ f"page{j + 1}.jpg" for j in range(pages[i]) ]
        for j in range(pages[i]):
            img_link = urls[i] + '/content/pages/' + images[j]
            img_response = None
            try:
                img_response = session.get(img_link)
            except:
                session.close()
                time.sleep(15)
                session = requests.Session()
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                img_response = session.get(img_link)

            # print(img_link, flush=True)
            with open(f'glossary_downloaded/{domain}/{images[j]}', 'wb') as f:
                f.write(img_response.content)
        images = [f'glossary_downloaded/{domain}/{images[j]}' for j in range(pages[i])]
        from PIL import Image
        images_ = []
        for f in images:
            try:
                images_.append(Image.open(f))
            except:
                pass

        
                        

        pdf_path = f'glossary_downloaded/{domain}/{books[i]}.pdf'
        if (len(images_)>0):
                
            images_[0].save(
                pdf_path, "PDF" ,resolution=100.0, save_all=True, append_images=images_[1:]
            )
        for f in images:
            os.remove(f)
session.close()


