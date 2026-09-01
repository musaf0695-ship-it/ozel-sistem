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

# --- YENİ EKLENEN ZEKİ ALGORİTMA (Geçmişi Okuma) ---
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
                        # Gelen tarihleri matematiksel işleme sokuyoruz
                        bas_tarih = datetime.datetime.strptime(bas_str.split('T')[0], "%Y-%m-%d").date()
                        bit_tarih = datetime.datetime.strptime(bit_str.split('T')[0], "%Y-%m-%d").date()
                        fark = (bit_tarih - bas_tarih).days
                        
                        # 1 ile 15 gün arasındaki mantıklı verileri ortalamaya kat
                        if 1 <= fark <= 15: 
                            toplam_gun += fark
                            sayac += 1
                            
            if sayac > 0:
                return round(toplam_gun / sayac)
    except Exception:
        pass
    return 5 # Eğer tabloda hiç veri yoksa varsayılan olarak 5 döner

# --- ARKA PLAN TASARIMI (CSS ENJEKSİYONU) ---
arkaplan_kodu = f"""
<style>
/* Ana Arka Plan ve Şeffaflık Ayarı */
.stApp {{
    background-image: linear-gradient(rgba(255, 255, 255, 0.45), rgba(255, 255, 255, 0.45)), url("https://raw.githubusercontent.com/musaf0695-ship-it/ozel-sistem/main/lilyum_arka_plan.jpg") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}

/* Üstteki inatçı pembe şeridi şeffaf yapma */
[data-testid="stHeader"] {{
    background: transparent !important;
}}
</style>
"""
st.markdown(arkaplan_kodu, unsafe_allow_html=True)

# --- ZARİF ARAYÜZ TASARIMI ---
st.title("🌸 Güzel Yavruma ...")
st.write("Hoş geldin! Sana özel takvimi oluşturmak için bilgileri aşağıdan seçebilirsin. ✨")

# 1. Başlangıç Tarihi
baslangic_tarihi = st.date_input("Son regl başlangıç tarihini seçebilir misin?")

# --- AKILLI TAHMİN MESAJI ---
hesaplanan_ortalama = notiondan_ortalama_oku()
st.info(f"✨ Önümüzdeki dönemin ortalama **{hesaplanan_ortalama} gün** sürmesi bekleniyor.")

# 2. Kaydırma Çubukları (Daha kibar metinlerle)
col1, col2 = st.columns(2)
with col1:
    kanama_suresi = st.slider("Bu dönem ortalama kaç gün sürüyor?", min_value=2, max_value=10, value=hesaplanan_ortalama)
with col2:
    dongu_uzunlugu = st.slider("İki döngü arası ortalama kaç gün?", min_value=21, max_value=35, value=28)

# 3. Hesaplamalar
tahmini_bitis = baslangic_tarihi + datetime.timedelta(days=kanama_suresi)
gelecek_ay_baslangic = baslangic_tarihi + datetime.timedelta(days=dongu_uzunlugu)

st.divider()
st.subheader("Gelecek Ayın Özeti 🗓️")

# 4. Şık Göstergeler
gosterge_kolon1, gosterge_kolon2 = st.columns(2)
with gosterge_kolon1:
    st.metric(label="Tahmini Bitiş Tarihi", value=tahmini_bitis.strftime("%d.%m.%Y"))
with gosterge_kolon2:
    st.metric(label="Bir Sonraki Beklenen", value=gelecek_ay_baslangic.strftime("%d.%m.%Y"))

st.divider()

# 5. Kaydet Butonu ve Kutlama Mesajı
if st.button("Bilgileri Kaydet 💌"):
    durum_kodu = veriyi_notiona_gonder(
        mod="Regl Döngüsü", 
        baslangic=baslangic_tarihi, 
        bitis=tahmini_bitis, 
        gelecek=gelecek_ay_baslangic
    )
    
    if durum_kodu == 200:
        st.success("Harika! Tarihler başarıyla kaydedildi ve hesaplandı. 💖")
        st.balloons()
    else:
        st.error("Bir hata oluştu. Lütfen bağlantıları kontrol et.")
