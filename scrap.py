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

response = requests.get("http://localhost:8080/corporate_announcements")
output = json.loads(response.text)



## SEND EACH PDF TO THE GEMINI AS SOON AS IT IS DOWNLOADED, SO THAT IT CAN BE PROCESSED IN PARALLEL




async def download_pdf(pdf_url, local_filename):
    async with aiohttp.ClientSession() as session:
        async with session.get(pdf_url) as response:
            with open(local_filename, 'wb') as f:
                while True:
                    chunk = await response.content.read(1024)
                    if not chunk:
                        break
                    f.write(chunk)


# Function to get text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        with open(pdf, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    return text





#Function to split text into chunks
def get_split_text(text):
    text_splitter = CharacterTextSplitter(separator="\n",
                                          chunk_size = 1000,
                                          chunk_overlap=200,
                                          length_function = len)
    chunks = text_splitter.split_text(text)
    return chunks









# List to store downloaded PDF paths
downloaded_pdf_paths = []

# Download PDFs asynchronously
for index, message in enumerate(output["message"]):
    print("Company Name: ", message["company_name"])
    print("pdf_link: ", message["pdf_link"])
    print("Title: ", message["title"])
    print("\n")
    
    
    full_pdf_link = base_url + message["pdf_link"]
    parsed_url = urlparse(full_pdf_link)
    filename = os.path.basename(parsed_url.path)
    
    local_filename = f"downloaded_pdf_{index}.pdf"

    # Download PDF asynchronously
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_pdf(full_pdf_link, local_filename))

    # Store downloaded PDF path
    downloaded_pdf_paths.append(local_filename)
    


# Extract text from downloaded PDFs
pdf_paths = downloaded_pdf_paths
pdf_text = get_pdf_text(pdf_paths)



pdf_split_text = get_split_text(pdf_text)
pdf_split_text_string = ''.join(map(str, pdf_split_text))



api_key = GEMINI_API_KEY
os.environ["GOOGLE_API_KEY"] = api_key

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"How did the company perform according to the financial result from this content :\n{pdf_split_text_string}"

response = model.generate_content(prompt)

with open("pdf_text.txt", "w",encoding='utf-8') as f:
    f.write(response.text)

