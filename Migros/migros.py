import pandas as pd
import cloudscraper
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

urunid = []
urunad = []
urunfiyat = []
urunanakategori = []
urunaltketegori = []

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*"
}

def linkduzenle():
    with open("Migros/MigrosLinks.txt", "r", encoding="utf-8") as dosya:
        return [link.strip() for link in dosya if link.strip()]

def sayfasayısı(url):
    scraper = cloudscraper.CloudScraper()
    return scraper.get(url, headers=headers).json()["data"]["searchInfo"]["pageCount"]

def sayfa_verisini_cek(url, sayfa):
    scraper = cloudscraper.CloudScraper()
    response = scraper.get(f"{url}?page={sayfa}", headers=headers).json()
    return response["data"]["searchInfo"]["storeProductInfos"]

temizlinkler = linkduzenle()

with ThreadPoolExecutor(max_workers=5) as executor:
    futures = [
        executor.submit(sayfa_verisini_cek, i, j)
        for i in temizlinkler
        for j in range(1, sayfasayısı(i) + 1)
    ]

    for future in as_completed(futures):
        info = future.result()
        for urun in info:
            urunid.append(urun.get("id"))
            urunad.append(urun.get("name"))
            urunfiyat.append(int(urun.get("salePrice")) / 100)
            kategoriler = urun.get("categoriesForSorting")
            urunanakategori.append(kategoriler[-1].get("name"))
            urunaltketegori.append(kategoriler[0].get("name"))

bugun = datetime.today()
tarih = bugun.strftime("%d-%m-%Y")

veri = pd.DataFrame({
    "Tarih": tarih,
    "ID": urunid,
    "Ürün Ad": urunad,
    "Fiyat": urunfiyat,
    "Ürün Ana Kategori": urunanakategori,
    "Ürün Alt Kategori": urunaltketegori
})

veri = veri[~veri["Ürün Ad"].duplicated(keep=False)]
veri.reset_index(inplace=True, drop=True)

klasoryolu = f"Fiyatlar/{tarih}"
os.makedirs(klasoryolu, exist_ok=True)

dosyayolu = os.path.join(klasoryolu, "MigrosFiyat.xlsx")
veri.to_excel(dosyayolu, index=False)
