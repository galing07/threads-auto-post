from bs4 import BeautifulSoup
import aiohttp


async def getnews(url):
    """
    Mengambil isi artikel dari URL berita.
    Mengembalikan list berisi isi artikel.
    """

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=30) as response:

                if response.status != 200:
                    print(f"Gagal mengambil halaman. Status: {response.status}")
                    return ["Gagal membaca berita"]

                html = await response.text()

                soup = BeautifulSoup(html, "html.parser")

                articles = soup.find_all("article")

                hasil = []

                for article in articles:
                    teks = article.get_text(separator="\n").strip()

                    # Hapus teks iklan yang sering muncul
                    daftar_hapus = [
                        "我是廣告 請繼續往下閱讀",
                        "Advertisement",
                        "Iklan",
                        "Baca Juga",
                    ]

                    for item in daftar_hapus:
                        teks = teks.replace(item, "")

                    # Hapus baris kosong
                    lines = [
                        line.strip()
                        for line in teks.splitlines()
                        if line.strip()
                    ]

                    teks_bersih = "\n".join(lines)

                    if teks_bersih:
                        hasil.append(teks_bersih)

                # Jika tag article tidak ditemukan
                if not hasil:
                    body = soup.get_text(separator="\n")

                    lines = [
                        line.strip()
                        for line in body.splitlines()
                        if line.strip()
                    ]

                    teks_bersih = "\n".join(lines[:300])

                    return [teks_bersih]

                return hasil

    except Exception as e:
        print(f"Terjadi kesalahan saat membaca berita: {e}")
        return ["Gagal membaca berita"]


async def setn_fetch_url(url):
    """
    Mengambil URL berita terbaru dari halaman kategori SETN.
    """

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/137.0.0.0 Safari/537.36"
            )
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=30) as response:

                if response.status != 200:
                    print(f"Gagal memuat halaman: {response.status}")
                    return None

                html = await response.text()

                soup = BeautifulSoup(html, "html.parser")

                # Cari berita terbaru
                title_block = soup.find("h3", class_="view-li-title")

                if not title_block:
                    print("Judul berita tidak ditemukan.")
                    return None

                a_tag = title_block.find("a")

                if not a_tag:
                    print("Link berita tidak ditemukan.")
                    return None

                href = a_tag.get("href")

                if not href:
                    return None

                # Jika URL relatif
                if href.startswith("/"):
                    href = f"https://www.setn.com{href}"

                return href

    except Exception as e:
        print(f"Terjadi kesalahan saat mengambil URL berita: {e}")
        return None
