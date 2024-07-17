from config import GEMINI_API_KEY
import spacy 
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
import os
import google.generativeai as genai


def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        with open(pdf, 'rb') as f:
            reader = PdfReader(f)
            for page in reader.pages:
                text += page.extract_text()
    return text

pdf_paths = ["rj_report_4_sem.pdf"]

pdf_text = get_pdf_text(pdf_paths)


def get_split_text(text):
    text_splitter = CharacterTextSplitter(separator="\n",
                                          chunk_size = 1000,
                                          chunk_overlap=200,
                                          length_function = len)
    chunks = text_splitter.split_text(text)
    return chunks

pdf_split_text = get_split_text(pdf_text)

my_string = ''.join(map(str, pdf_split_text))


# with open("pdf_text.txt", "w",encoding='utf-8') as f:
#     f.write(my_string)






api_key = GEMINI_API_KEY
os.environ["GOOGLE_API_KEY"] = api_key

genai.configure(api_key=api_key)

model = genai.GenerativeModel('gemini-1.5-flash')

prompt = f"How did the company perform according to the financial result from this content :\n{my_string}"

response = model.generate_content(prompt)

print(response.text)



