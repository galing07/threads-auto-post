from bs4 import BeautifulSoup
import aiohttp

async def getnews(url):
    """
    Mengambil isi artikel berita dari URL yang diberikan.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as inner_response:

            if inner_response.status == 200:
                inner_html = await inner_response.text()

                soup = BeautifulSoup(inner_html, 'html.parser')
                articles = soup.find_all('article')

                hasil_artikel = []

                for article in articles:
                    isi_artikel = article.text.strip()

                    # Menghapus teks iklan bawaan situs
                    hapus_teks = "我是廣告 請繼續往下閱讀"
                    isi_artikel = isi_artikel.replace(hapus_teks, "")

                    # Menghapus baris kosong
                    lines = isi_artikel.splitlines()
                    isi_artikel = '\n'.join(
                        line for line in lines if line.strip()
                    )

                    hasil_artikel.append(isi_artikel)

                return hasil_artikel

            else:
                print(f"Gagal mengambil halaman. Status kode: {inner_response.status}")
                return ["Gagal membaca berita"]


async def setn_fetch_url(url):
    """
    Mengambil URL berita terbaru dari halaman kategori SETN.
    """
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:

            if response.status == 200:
                html = await response.text()

                soup = BeautifulSoup(html, 'html.parser')

                title_block = soup.find('h3', class_='view-li-title')

                if title_block:
                    a_tag = title_block.find('a')

                    if a_tag:
                        href = a_tag['href']
                        return href

                return None

            else:
                print(f"Gagal memuat halaman: {response.status}")
                return None
