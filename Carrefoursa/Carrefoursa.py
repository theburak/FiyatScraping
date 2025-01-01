import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import time
from datetime import datetime
import os

chrome_options=Options()
chrome_options.add_argument("--headless")
service=Service(ChromeDriverManager().install())
driver=webdriver.Chrome(service=service, options=chrome_options)

def linkduzenle():
    with open("Carrefoursa/CarfLinks.txt","r",encoding="utf-8") as dosya:
        linkler=dosya.readlines()
    temizlinkler=[link.strip() for link in linkler if link.strip()]
    return temizlinkler


def altkategori(url):
    driver.get(url)
    time.sleep(7)
    kaynak=driver.page_source
    s=BeautifulSoup(kaynak,"html.parser")
    div_elements=s.find_all("span",{"class":"cat-title"})

    altkat=[]

    for div in div_elements:
        a_tags=div.find_all("a",href=True)
        for a in a_tags:
           altkat.append("https://www.carrefoursa.com"+a['href']+"?q=%3AbestSeller&show=All")
    return altkat


urunid=[]
urunad=[]
urunfiyat=[]
urunanakategori=[]
urunaltketegori=[]

url_listesi=linkduzenle()

for url in url_listesi:
    alt_kategoriler=altkategori(url) 

    for alt_url in alt_kategoriler:
        driver.get(alt_url)
        time.sleep(7)
        kaynak=driver.page_source
        s=BeautifulSoup(kaynak,"html.parser")
        
        a=s.find("ul",{"class":"product-listing product-grid container-fluid add_to_cart"}).find_all("li", {"class": "product-listing-item"})
        b=s.find("ol",{"class":"breadcrumb"})
        li=b.find_all("li")
        
        ana_kategori=(li[1].get_text(strip=True))
        alt_kategori=(li[2].get_text(strip=True))
        
        
        for i in a:
            urun=i.find("div", {"class": "product_click"})
            if urun and urun.has_attr('id'):
                urunid.append(urun['id'])
                ad=i.find("h3", {"class": "item-name"})
                urunad.append(ad.text)
            
            fiyat=i.find("span", {"class": "item-price js-variant-discounted-price"})
            if not fiyat:
                fiyat=i.find("span", {"class": "item-price js-variant-discounted-price unit-price-pos"})
            if fiyat and fiyat.has_attr('content'):
                urunfiyat.append(fiyat['content'])
                urunanakategori.append(ana_kategori)
                urunaltketegori.append(alt_kategori)

bugun=datetime.today()
tarih=bugun.strftime("%d-%m-%Y")

veri=pd.DataFrame({"Tarih":tarih,"ID":urunid,"Ürün Ad":urunad,"Fiyat":urunfiyat,
                "Ürün Ana Kategori":urunanakategori,"Ürün Alt Kategori":urunaltketegori})

veri=veri[~veri["Ürün Ad"].duplicated(keep=False)]
veri.reset_index(inplace=True,drop=True)
veri["Fiyat"]=veri["Fiyat"].apply(lambda x: "{:.2f}".format(float(x)).replace('.', ','))

klasoryolu=f"Fiyatlar/{tarih}"
os.makedirs(klasoryolu,exist_ok=True)

dosyayolu=os.path.join(klasoryolu,"CarrefoursaFiyat.xlsx")
veri.to_excel(dosyayolu,index=False)