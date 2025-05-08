import requests
from bs4 import BeautifulSoup

def get_text_news(url: str) -> str:
    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Encontra o conteúdo principal
        article = soup.find("article") or soup.find("div", class_="article") or soup.find("main") or soup.find("div", class_="content") or soup.find("div", class_="article-content")
        
        if article:
            # Remove elementos indesejados
            for tag in article.find_all(["script", "style", "iframe", "button"]):
                tag.decompose()
            
            # Extrai o texto
            content = article.get_text(separator="\n", strip=True)
            return content
        else:
            # Fallback: usa o body se não encontrar artigo específico
            body_text = soup.body.get_text(separator="\n", strip=True)
            # Limita o tamanho para evitar exceder o limite de tokens
            return body_text[:5000]
            
    except Exception as e:
        return f"Erro ao processar a notícia: {str(e)}"