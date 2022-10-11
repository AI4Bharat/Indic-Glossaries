
import pandas as pd
import requests
import time
from bs4 import BeautifulSoup

# This file is used to crawl all the pdfs off the website and store them in glossary/domain.

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

comprehensive = {
    "science_a-b": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_I_(A-B)",
    "science_c-d": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_II_(C-D)",
    "science_e-g": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_III_(E-G)",
    "science_h-l": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_IV_(H-L)",
    "science_m-o": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_V_(M-O)",
    "science_p-r": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_VI_(P-R)",
    "science_s": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_VII_(S)",
    "science_t-z": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Science_Vol_-_VIII_(T-Z)",
    "hss_a-c": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Humanities_and_Social_Science_Vol_-_IX_(A-C)",
    "hss_d-h": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Humanities_and_Social_Science_Vol_-_X_(D-H)",
    "hss_i-o": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Humanities_and_Social_Science_Vol_-_XI_(I-O)",
    "hss_p-s": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Humanities_and_Social_Science_Vol_-_XII_(P-S)",
    "hss_t-z": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Humanities_and_Social_Science_Vol_-_XIII_(T-Z)",
    "medical_a-e": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Medical_Science_Volume-XVIII_(A-E)",
    "medical_f-o": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Medical_Science_Volume-XIX_(F-O)",
    "medical_p-z": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Medical_Science_Volume-XX_(P-Z)",
    "math_a-z": "http://www.csttpublication.mhrd.gov.in/ebook/Comprehensive_Glossary_of_Mathematics_Vol._-_XXI_(A-Z)"
}
overall = []
for domain, URL in domains.items():
    
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, "html.parser")

    results = soup.find_all("div", class_="box-prod group-book")
    # print(results)

    BASE = 'http://www.csttpublication.mhrd.gov.in'
    urls = []
    for r in results:
        dict_ = {}
        url_obj = r.find("div", class_="box-img-book")
        dict_['url'] = BASE + url_obj.find('a').get('href').split('..')[1]
        try:
            dict_['title'] = r.find_all('h5')[0].text.strip()
        except:
            dict_['title'] = r.find_all('h4')[0].text.strip()
        if dict_['title'] in overall:
            continue
        else:
            overall.append(dict_['title'])
        page_book = requests.get(dict_['url'] + 'data/pages.xml')
        #time.sleep(1)
        book_soup = BeautifulSoup(page_book.content, 'html.parser')
        print(dict_["url"], flush = True)
        try:
            dict_['pages'] = len(book_soup.find_all('page'))
        except:
            continue
        urls.append(dict_)

    df = pd.DataFrame(urls, columns = ["url", "title", "pages"])
    df.to_csv(f'glossary/{domain}.tsv', index=False, sep='\t')

