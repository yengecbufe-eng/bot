# Gerekli kütüphaneleri içe aktarıyoruz
import platform  # İşletim sistemi bilgisini almak için
import datetime  # Zaman ölçümü ve damga (timestamp) için

import discord  # Discord bot kütüphanesi
import psutil  # CPU, RAM, disk, ağ ve işlem bilgilerini okumak için
from discord.ext import commands, tasks  # Komut ve zamanlanmış görev yardımcıları

# Bot token'ını config.py dosyasından alıyoruz
from config import TOKEN

# Otomatik raporun gönderileceği kanalın ID'si (0 ise otomatik rapor gönderilmez)
KANAL_ID = 0

# Discord'un botumuza hangi bilgileri göndereceğini belirleyen ayarlar (intents)
intents = discord.Intents.default()
intents.message_content = True  # "!durum" gibi mesaj içeriklerini okuyabilmek için gerekli

# "!" ile başlayan komutları dinleyen bot nesnesini oluşturuyoruz
bot = commands.Bot(command_prefix="!", intents=intents)

# Ağ hızını hesaplamak için ilk ağ ölçümünü ve zamanı kaydediyoruz
onceki_ag = psutil.net_io_counters()
onceki_zaman = datetime.datetime.now()


def calisma_suresi_metni() -> str:
    """Bilgisayarın son açılışından bu yana geçen süreyi 'X gün Y saat Z dakika' biçiminde döndürür."""
    # psutil.boot_time() bilgisayarın açılma zamanını Unix zaman damgası olarak verir
    acilis = datetime.datetime.fromtimestamp(psutil.boot_time())
    gecen = datetime.datetime.now() - acilis  # Açılıştan bu yana geçen süre

    gun = gecen.days  # Tam gün sayısı
    saat = gecen.seconds // 3600  # Günden artan saat kısmı
    dakika = (gecen.seconds % 3600) // 60  # Saatten artan dakika kısmı
    return f"{gun} gün {saat} saat {dakika} dakika"


def sistem_raporu_olustur() -> discord.Embed:
    """Altı sistem parametresini ölçüp Discord embed (kart) olarak döndürür."""
    global onceki_ag, onceki_zaman  # Fonksiyon içinde bu değişkenleri güncelleyeceğimiz için

    # 1) CPU kullanımını yüzde olarak alıyoruz. interval=1 ile 1 saniye boyunca ölçüm yapılır,
    # böylece değer anlık ve doğru kullanımı yansıtır
    cpu = psutil.cpu_percent(interval=1)

    # 2) RAM bilgisi: kullanım yüzdesi, kullanılan ve toplam bellek
    ram = psutil.virtual_memory()

    # 3) Disk bilgisi: Windows'ta C:\, diğer sistemlerde kök dizin (/) ölçülür
    disk_yolu = "C:\\" if platform.system() == "Windows" else "/"
    disk = psutil.disk_usage(disk_yolu)

    # 4) Ağ hızı: iki ölçüm arasındaki veri farkı geçen süreye bölünerek KB/s bulunur
    simdiki_ag = psutil.net_io_counters()  # Şu anki toplam gelen/giden bayt sayıları
    simdi = datetime.datetime.now()  # Şu anki zaman
    gecen_sure = (simdi - onceki_zaman).total_seconds() or 1  # 0'a bölmemek için "or 1"
    gelen_hiz = (simdiki_ag.bytes_recv - onceki_ag.bytes_recv) / gecen_sure / 1024
    giden_hiz = (simdiki_ag.bytes_sent - onceki_ag.bytes_sent) / gecen_sure / 1024

    # Bir sonraki ölçümde kullanmak üzere mevcut değerleri saklıyoruz
    onceki_ag = simdiki_ag
    onceki_zaman = simdi

    # 5) Çalışma süresi: bilgisayarın açık kaldığı süre
    calisma = calisma_suresi_metni()

    # 6) İşlem sayısı: o an çalışan toplam işlem (process) sayısı
    islem_sayisi = len(psutil.pids())

    # Kaynaklardan biri yüksekse kartın rengi kırmızı, değilse yeşil olur
    renk = discord.Color.green()
    if cpu > 80 or ram.percent > 80 or disk.percent > 90:
        renk = discord.Color.red()

    # Discord'da gösterilecek kartın (embed) başlık, açıklama ve rengini belirliyoruz
    embed = discord.Embed(
        title="🖥️ Sistem Durum Raporu",
        description=f"Makine: **{platform.node()}** ({platform.system()})",
        color=renk,
        timestamp=datetime.datetime.now(),  # Kartın altında gönderim zamanını gösterir
    )

    # Her parametreyi kartta ayrı bir alan (field) olarak ekliyoruz
    embed.add_field(name="🧠 CPU", value=f"%{cpu:.1f}", inline=True)
    embed.add_field(
        name="💾 RAM",
        value=f"%{ram.percent:.1f} ({ram.used // (1024**2)} / {ram.total // (1024**2)} MB)",
        inline=True,
    )
    embed.add_field(
        name="📀 Disk",
        value=f"%{disk.percent:.1f} ({disk.used // (1024**3)} / {disk.total // (1024**3)} GB)",
        inline=True,
    )
    embed.add_field(
        name="🌐 Ağ",
        value=f"⬇️ {gelen_hiz:.1f} KB/s\n⬆️ {giden_hiz:.1f} KB/s",
        inline=False,  # Ağ alanını bir alt satıra geçirir, tam genişlikte gösterir
    )
    embed.add_field(name="⏱️ Çalışma Süresi", value=calisma, inline=True)
    embed.add_field(name="⚙️ İşlem Sayısı", value=f"{islem_sayisi} işlem", inline=True)

    # Hazırlanan kartı geri döndürüyoruz
    return embed


@bot.event
async def on_ready():
    """Bot Discord'a bağlandığında bir kez çalışır ve otomatik raporu başlatır."""
    print(f"Bot giriş yaptı: {bot.user}")  # Terminalde bağlantının başarılı olduğunu gösterir

    # Otomatik rapor döngüsü zaten çalışıyorsa tekrar başlatmıyoruz
    if not otomatik_rapor.is_running():
        otomatik_rapor.start()


@bot.command(name="durum")
async def durum(ctx: commands.Context):
    """Kullanıcı '!durum' yazdığında anlık sistem raporunu komutun yazıldığı kanala gönderir."""
    await ctx.send(embed=sistem_raporu_olustur())


@tasks.loop(minutes=10)
async def otomatik_rapor():
    """Her 10 dakikada bir, KANAL_ID ile belirtilen kanala otomatik rapor gönderir."""
    kanal = bot.get_channel(KANAL_ID)  # Kanal ID'sine göre kanal nesnesini buluyoruz
    if kanal is not None:  # Kanal bulunamazsa (ID yanlışsa ya da 0 ise) hata vermeden atlıyoruz
        await kanal.send(embed=sistem_raporu_olustur())


# Dosya doğrudan "python main.py" ile çalıştırıldığında botu başlatıyoruz
if __name__ == "__main__":
    bot.run(TOKEN)
