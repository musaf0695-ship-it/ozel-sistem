import streamlit as st
import datetime
import requests

# Sayfa sekmesi ayarları
st.set_page_config(page_title="Özel Takvim", page_icon="🌸")

# Şifreleri güvenli kasadan çekme
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

def veriyi_notiona_gonder(mod, baslangic, bitis, gelecek):
    url = "https://api.notion.com/v1/pages"
    
    veri = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "İşlem": {"title": [{"text": {"content": mod}}]},
            "Başlangıç": {"date": {"start": str(baslangic)}},
            "Bitiş": {"date": {"start": str(bitis)}},
            "Gelecek Beklenen": {"date": {"start": str(gelecek)}}
        }
    }
    
    cevap = requests.post(url, headers=headers, json=veri)
    return cevap.status_code

# --- ZEKİ ALGORİTMA 1 (Kanama Süresi Ortalaması) ---
def notiondan_ortalama_oku():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            sonuclar = res.json().get("results", [])
            toplam_gun = 0
            sayac = 0
            for kayit in sonuclar:
                props = kayit.get("properties", {})
                
                bas_kutu = props.get("Başlangıç", {}).get("date")
                bit_kutu = props.get("Bitiş", {}).get("date")
                
                if bas_kutu and bit_kutu:
                    bas_str = bas_kutu.get("start")
                    bit_str = bit_kutu.get("start")
                    
                    if bas_str and bit_str:
                        bas_tarih = datetime.datetime.strptime(bas_str.split('T')[0], "%Y-%m-%d").date()
                        bit_tarih = datetime.datetime.strptime(bit_str.split('T')[0], "%Y-%m-%d").date()
                        fark = (bit_tarih - bas_tarih).days
                        
                        if 1 <= fark <= 15: 
                            toplam_gun += fark
                            sayac += 1
                            
            if sayac > 0:
                return round(toplam_gun / sayac)
    except Exception:
        pass
    return 5 

# --- ZEKİ ALGORİTMA 2 (İki Döngü Arası Süre Ortalaması) ---
def notiondan_dongu_uzunlugu_oku():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    try:
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            sonuclar = res.json().get("results", [])
            baslangic_tarihleri = []
            
            for kayit in sonuclar:
                props = kayit.get("properties", {})
                bas_kutu = props.get("Başlangıç", {}).get("date")
                if bas_kutu and bas_kutu.get("start"):
                    bas_str = bas_kutu.get("start").split('T')[0]
                    bas_tarih = datetime.datetime.strptime(bas_str, "%Y-%m-%d").date()
                    baslangic_tarihleri.append(bas_tarih)
            
            # Tarihleri sıralayıp aralarındaki gün farkını hesaplıyoruz
            if len(baslangic_tarihleri) >= 2:
                baslangic_tarihleri.sort()
                toplam_fark = 0
                sayac = 0
                for i in range(1, len(baslangic_tarihleri)):
                    fark = (baslangic_tarihleri[i] - baslangic_tarihleri[i-1]).days
                    if 21 <= fark <= 35:
                        toplam_fark += fark
                        sayac += 1
                if sayac > 0:
                    return round(toplam_fark / sayac)
    except Exception:
        pass
    return 28 # Veri yoksa varsayılan 28 kalır

# --- ARKA PLAN TASARIMI VE GÜVENLİK (CSS ENJEKSİYONU) ---
arkaplan_kodu = f"""
<style>
/* 1. Arka Plan Parlaklığını Artırma (Çiçekler artık capcanlı) */
.stApp {{
    background-color: white !important;
    background-image: linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05)), url("https://raw.githubusercontent.com/musaf0695-ship-it/ozel-sistem/main/lilyum_arka_plan.jpg") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}

/* 2. Üst Şeridi, GitHub İkonunu ve Menüyü Tamamen Gizleme */
[data-testid="stToolbar"] {{
    visibility: hidden !important;
    display: none !important;
}}
[data-testid="stHeader"] {{
    background: transparent !important;
    height: 0px !important;
}}
#MainMenu {{
    visibility: hidden !important;
    display: none !important;
}}
footer {{
    visibility: hidden !important;
    display: none !important;
}}
</style>
"""
st.markdown(arkaplan_kodu, unsafe_allow_html=True)

# --- ZARİF ARAYÜZ TASARIMI ---
st.title("🌸 Güzel Yavruma ...")

# AKILLI ALGORİTMALARI ÇALIŞTIRMA
hesaplanan_ortalama = notiondan_ortalama_oku()
hesaplanan_dongu = notiondan_dongu_uzunlugu_oku()

st.info(f"✨ Önümüzdeki dönemin ortalama **{hesaplanan_ortalama} gün** sürmesi bekleniyor.")

# 1. Başlangıç Tarihi
baslangic_tarihi = st.date_input("Başlangıç Tarihi 🩸")

# 2. Döngü Bitti mi?
dongu_bitti_mi = st.checkbox("Bu döngü sona erdi (Bitiş tarihini takvimden seç)")

if dongu_bitti_mi:
    bitis_tarihi = st.date_input("Bitiş Tarihi 🌸", value=baslangic_tarihi)
else:
    bitis_tarihi = baslangic_tarihi + datetime.timedelta(days=hesaplanan_ortalama)

# 3. Döngü Uzunluğu (Değer artık akıllı algoritmadan geliyor)
st.write("") 
dongu_uzunlugu = st.slider("İki döngü arası ortalama kaç gün sürüyor?", min_value=21, max_value=35, value=hesaplanan_dongu)

# 4. Gelecek Ay Hesaplaması
gelecek_ay_baslangic = baslangic_tarihi + datetime.timedelta(days=dongu_uzunlugu)

st.divider()
st.subheader("Gelecek Ayın Özeti 🗓️")

# 5. Şık Göstergeler
gosterge_kolon1, gosterge_kolon2 = st.columns(2)
with gosterge_kolon1:
    st.metric(label="Bu Döngünün Bitişi", value=bitis_tarihi.strftime("%d.%m.%Y"))
with gosterge_kolon2:
    st.metric(label="Bir Sonraki Beklenen", value=gelecek_ay_baslangic.strftime("%d.%m.%Y"))

st.divider()

# 6. Kaydet Butonu
if st.button("Bilgileri Kaydet 💌"):
    durum_kodu = veriyi_notiona_gonder(
        mod="Regl Döngüsü", 
        baslangic=baslangic_tarihi, 
        bitis=bitis_tarihi, 
        gelecek=gelecek_ay_baslangic
    )
    
    if durum_kodu == 200:
        st.success("Harika! Tarihler başarıyla kaydedildi. Her şey kontrol altında! 😎💖")
        st.balloons()
    else:
        st.error("Bir hata oluştu. Lütfen bağlantıları kontrol et.")
