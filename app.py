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
# O kırmızıyla çizdiğin gereksiz yazıyı tamamen sildik!

# --- AKILLI TAHMİN MESAJI ---
hesaplanan_ortalama = notiondan_ortalama_oku()
# BURAYI ESKİ HALİNE GETİRDİM, İÇİNE KENDİ CÜMLENİ YAZABİLİRSİN:
st.info(f"✨ Önümüzdeki dönemin ortalama **{hesaplanan_ortalama} gün** sürmesi bekleniyor.")

# 1. Başlangıç Tarihi (Her zaman girilecek)
baslangic_tarihi = st.date_input("Başlangıç Tarihi 🩸")

# 2. Döngü Bitti mi? (Mühendislik Çözümü)
dongu_bitti_mi = st.checkbox("Bu döngü sona erdi (Bitiş tarihini takvimden seç)")

if dongu_bitti_mi:
    # Eğer bittiyse gerçek bitiş tarihini kendi seçer
    bitis_tarihi = st.date_input("Bitiş Tarihi 🌸", value=baslangic_tarihi)
else:
    # Eğer henüz bitmediyse, sistem ortalamayı baz alarak arka planda otomatik bir bitiş belirler
    bitis_tarihi = baslangic_tarihi + datetime.timedelta(days=hesaplanan_ortalama)

# 3. Döngü Uzunluğu (Gelecek ayı tahmin etmek için)
st.write("") 
dongu_uzunlugu = st.slider("İki döngü arası ortalama kaç gün sürüyor?", min_value=21, max_value=35, value=28)

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

# 6. Kaydet Butonu ve Kutlama Mesajı
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
    # Kullanıcı bitiş tarihini seçmeyi unutursa çıkacak kibar uyarı
    st.warning("İşleme devam edebilmek için takvim üzerinden bir de **bitiş tarihi** seçmelisin. (Takvime iki kere tıklayabilirsin) ✨")
