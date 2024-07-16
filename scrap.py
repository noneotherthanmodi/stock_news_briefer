import requests
import json
import asyncio
import aiohttp
import os
from urllib.parse import urlparse
##
base_url = "https://www.bseindia.com"

response = requests.get("http://localhost:8080/corporate_announcements")
output = json.loads(response.text)

for index, message in enumerate(output["message"]):
    print("Company Name: ", message["company_name"])
    print("pdf_link: ", message["pdf_link"])
    print("Title: ", message["title"])
    print("\n")
    
    full_pdf_link = base_url + message["pdf_link"]
    
    parsed_url = urlparse(full_pdf_link)
    filename = os.path.basename(parsed_url.path)
    
    local_filename = f"downloaded_pdf_{index}.pdf"  
 
    async def download_pdf(pdf_url, local_filename):
        async with aiohttp.ClientSession() as session:
            async with session.get(pdf_url) as response:
                with open(local_filename, 'wb') as f:
                    while True:
                        chunk = await response.content.read(1024)
                        if not chunk:
                            break
                        f.write(chunk)
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(download_pdf(full_pdf_link, local_filename))

