import pandas as pd
import cloudscraper
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor,as_completed

urunid=[]
urunad=[]
urunfiyat=[]
urunanakategori=[]
urunaltketegori=[]

headers={"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept":"application/json, text/plain, */*"}

def linkduzenle():
    with open("Migros/MigrosLinks.txt","r",encoding="utf-8") as dosya:
        linkler=dosya.readlines()
    temizlinkler=[link.strip() for link in linkler if link.strip()]
    return temizlinkler

def sayfasayısı(url):
    scraper=cloudscraper.CloudScraper()
    return scraper.get(url,headers=headers).json()["data"]["searchInfo"]["pageCount"]

def sayfa_verisini_cek(url,sayfa):
    scraper=cloudscraper.CloudScraper()
    response=scraper.get(f"{url}?page={sayfa}",headers=headers).json()
    return response["data"]["searchInfo"]["storeProductInfos"]

temizlinkler=linkduzenle()

with ThreadPoolExecutor(max_workers=5) as executor:
    futures=[]
    for i in temizlinkler:
        sayfa_sayisi=sayfasayısı(i)
        for j in range(1,sayfa_sayisi+1):
            futures.append(executor.submit(sayfa_verisini_cek,i,j))
    
    for future in as_completed(futures):
        info=future.result()
        for urun in info:
            urunid.append(urun.get("id"))
            urunad.append(urun.get("name"))
            urunfiyat.append(int(urun.get("salePrice"))/100)
            kategoriler=urun.get("categoriesForSorting")
            urunanakategori.append(kategoriler[-1].get("name"))
            urunaltketegori.append(kategoriler[0].get("name"))

bugun=datetime.today()
tarih=bugun.strftime("%d-%m-%Y")

veri=pd.DataFrame({"Tarih":tarih,"ID":urunid,"Ürün Ad":urunad,"Fiyat":urunfiyat,
                   "Ürün Ana Kategori":urunanakategori,"Ürün Alt Kategori":urunaltketegori})
veri=veri[~veri["Ürün Ad"].duplicated(keep=False)]
veri.reset_index(inplace=True,drop=True)
veri.to_excel("Migros/MigrosFiyat.xlsx",index=False)
