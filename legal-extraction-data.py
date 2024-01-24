import requests
from bs4 import BeautifulSoup
import pandas as pd
import fitz  # PyMuPDF
import re
import json

class CaseDataExtractor:
    def __init__(self, number_of_case_document):
        self.number_of_case_document = number_of_case_document
        self.df = pd.DataFrame(columns=['frontend_pdf_url', 'reporter', 'provenance', 'court', 'jurisdiction',
                                        'citations', 'url', 'name', 'cites_to', 'name_abbreviation', 'extracted_text'])

    def extract_text_from_pdf(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Check for any HTTP errors
            pdf_content = response.content

            # Using PyMuPDF to extract text from PDF
            pdf_document = fitz.open(stream=pdf_content, filetype='pdf')
            text = ""
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()

            return text
        except Exception as e:
            print(f"Error extracting text from {url}: {str(e)}")
            return None

    def preprocess_text(self, text):
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def fetch_case_data(self):
        topic_page_url = f"https://api.case.law/v1/cases/?jurisdiction=ill&page_size={self.number_of_case_document}"
        response = requests.get(topic_page_url)
        topic_doc = BeautifulSoup(response.text, 'html.parser')
        data = json.loads(str(topic_doc))

        for item in data['results']:
            extracted_text = self.extract_text_from_pdf(item['frontend_pdf_url'])
            extracted_text = self.preprocess_text(extracted_text)

            self.df.loc[len(self.df)] = [
                item['frontend_pdf_url'], item['reporter'], item['provenance'], item['court'],
                item['jurisdiction'], item['citations'], item['url'], item['name'],
                item['cites_to'], item['name_abbreviation'], extracted_text
            ]

        return self.df

    def save_to_csv(self, filename='case_data.csv'):
        self.df.to_csv(filename, index=False)
        print(f"DataFrame has been saved to {filename}")


# Example usage:
number_of_case_document = 5  # Replace with your desired number
case_data_extractor = CaseDataExtractor(number_of_case_document)
result_df = case_data_extractor.fetch_case_data()

# Save the DataFrame to CSV
case_data_extractor.save_to_csv()
