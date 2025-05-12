import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import logging
from typing import Optional

def get_main_image_from_url(url: str) -> Optional[str]:
    """
    Extrai a URL da imagem principal de uma página web.
    
    Args:
        url: URL da página web
        
    Returns:
        URL da imagem principal ou None se não encontrar
    """
    try:
        # Adicionar user-agent para evitar bloqueios
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Fazer o request para a página
        response = requests.get(url, headers=headers, timeout=5)
        response.raise_for_status()
        
        # Usar BeautifulSoup para analisar o HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Estratégia 1: Buscar meta tags Open Graph (prioridade máxima)
        og_image = soup.find('meta', property='og:image')
        if og_image and og_image.get('content'):
            return og_image['content']
            
        # Estratégia 2: Buscar meta tags Twitter Card
        twitter_image = soup.find('meta', {'name': 'twitter:image'})
        if twitter_image and twitter_image.get('content'):
            return twitter_image['content']
            
        # Estratégia 3: Buscar link rel="image_src"
        image_src = soup.find('link', rel='image_src')
        if image_src and image_src.get('href'):
            return image_src['href']
            
        # Estratégia 4: Buscar imagens em artigos
        article = soup.find('article')
        if article:
            article_img = article.find('img')
            if article_img and article_img.get('src'):
                return urljoin(url, article_img['src'])
        
        # Estratégia 5: Procurar por classes comuns de imagens em destaque
        featured_selectors = ['.featured-image img', '.post-thumbnail img', '.entry-content img', 
                              'figure img', '.wp-post-image', '.attachment-large']
        
        for selector in featured_selectors:
            try:
                parts = selector.split()
                if len(parts) == 1:
                    # Caso seja apenas uma classe ou tag
                    element = soup.select_one(selector)
                else:
                    # Caso seja uma combinação (ex: '.class img')
                    element = soup.select_one(selector)
                
                if element:
                    if element.name == 'img' and element.get('src'):
                        return urljoin(url, element['src'])
                    elif element.get('src'):
                        return urljoin(url, element['src'])
            except Exception as e:
                logging.error(f"Erro ao buscar seletor {selector}: {str(e)}")
                continue
        
        # Estratégia 6: Encontrar a maior imagem na página
        images = soup.find_all('img')
        largest_image = None
        max_size = 0
        
        for img in images:
            # Ignorar ícones e imagens pequenas
            if img.get('width') and img.get('height'):
                try:
                    width = int(img['width'])
                    height = int(img['height'])
                    size = width * height
                    
                    # Ignorar imagens muito pequenas (provavelmente ícones)
                    if size > max_size and size > 10000 and width > 100 and height > 100:
                        max_size = size
                        largest_image = img
                except ValueError:
                    continue
            
            # Verificar se a URL da imagem contém pistas de ser a principal
            src = img.get('src', '')
            if src and any(term in src.lower() for term in ['hero', 'feature', 'main', 'large', 'cover']):
                return urljoin(url, src)
        
        # Se encontrou a maior imagem, retorna ela
        if largest_image and largest_image.get('src'):
            return urljoin(url, largest_image['src'])
            
        # Estratégia 7: Pegar a primeira imagem não-ícone da página
        for img in images:
            src = img.get('src', '')
            # Ignorar ícones comuns
            if src and not any(icon in src.lower() for icon in ['icon', 'logo', 'avatar', 'emoji', 'banner']):
                # Verificar dimensões, se disponíveis
                width = img.get('width')
                height = img.get('height')
                
                if width and height:
                    try:
                        if int(width) > 100 and int(height) > 100:
                            return urljoin(url, src)
                    except ValueError:
                        pass
                else:
                    # Se não tiver dimensões, considerar que é uma imagem válida
                    # mas apenas se o nome do arquivo parecer ser uma imagem de conteúdo
                    parsed = urlparse(src)
                    path = parsed.path.lower()
                    if path.endswith(('.jpg', '.jpeg', '.png', '.webp')) and not any(x in path for x in ['icon', 'logo']):
                        return urljoin(url, src)
        
        # Não encontrou nenhuma imagem válida
        return None
        
    except Exception as e:
        logging.error(f"Erro ao extrair imagem de {url}: {str(e)}")
        return None
