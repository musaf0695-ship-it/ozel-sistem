import streamlit as st
import datetime
import requests
import calendar 

# Sayfa sekmesi ayarları
st.set_page_config(page_title="Özel Takvim", page_icon="🌸")

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
DATABASE_ID = st.secrets["DATABASE_ID"]

headers = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28"
}

# --- AKILLI KAYIT & GÜNCELLEME MOTORU ---
def veriyi_notiona_gonder(mod, baslangic, bitis, gelecek, page_id=None):
    veri = {
        "properties": {
            "İşlem": {"title": [{"text": {"content": mod}}]},
            "Başlangıç": {"date": {"start": str(baslangic)}}
        }
    }
    
    if bitis:
        veri["properties"]["Bitiş"] = {"date": {"start": str(bitis)}}
    if gelecek:
        veri["properties"]["Gelecek Beklenen"] = {"date": {"start": str(gelecek)}}

    if page_id:
        url = f"https://api.notion.com/v1/pages/{page_id}"
        cevap = requests.patch(url, headers=headers, json=veri)
    else:
        url = "https://api.notion.com/v1/pages"
        veri["parent"] = {"database_id": DATABASE_ID}
        cevap = requests.post(url, headers=headers, json=veri)
        
    return cevap.status_code

# --- YENİ BİRLEŞTİRİLMİŞ ZEKİ MOTOR ---
def notion_verilerini_analiz_et():
    url = f"https://api.notion.com/v1/databases/{DATABASE_ID}/query"
    ortalama_kanama = 5
    ortalama_dongu = 28
    gecmis_gunler_seti = set()
    aktif_page_id = None
    aktif_baslangic = None
    
    try:
        res = requests.post(url, headers=headers)
        if res.status_code == 200:
            sonuclar = res.json().get("results", [])
            toplam_kanama = 0
            kanama_sayaci = 0
            baslangic_tarihleri = []
            bugun = datetime.date.today()
            
            for kayit in sonuclar:
                props = kayit.get("properties", {})
                bas_kutu = props.get("Başlangıç", {}).get("date")
                bit_kutu = props.get("Bitiş", {}).get("date")
                kayit_id = kayit.get("id")
                
                if bas_kutu and bas_kutu.get("start"):
                    bas_str = bas_kutu.get("start").split('T')[0]
                    bas_tarih = datetime.datetime.strptime(bas_str, "%Y-%m-%d").date()
                    baslangic_tarihleri.append(bas_tarih)
                    
                    if bit_kutu and bit_kutu.get("start"):
                        bit_str = bit_kutu.get("start").split('T')[0]
                        bit_tarih = datetime.datetime.strptime(bit_str, "%Y-%m-%d").date()
                        fark = (bit_tarih - bas_tarih).days
                        
                        if 0 <= fark <= 15: 
                            toplam_kanama += fark
                            kanama_sayaci += 1
                            for i in range(fark + 1):
                                gecmis_gunler_seti.add(bas_tarih + datetime.timedelta(days=i))
                    else:
                        aktif_page_id = kayit_id
                        aktif_baslangic = bas_tarih
                        
                        fark = (bugun - bas_tarih).days
                        if fark >= 0:
                            boyanacak_gun = min(fark, 15)
                            for i in range(boyanacak_gun + 1):
                                gecmis_gunler_seti.add(bas_tarih + datetime.timedelta(days=i))
            
            if kanama_sayaci > 0:
                ortalama_kanama = round(toplam_kanama / kanama_sayaci)
                if ortalama_kanama == 0: ortalama_kanama = 1
                
            if len(baslangic_tarihleri) >= 2:
                baslangic_tarihleri.sort()
                toplam_dongu = 0
                dongu_sayaci = 0
                for i in range(1, len(baslangic_tarihleri)):
                    fark = (baslangic_tarihleri[i] - baslangic_tarihleri[i-1]).days
                    if 21 <= fark <= 35:
                        toplam_dongu += fark
                        dongu_sayaci += 1
                if dongu_sayaci > 0:
                    ortalama_dongu = round(toplam_dongu / dongu_sayaci)
    except Exception:
        pass
        
    return ortalama_kanama, ortalama_dongu, gecmis_gunler_seti, aktif_page_id, aktif_baslangic

