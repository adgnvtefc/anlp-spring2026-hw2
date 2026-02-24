from bs4 import BeautifulSoup
import pdfplumber

def parse_html_to_text(html_content: str) -> str:
    """
    Parses raw HTML and extracts visible text while stripping out scripts and styles.
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Remove script and style elements
    for script_or_style in soup(["script", "style", "nav", "footer"]):
        script_or_style.extract()
        
    text = soup.get_text(separator=' ', strip=True)
    return text

def parse_pdf_to_text(pdf_path: str) -> str:
    """
    Extracts text from a local PDF file.
    Requires `pdfplumber` to be installed.
    """
    text_content = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            extracted = page.extract_text()
            if extracted:
                text_content.append(extracted)
    return "\n\n".join(text_content)
