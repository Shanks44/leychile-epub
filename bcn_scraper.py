import requests
from xml.etree import ElementTree as ET
import re
from urllib.parse import urlparse, parse_qs
from typing import Dict, List, Optional
import html


class BCNLawScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'application/xml, text/xml, */*',
        })
        self.ns = {'lc': 'http://www.leychile.cl/esquemas'}

    def extract_id_norma(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('idNorma', [None])[0]

    def extract_id_version(self, url: str) -> Optional[str]:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        return params.get('idVersion', [None])[0]

    def get_api_url(self, id_norma: str) -> str:
        return f"https://www.leychile.cl/Consulta/obtxml?opt=7&idNorma={id_norma}"

    def fetch_xml(self, url: str) -> Optional[ET.Element]:
        try:
            response = self.session.get(url, timeout=60)
            response.raise_for_status()
            return ET.fromstring(response.content)
        except Exception as e:
            print(f"Error fetching XML: {e}")
            return None

    def get_text(self, element: ET.Element, path: str) -> str:
        elem = element.find(path, self.ns)
        if elem is not None and elem.text:
            return html.unescape(elem.text.strip())
        return ''

    def get_all_text(self, element: ET.Element, path: str) -> List[str]:
        elements = element.findall(path, self.ns)
        return [html.unescape(e.text.strip()) for e in elements if e.text]

    def scrape_full_law(self, url: str, progress_callback=None) -> Dict:
        id_norma = self.extract_id_norma(url)
        id_version = self.extract_id_version(url)
        
        if not id_norma:
            raise ValueError("No se pudo extraer el ID de la norma de la URL proporcionada")
        
        if progress_callback:
            progress_callback(0.1, "Conectando con la API de Ley Chile...")
        
        api_url = self.get_api_url(id_norma)
        root = self.fetch_xml(api_url)
        
        if root is None:
            raise Exception("No se pudo acceder a la API de Ley Chile")
        
        if progress_callback:
            progress_callback(0.3, "Extrayendo metadatos...")
        
        metadata = self._extract_metadata(root)
        
        if progress_callback:
            progress_callback(0.5, "Extrayendo contenido de la ley...")
        
        content = self._extract_content(root, progress_callback)
        
        if progress_callback:
            progress_callback(0.9, "Procesamiento completado")
        
        return {
            'metadata': metadata,
            'content': content,
            'url': url,
            'id_norma': id_norma,
            'id_version': id_version
        }

    def _extract_metadata(self, root: ET.Element) -> Dict[str, str]:
        metadata = {
            'title': '',
            'type': '',
            'number': '',
            'organism': '',
            'subjects': [],
            'common_name': '',
            'source': '',
            'promulgation_text': '',
            'derogation_dates': []
        }
        
        metadata['title'] = self.get_text(root, './/lc:TituloNorma')
        metadata['type'] = self.get_text(root, './/lc:TipoNumero/lc:Tipo')
        metadata['number'] = self.get_text(root, './/lc:TipoNumero/lc:Numero')
        metadata['organism'] = self.get_text(root, './/lc:Organismo')
        metadata['subjects'] = self.get_all_text(root, './/lc:Materia')
        metadata['common_name'] = self.get_text(root, './/lc:NombreUsoComun')
        metadata['source'] = self.get_text(root, './/lc:IdentificacionFuente')
        
        prom = root.find('.//lc:Promulgacion', self.ns)
        if prom is not None:
            texto = prom.find('lc:Texto', self.ns)
            if texto is not None:
                metadata['promulgation_text'] = self._get_all_text_content(prom)
        
        derog_dates = set()
        for elem in root.iter():
            tag = elem.tag.replace('{http://www.leychile.cl/esquemas}', '')
            if tag == 'FechaDerogacion' and elem.text:
                derog_dates.add(elem.text.strip())
        metadata['derogation_dates'] = sorted(list(derog_dates))
        
        if not metadata['title']:
            metadata['title'] = f"{metadata['type']} {metadata['number']}"
        
        return metadata

    def _extract_content(self, root: ET.Element, progress_callback=None) -> List[Dict]:
        content = []
        
        encabezado = root.find('.//lc:Encabezado', self.ns)
        if encabezado is not None:
            enc_text = self._extract_element_text(encabezado)
            if enc_text:
                content.append({
                    'type': 'encabezado',
                    'level': 0,
                    'text': enc_text
                })
        
        estructuras = root.findall('.//lc:EstructuraFuncional', self.ns)
        
        current_titulo = None
        current_parrafo = None
        total = len(estructuras)
        
        for i, ef in enumerate(estructuras):
            texto = self._extract_element_text(ef)
            if not texto:
                continue
            
            texto = texto.strip()
            
            element_type = self._classify_text(texto)
            
            if element_type == 'titulo':
                current_titulo = texto
                current_parrafo = None
                content.append({
                    'type': 'titulo',
                    'level': 1,
                    'text': texto,
                    'parent': None
                })
            
            elif element_type == 'parrafo':
                current_parrafo = texto
                content.append({
                    'type': 'parrafo',
                    'level': 2,
                    'text': texto,
                    'parent': current_titulo
                })
            
            elif element_type == 'articulo':
                article_match = re.match(
                    r'^(Art[íi]culo\s+\d+[°º]?(?:\s*(?:bis|ter|qu[aá]ter|quinquies|sexies|septies|octies|nonies|decies))?)[.\s:\-]*(.*)$',
                    texto,
                    re.IGNORECASE | re.DOTALL
                )
                
                if article_match:
                    article_title = article_match.group(1).strip()
                    article_text = article_match.group(2).strip()
                else:
                    article_title = texto[:50]
                    article_text = texto
                
                content.append({
                    'type': 'articulo',
                    'level': 3,
                    'title': article_title,
                    'text': article_text,
                    'parent_titulo': current_titulo,
                    'parent_parrafo': current_parrafo
                })
            
            else:
                if content and content[-1]['type'] == 'articulo':
                    content[-1]['text'] += '\n\n' + texto
                else:
                    content.append({
                        'type': 'texto',
                        'level': 4,
                        'text': texto
                    })
            
            if progress_callback and i % 50 == 0:
                progress = 0.5 + (i / total) * 0.35
                progress_callback(progress, f"Procesando elemento {i+1} de {total}...")
        
        if progress_callback:
            progress_callback(0.85, f"Extraídos {len(content)} elementos...")
        
        return content

    def _extract_element_text(self, element: ET.Element) -> str:
        texto_elem = element.find('lc:Texto', self.ns)
        if texto_elem is not None:
            return self._get_all_text_content(texto_elem)
        
        return self._get_all_text_content(element)

    def _get_all_text_content(self, element: ET.Element) -> str:
        parts = []
        
        if element.text:
            parts.append(element.text)
        
        for child in element:
            child_text = self._get_all_text_content(child)
            if child_text:
                parts.append(child_text)
            if child.tail:
                parts.append(child.tail)
        
        text = ''.join(parts)
        text = re.sub(r'\s+', ' ', text)
        text = html.unescape(text)
        
        return text.strip()

    def _classify_text(self, text: str) -> str:
        text_clean = text.strip()
        
        if re.match(r'^T[ÍI]TULO\s+[IVXLCDM]+', text_clean, re.IGNORECASE):
            return 'titulo'
        
        if re.match(r'^P[ÁA]RRAFO\s+\d', text_clean, re.IGNORECASE):
            return 'parrafo'
        
        if re.match(r'^Art[íi]culo\s+\d', text_clean, re.IGNORECASE):
            return 'articulo'
        
        if re.match(r'^CAP[ÍI]TULO\s+[IVXLCDM]+', text_clean, re.IGNORECASE):
            return 'titulo'
        
        if re.match(r'^LIBRO\s+[IVXLCDM]+', text_clean, re.IGNORECASE):
            return 'titulo'
        
        return 'texto'


def scrape_bcn_law(url: str, progress_callback=None) -> Dict:
    scraper = BCNLawScraper()
    return scraper.scrape_full_law(url, progress_callback)
