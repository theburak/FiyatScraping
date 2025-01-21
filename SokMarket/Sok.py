import pandas as pd
import cloudscraper
from urllib.parse import urlparse,parse_qs,urlencode
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor,as_completed
import os


urunid=[]
urunad=[]
urunfiyat=[]
urunanakategori=[]
urunaltketegori=[]

headers={
    "cookie":"X-Ecommerce-Deviceid=346cfe18-a8f6-4958-92f5-99a090a20795-dbc915c2-9409-4d48-886d-fc86c401a527; X-Ecommerce-Sid=ed35762f-2e49-4277-b875-99ae20339f81-d96b88c0-1854-44ad-928a-eb33e35eefdd; X-Platform=WEB; X-Service-Type=MARKET; access_token=FNlmBCX9Ep544pj9IfZztWgr0ynlG3Dc-a8t7h5rsXEtGhsJhWLUbbFTGXw0qMmS3; X-Store-Id=13412; _gcl_aw=GCL.1735392795.Cj0KCQiA4L67BhDUARIsADWrl7GfhUe7m_JiBy2Ub4rlI0bus8vGO-QFd5MpFXrKdafsQ46M_dGfksIaAtSDEALw_wcB; _gcl_gs=2.1.k1$i1735392794$u158814008; _gcl_au=1.1.1973247259.1735392795; _fbp=fb.2.1735392795161.73291538193259584; _ga=GA1.1.1920777221.1735392797; OptanonAlertBoxClosed=2024-12-28T13:33:19.516Z; _dn_sid=7d64f942-af19-4aa0-82ac-b99caf625080; OptanonConsent=isGpcEnabled=0&datestamp=Sat+Dec+28+2024+16%3A56%3A43+GMT%2B0300+(GMT%2B03%3A00)&version=202308.2.0&browserGpcFlag=0&isIABGlobal=false&hosts=&landingPath=NotLandingPage&groups=C0001%3A1%2CC0002%3A0%2CC0004%3A0%2CC0003%3A0&AwaitingReconsent=false&geolocation=TR%3B06; _ga_97YKG29ZHZ=GS1.1.1735392797.1.1.1735394259.60.0.1734515732",
    "user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-platform":"WEB",
    "x-service-type":"MARKET",
    "x-store-id":"13412"}

def sayfasayısı(url):
    scraper=cloudscraper.CloudScraper()
    r=scraper.get(url,headers=headers)
    return r.json()["page"]["totalPages"]

def veri_cek(url):
    scraper = cloudscraper.CloudScraper()
    r = scraper.get(url, headers=headers)
    results = r.json().get("results", [])

    local_urunid = [result["product"]["id"] for result in results]
    local_urunad = [result["product"]["name"] for result in results]
    local_urunfiyat = [result["prices"]["original"]["value"] for result in results]
    local_urunanakategori = [result["sku"]["breadCrumbs"][1]["label"] for result in results]
    local_urunaltketegori = [result["sku"]["breadCrumbs"][2]["label"] for result in results]

    return local_urunid, local_urunad, local_urunfiyat, local_urunanakategori, local_urunaltketegori

with open("SokMarket/SokLinks.txt","r",encoding="utf-8") as dosya:
    linkler=dosya.readlines()
    temizlinkler=[link.strip() for link in linkler if link.strip()]

with ThreadPoolExecutor() as executor:
    futures = [
        executor.submit(veri_cek, f"https://www.sokmarket.com.tr/api/v1/search?{urlencode({**parse_qs(urlparse(i).query), 'page': [str(j)]}, doseq=True)}")
        for i in temizlinkler
        for j in range(sayfasayısı(i))
    ]

    for future in as_completed(futures):
        local_urunid, local_urunad, local_urunfiyat, local_urunanakategori, local_urunaltketegori = future.result()
        urunid.extend(local_urunid)
        urunad.extend(local_urunad)
        urunfiyat.extend(local_urunfiyat)
        urunanakategori.extend(local_urunanakategori)
        urunaltketegori.extend(local_urunaltketegori)

bugun=datetime.today()
tarih=bugun.strftime("%d-%m-%Y")

veri=pd.DataFrame({"Tarih":tarih,"ID":urunid,"Ürün Ad":urunad,"Fiyat":urunfiyat,"Ürün Ana Kategori":urunanakategori,
    "Ürün Alt Kategori":urunaltketegori})

veri=veri[~veri["Ürün Ad"].duplicated(keep=False)]
veri.reset_index(inplace=True,drop=True)

klasoryolu=f"Fiyatlar/{tarih}"
os.makedirs(klasoryolu,exist_ok=True)

dosyayolu=os.path.join(klasoryolu,"SokFiyat.xlsx")
veri.to_excel(dosyayolu,index=False)
