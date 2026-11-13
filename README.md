# 🖥️ Discord Sistem Durum Botu

Sunucunuzun veya kişisel bilgisayarınızın **CPU**, **RAM**, **disk** ve **ağ** durumunu izleyen ve bu bilgileri Discord sohbet kanalına şık kartlar hâlinde gönderen bir Python botu.

---

## ✨ Özellikler

- 🧠 **CPU kullanımı** (yüzde olarak)
- 💾 **RAM kullanımı** (yüzde, kullanılan / toplam MB)
- 📀 **Disk kullanımı** (yüzde, kullanılan / toplam GB)
- 🌐 **Ağ hızı** (gelen ve giden veri, KB/s)
- 📨 `!durum` komutu ile anlık rapor
- ⏰ Her 10 dakikada bir otomatik rapor
- 🎨 Kaynaklardan biri yüksek olduğunda kart rengi otomatik olarak kırmızıya döner

## 🛠️ Kullanılan Teknolojiler

| Teknoloji | Amaç |
|-----------|------|
| [Python 3](https://www.python.org/) | Ana programlama dili |
| [discord.py](https://discordpy.readthedocs.io/) | Discord bot bağlantısı ve komutlar |
| [psutil](https://github.com/giampaolo/psutil) | Sistem bilgilerini okuma |

## 📁 Proje Yapısı

```
discord-sistem-botu/
├── bot.py        # Botun ana kodu
├── config.py     # Bot token'ı
├── .gitignore    # config.py'nin GitHub'a yüklenmesini engeller
├── LICENSE       # MIT lisans metni
└── README.md     # Bu dosya
```

## 🚀 Kurulum

### 1. Gereksinimleri yükleyin

Python 3.8 veya üzeri gereklidir.

```bash
pip install discord.py psutil
```

### 2. Discord botu oluşturun

1. [Discord Developer Portal](https://discord.com/developers/applications) üzerinden yeni bir uygulama oluşturun.
2. **Bot** sekmesinden token alın.
3. Aynı sekmede **Message Content Intent** seçeneğini açın.
4. **OAuth2 → URL Generator** bölümünde `bot` kapsamını seçip `Send Messages` ve `Embed Links` izinlerini verin. Oluşan bağlantıyla botu sunucunuza davet edin.

### 3. Token'ı yapılandırın

Proje klasörüne `config.py` dosyasını oluşturun:

```python
TOKEN = "botunuzun_tokeni"
```

### 4. Kanal ID'sini ayarlayın

Otomatik raporların gönderileceği kanalın ID'sini `bot.py` içindeki `KANAL_ID` değişkenine yazın:

```python
KANAL_ID = 123456789012345678
```

> 💡 Discord'da **Ayarlar → Gelişmiş → Geliştirici Modu** açıkken kanala sağ tıklayıp **ID'yi kopyala** seçeneğini kullanabilirsiniz.

### 5. Botu çalıştırın

```bash
python bot.py
```

Terminalde `Bot giriş yaptı: ...` mesajını görürseniz bot hazırdır.

## 💬 Kullanım

| Komut | Açıklama |
|-------|----------|
| `!durum` | Komutun yazıldığı kanala anlık sistem raporu gönderir |

Bot çalıştığı sürece her 10 dakikada bir `KANAL_ID` ile belirtilen kanala otomatik rapor göndermeye devam eder.

## 🔒 Güvenlik Notu

Bot token'ı bir şifre gibidir. Token'ı asla GitHub'a yüklemeyin ve kimseyle paylaşmayın. `config.py` dosyası `.gitignore` içinde listelendiği için depoya dahil edilmez. Token'ın açığa çıktığını düşünüyorsanız Discord Developer Portal üzerinden yenileyin.

## 📄 Lisans

Bu proje [MIT Lisansı](LICENSE) altında paylaşılmaktadır.
