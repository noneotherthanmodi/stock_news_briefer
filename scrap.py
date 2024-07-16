import requests
import json
import os
from urllib.parse import urlparse
import asyncio
import aiohttp
from PyPDF2 import PdfReader

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

# Function to get text from PDFs
def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        with open(pdf, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    return text




# Example code to fetch corporate announcements and process PDFs
response = requests.get("http://localhost:8080/corporate_announcements")
output = json.loads(response.text)



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
all_text = get_pdf_text(downloaded_pdf_paths)
print(all_text)
