import streamlit as st
import datetime
import requests

# Sayfa sekmesi ayarları
st.set_page_config(page_title="Özel Takip", page_icon="🌸")

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

# --- ZARİF ARAYÜZ TASARIMI ---
st.title("🌸 Döngü Tahmincisi")
st.write("Hoş geldin! Sana özel takvimi oluşturmak için bilgileri aşağıdan seçebilirsin. ✨")

# 1. Başlangıç Tarihi
baslangic_tarihi = st.date_input("Son regl başlangıç tarihini seçebilir misin?")

# 2. Kaydırma Çubukları (Daha kibar metinlerle)
col1, col2 = st.columns(2)
with col1:
    kanama_suresi = st.slider("Bu dönem ortalama kaç gün sürüyor?", min_value=2, max_value=10, value=5)
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
