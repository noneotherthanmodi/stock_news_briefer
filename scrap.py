import requests
import json
import os
from urllib.parse import urlparse
import asyncio
import aiohttp
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from config import GEMINI_API_KEY
import google.generativeai as genai

base_url = "https://www.bseindia.com"

async def download_pdf(pdf_url, local_filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(pdf_url) as response:
            with open(local_filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)
    return local_filename

def get_pdf_text(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as f:
        reader = PdfReader(f)
        for page in reader.pages:
            text += page.extract_text()
    return text

def get_split_text(text):
    text_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_text(text)
    return chunks

async def process_pdf(message, index):
    print(f"Processing PDF {index + 1}")
    print("Company Name: ", message["company_name"])
    print("pdf_link: ", message["pdf_link"])
    print("Title: ", message["title"])
    print("\n")

    full_pdf_link = base_url + message["pdf_link"]
    local_filename = f"downloaded_pdf_{index}.pdf"

    # Download PDF
    pdf_path = await download_pdf(full_pdf_link, local_filename)

    # Extract and split text
    pdf_text = get_pdf_text(pdf_path)
    pdf_split_text = get_split_text(pdf_text)
    pdf_split_text_string = ''.join(map(str, pdf_split_text))

    # Process with Gemini API
    model = genai.GenerativeModel('gemini-1.5-flash')
    prompt = f"How did the company perform according to the financial result from this content:\n{pdf_split_text_string}"
    response = model.generate_content(prompt)

    # Write response to file
    with open(f"pdf_text_{index}.txt", "w", encoding='utf-8') as f:
        f.write(response.text)

    print(f"Finished processing PDF {index + 1} via Gemini API")


async def main():
    response = requests.post("http://localhost:8080/corporate_announcements",json={"pages": 2})
    output = json.loads(response.text)
    print(output)

    # Configure Gemini API
    api_key = GEMINI_API_KEY
    os.environ["GOOGLE_API_KEY"] = api_key
    genai.configure(api_key=api_key)

    # Process PDFs in parallel
    tasks = [process_pdf(message, index) for index, message in enumerate(output["message"][:7])]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())