from bs4 import BeautifulSoup
import pdfplumber

def parse_html_to_text(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "form", "iframe", "noscript", "sup"]):
        element.extract()
    
    for element in soup.find_all(class_=["mw-editsection", "reference", "noprint", "infobox"]):
        element.extract()
        
    text = soup.get_text(separator=' ', strip=True)
    return text

def parse_pdf_to_text(pdf_path: str) -> str:
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
    return "\n\n".join(text_content)