# --- GÖRSEL TAKVİM ÇİZİCİ ---
def aylik_takvim_ciz(yil, ay, gelecek_gunler, gecmis_gunler):
    cal = calendar.monthcalendar(yil, ay)
    ay_isimleri = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
    gun_isimleri = ["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]
    
    html = f"""
    <div style="background-color: rgba(255, 255, 255, 0.75); padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
        <h4 style="color: #d81b60; margin-bottom: 5px; margin-top: 5px; font-family: sans-serif;">{ay_isimleri[ay]} {yil}</h4>
        <table style="width: 100%; border-collapse: collapse; font-family: sans-serif; font-size: 15px;">
            <tr>
    """
    for gun in gun_isimleri:
        html += f'<th style="padding: 5px; color: #666;">{gun}</th>'
    html += "</tr>"
    
    for hafta in cal:
        html += "<tr>"
        for gun in hafta:
            if gun == 0:
                html += "<td></td>"
            else:
                guncel_tarih = datetime.date(yil, ay, gun)
                if guncel_tarih in gecmis_gunler:
                    html += f'<td><div style="background-color: #58b3a4; color: white; border-radius: 50%; width: 28px; height: 28px; line-height: 28px; margin: 2px auto; font-weight: bold; box-shadow: 0 2px 4px rgba(88, 179, 164, 0.5);">{gun}</div></td>'
                elif guncel_tarih in gelecek_gunler:
                    html += f'<td><div style="background-color: #ff8fa3; color: white; border-radius: 50%; width: 28px; height: 28px; line-height: 28px; margin: 2px auto; font-weight: bold; box-shadow: 0 2px 4px rgba(255, 143, 163, 0.5);">{gun}</div></td>'
                else:
                    html += f'<td style="padding: 5px; color: #333;">{gun}</td>'
        html += "</tr>"
        
    html += "</table></div>"
    return html

# --- ARKA PLAN TASARIMI VE GÜVENLİK ---
arkaplan_kodu = f"""
<style>
.stApp {{
    background-color: white !important;
    background-image: linear-gradient(rgba(255, 255, 255, 0.05), rgba(255, 255, 255, 0.05)), url("https://raw.githubusercontent.com/musaf0695-ship-it/ozel-sistem/main/lilyum_arka_plan.jpg") !important;
    background-size: cover !important;
    background-position: center !important;
    background-attachment: fixed !important;
}}
[data-testid="stToolbar"] {{ visibility: hidden !important; display: none !important; }}
[data-testid="stHeader"] {{ background: transparent !important; height: 0px !important; }}
#MainMenu {{ visibility: hidden !important; display: none !important; }}
footer {{ visibility: hidden !important; display: none !important; }}
</style>
"""
st.markdown(arkaplan_kodu, unsafe_allow_html=True)

# --- ZARİF ARAYÜZ TASARIMI ---
st.title("🌸 Güzel Yavruma ...")

hesaplanan_ortalama, hesaplanan_dongu, gecmis_gunler_seti, aktif_page_id, aktif_baslangic = notion_verilerini_analiz_et()

st.info(f"✨ Önümüzdeki dönemin ortalama **{hesaplanan_ortalama} gün** sürmesi bekleniyor.")

if aktif_baslangic:
    st.success("💧 Şu anda aktif bir döngü devam ediyor. Takvim anlık olarak yeşile boyanıyor!")
    varsayilan_baslangic = aktif_baslangic
else:
    varsayilan_baslangic = datetime.date.today()

baslangic_tarihi = st.date_input("Başlangıç Tarihi 🏗️🩸", value=varsayilan_baslangic)

dongu_bitti_mi = st.checkbox("Bu döngü sona erdi (Bitiş tarihini takvimden seç)")

if dongu_bitti_mi:
    bitis_tarihi = st.date_input("Bitiş Tarihi 🌸", value=baslangic_tarihi)
    kayit_icin_bitis = bitis_tarihi
else:
    kayit_icin_bitis = None 
    bitis_tarihi = baslangic_tarihi + datetime.timedelta(days=hesaplanan_ortalama)

st.write("") 
dongu_uzunlugu = st.number_input("İki döngü arası ortalama kaç gün sürüyor?", min_value=21, max_value=35, value=hesaplanan_dongu, step=1)

gelecek_ay_baslangic = baslangic_tarihi + datetime.timedelta(days=dongu_uzunlugu)

st.divider()

# --- TAKVİM KONTROL PANELİ ---
st.subheader("Takvim & Tahmin Haritası 🗓️")

if 'ay_ofseti' not in st.session_state:
    st.session_state.ay_ofseti = 0

col_sol, col_orta, col_sag = st.columns([1, 2, 1])
with col_sol:
    if st.button("◀ Önceki Ay"):
        st.session_state.ay_ofseti -= 1
with col_sag:
    if st.button("Sonraki Ay ▶"):
        st.session_state.ay_ofseti += 1

gelecek_kanama_gunleri = set()
gecici_tarih = baslangic_tarihi
for _ in range(12):
    gecici_tarih += datetime.timedelta(days=dongu_uzunlugu)
    for i in range(hesaplanan_ortalama):
        gelecek_kanama_gunleri.add(gecici_tarih + datetime.timedelta(days=i))

bugun = datetime.date.today()
gosterilecek_ay = bugun.month + st.session_state.ay_ofseti
gosterilecek_yil = bugun.year

while gosterilecek_ay > 12:
    gosterilecek_ay -= 12
    gosterilecek_yil += 1
while gosterilecek_ay < 1:
    gosterilecek_ay += 12
    gosterilecek_yil -= 1

st.markdown(aylik_takvim_ciz(gosterilecek_yil, gosterilecek_ay, gelecek_kanama_gunleri, gecmis_gunler_seti), unsafe_allow_html=True)

st.markdown("""
<div style="text-align: center; margin-bottom: 15px; font-size: 14px;">
    <span style="color: #58b3a4; font-weight: bold;">🟢 Su Yeşili:</span> Geçmiş & Kaydedilen &nbsp; | &nbsp; 
    <span style="color: #ff8fa3; font-weight: bold;">🔴 Pembe:</span> Gelecek Tahmini
</div>
""", unsafe_allow_html=True)

st.divider()

gosterge_kolon1, gosterge_kolon2 = st.columns(2)
with gosterge_kolon1:
    st.metric(label="Bu Döngünün Bitişi", value=bitis_tarihi.strftime("%d.%m.%Y"))
with gosterge_kolon2:
    st.metric(label="Bir Sonraki Beklenen", value=gelecek_ay_baslangic.strftime("%d.%m.%Y"))

st.divider()

if st.button("Bilgileri Kaydet 💌"):
    durum_kodu = veriyi_notiona_gonder(
        mod="Regl Döngüsü", 
        baslangic=baslangic_tarihi, 
        bitis=kayit_icin_bitis, 
        gelecek=gelecek_ay_baslangic,
        page_id=aktif_page_id 
    )
    
    if durum_kodu == 200:
        st.success("Harika! Tarihler başarıyla kaydedildi. Her şey kontrol altında! 😎💖")
        st.balloons()
    else:
        st.error("Bir hata oluştu. Lütfen bağlantıları kontrol et.")
