import platform
import datetime

import discord
import psutil
from discord.ext import commands, tasks

# Token, config.py dosyasından alınır
from config import TOKEN

# Otomatik raporun gönderileceği kanalın ID'si (0 ise otomatik rapor gönderilmez)
KANAL_ID = 0

# Mesaj içeriğini okuyabilmek için gerekli yetki (intent)
intents = discord.Intents.default()
intents.message_content = True

# "!" ile başlayan komutları dinleyen bot nesnesi
bot = commands.Bot(command_prefix="!", intents=intents)

# Ağ hızını hesaplamak için ilk ölçüm değerleri
onceki_ag = psutil.net_io_counters()
onceki_zaman = datetime.datetime.now()

# CPU ölçümünün ilk değeri her zaman 0 döner, bu yüzden bir kez önceden çağırıyoruz
psutil.cpu_percent(interval=None)


def sistem_raporu_olustur() -> discord.Embed:
    """CPU, RAM, disk ve ağ bilgilerini ölçüp Discord embed (kart) olarak döndürür."""
    global onceki_ag, onceki_zaman

    # 1) CPU kullanımı (yüzde). Son çağrıdan bu yana geçen süre üzerinden hesaplanır.
    cpu = psutil.cpu_percent(interval=None)

    # 2) RAM bilgisi (kullanım yüzdesi, kullanılan ve toplam bayt)
    ram = psutil.virtual_memory()

    # 3) Disk bilgisi. Windows'ta C:\, diğer sistemlerde kök dizin ("/") ölçülür.
    disk_yolu = "C:\\" if platform.system() == "Windows" else "/"
    disk = psutil.disk_usage(disk_yolu)

    # 4) Ağ hızı: iki ölçüm arasındaki veri farkı, geçen süreye bölünür (KB/s)
    simdiki_ag = psutil.net_io_counters()
    simdi = datetime.datetime.now()
    gecen_sure = (simdi - onceki_zaman).total_seconds() or 1  # Sıfıra bölmemek için
    gelen_hiz = (simdiki_ag.bytes_recv - onceki_ag.bytes_recv) / gecen_sure / 1024
    giden_hiz = (simdiki_ag.bytes_sent - onceki_ag.bytes_sent) / gecen_sure / 1024

    # Bir sonraki ölçüm için mevcut değerleri saklıyoruz
    onceki_ag = simdiki_ag
    onceki_zaman = simdi

    # Kaynaklardan biri yüksekse kart kırmızı, değilse yeşil olur
    renk = discord.Color.green()
    if cpu > 80 or ram.percent > 80 or disk.percent > 90:
        renk = discord.Color.red()

    # Discord'da gösterilecek kartın başlık ve açıklaması
    embed = discord.Embed(
        title="🖥️ Sistem Durum Raporu",
        description=f"Makine: **{platform.node()}** ({platform.system()})",
        color=renk,
        timestamp=datetime.datetime.now(),
    )
    # Her parametre kartta ayrı bir alan (field) olarak eklenir
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
        inline=False,
    )
    return embed


@bot.event
async def on_ready():
    """Bot Discord'a bağlanınca çalışır ve otomatik rapor döngüsünü başlatır."""
    print(f"Bot giriş yaptı: {bot.user}")
    # Döngü zaten çalışıyorsa tekrar başlatmıyoruz
    if not otomatik_rapor.is_running():
        otomatik_rapor.start()


@bot.command(name="durum")
async def durum(ctx: commands.Context):
    """'!durum' yazıldığında anlık sistem raporunu komutun yazıldığı kanala gönderir."""
    await ctx.send(embed=sistem_raporu_olustur())


@tasks.loop(minutes=10)
async def otomatik_rapor():
    """Her 10 dakikada bir, KANAL_ID ile belirtilen kanala rapor gönderir."""
    kanal = bot.get_channel(KANAL_ID)
    if kanal is not None:
        await kanal.send(embed=sistem_raporu_olustur())


if __name__ == "__main__":
    # Dosya doğrudan çalıştırıldığında botu başlatır
    bot.run(TOKEN)
