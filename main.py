import google.generativeai as genai
import asyncio
from metathreads import MetaThreads
from spider import getnews, setn_fetch_url
import random
import json
import re

data = json.load(open("config.json", encoding="utf-8"))

ACCOUNT = data["ACCOUNT"]
PASSWORD = data["PASSWORD"]
API_KEY = data["API_KEY"]
NEWS = data["NEWS"]
MODE = data["MODE"]

# Isi Prompt di sini
##########################
prompt = """
Halo
"""
##########################

while True:
    if MODE in ['setn', 'text', 'manual']:
        break

    MODE = input('Mode tidak dikenal. Mode harus "setn", "text", atau "manual"\nMasukkan mode: ')

print("Sedang login...")
threads = MetaThreads()
threads.login(ACCOUNT, PASSWORD)

genai.configure(api_key=API_KEY)

generation_config = {
    'temperature': 1,
    'top_p': 0.95,
    'top_k': 64,
    'max_output_tokens': 2048,
}

safety_settings = [
    {
        'category': 'HARM_CATEGORY_HARASSMENT',
        'threshold': 'block_none'
    },
    {
        'category': 'HARM_CATEGORY_HATE_SPEECH',
        'threshold': 'block_none'
    },
    {
        'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
        'threshold': 'block_none'
    },
    {
        'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
        'threshold': 'block_none'
    },
]

model = genai.GenerativeModel(
    model_name='gemini-1.0-pro',
    generation_config=generation_config,
    safety_settings=safety_settings
)

async def text_api(msg: str) -> str | None:
    """
    Memanggil API Gemini dan mengembalikan hasil respons.
    """
    convo = model.start_chat(history=[])

    if not msg:
        return 'Pesan kosong'

    await convo.send_message_async(msg)
    reply_text = convo.last.text
    return reply_text

async def text_auto_post():
    while True:
        reply_text = await text_api(prompt)
        print("\nHasil Generasi:\n" + reply_text)

        print("\nMengirim postingan...")
        threads.post_thread(thread_caption=reply_text)
        print("Postingan berhasil dikirim!")

        await asyncio.sleep(60 + random.randint(10, 60))

async def setn_auto_post(url):
    while True:
        news_url = await setn_fetch_url(url)

        try:
            with open('cache.txt', 'r') as file:
                cached_url = file.read().strip()
        except FileNotFoundError:
            with open('cache.txt', 'w') as file:
                file.write("")
            cached_url = ""

        if cached_url == f"https://www.setn.com{news_url}":
            print("URL sama, proses dilewati.")
        else:
            with open('cache.txt', 'w') as file:
                file.write(f"https://www.setn.com{news_url}")

            news = await getnews(f"https://www.setn.com{news_url}")
            print("\nIsi Berita:", news)

            reply_text = await text_api(prompt + " ".join(news))
            print("\nHasil Generasi:\n" + reply_text)

            print("\nMengirim postingan...")
            threads.post_thread(thread_caption=reply_text)
            print("Postingan berhasil dikirim!")

        await asyncio.sleep(60 + random.randint(10, 60))

async def manual():
    url = input("Masukkan URL berita atau topik: ")

    pattern = r'https://[^\s]+'

    if re.match(pattern, url):
        news = await getnews(url)
        print("\nIsi Berita:", news)

        reply_text = await text_api(prompt + " ".join(news))
        print("\nHasil Generasi:\n" + reply_text)
    else:
        reply_text = await text_api(prompt + url)
        print("\nHasil Generasi:\n" + reply_text)

    yes_or_no = input("\nApakah Anda ingin memposting tulisan ini? (y/n): ")

    if yes_or_no.lower() in ["yes", "y"]:
        if re.match(pattern, url):
            include_link = input("Sertakan link berita? (y/n): ")

            if include_link.lower() in ["yes", "y"]:
                print("Mengirim postingan...")
                threads.post_thread(
                    thread_caption=f"{reply_text}\n\n{url}"
                )
                print("Postingan berhasil dikirim!")
            else:
                print("Mengirim postingan...")
                threads.post_thread(
                    thread_caption=reply_text
                )
                print("Postingan berhasil dikirim!")
        else:
            print("Mengirim postingan...")
            threads.post_thread(
                thread_caption=reply_text
            )
            print("Postingan berhasil dikirim!")

        await manual()
    else:
        await manual()

if MODE == "setn":
    asyncio.run(setn_auto_post(NEWS))

if MODE == "text":
    asyncio.run(text_auto_post())

if MODE == "manual":
    asyncio.run(manual())
