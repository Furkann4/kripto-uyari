import os
import requests
import ccxt

COINLER = ["SOL", "XRP", "NEAR", "HYPE", "TIA", "AVAX"]
TEST = os.getenv("TEST", "0") == "1"
ESIK = 0.05 if TEST else float(os.getenv("ESIK", "2.5"))  # 15 dk'da yüzde
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


def telegram_gonder(mesaj):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    cevap = requests.post(url, data={"chat_id": CHAT_ID, "text": mesaj}, timeout=15)
    print("Telegram:", cevap.status_code)


def degisim(kapanislar, i):
    # i. mumun kapanışı ile 3 mum (15 dk) öncesinin kapanışı arasındaki yüzde değişim
    return (kapanislar[i] - kapanislar[i - 3]) / kapanislar[i - 3] * 100


exchange = ccxt.okx()  # sadece okuma, emir vermez
uyarilar = []

for coin in COINLER:
    try:
        mumlar = exchange.fetch_ohlcv(f"{coin}/USDT:USDT", timeframe="5m", limit=12)
        kapanis = [m[4] for m in mumlar]
        simdi = degisim(kapanis, -1)
        onceki = degisim(kapanis, -4)  # 15 dk önceki durum
        fiyat = kapanis[-1]
        print(f"{coin}: %{simdi:+.2f} (fiyat {fiyat})")

        if abs(simdi) >= ESIK and (TEST or abs(onceki) < ESIK):
            if simdi > 0:
                uyarilar.append(f"🟢 {coin} 15 dk'da %{simdi:+.2f} yükseldi (fiyat {fiyat}). Long düşünebilirsin.")
            else:
                uyarilar.append(f"🔴 {coin} 15 dk'da %{simdi:+.2f} düştü (fiyat {fiyat}). Short düşünebilirsin.")
    except Exception as hata:
        print(f"{coin} hata:", hata)

if uyarilar:
    baslik = "🧪 TEST\n" if TEST else ""
    telegram_gonder(baslik + "\n".join(uyarilar) + "\nKarar ve risk sende.")
else:
    print("Ani hareket yok.")
