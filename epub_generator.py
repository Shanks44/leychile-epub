from ebooklib import epub
from typing import Dict, List, Optional, Tuple
import re
from datetime import datetime
import uuid


class LawEpubGenerator:
    """Premium ePub generator with world-class design standards for Chilean legal documents."""
    
    CHILEAN_BLUE = '#0b3d91'
    CHILEAN_RED = '#de1f2a'
    ACCENT_GOLD = '#c9a227'
    
    FONT_SIZES = {
        'small': {'base': '0.9em', 'h1': '1.758em', 'h2': '1.406em', 'h3': '1.125em'},
        'medium': {'base': '1em', 'h1': '1.953em', 'h2': '1.563em', 'h3': '1.25em'},
        'large': {'base': '1.1em', 'h1': '2.148em', 'h2': '1.719em', 'h3': '1.375em'},
        'extra-large': {'base': '1.2em', 'h1': '2.344em', 'h2': '1.875em', 'h3': '1.5em'}
    }
    
    def __init__(self, customization: Dict = None):
        self.book = None
        self.chapters = []
        self.toc = []
        self.toc_sections = []
        self.article_ids = {}
        self.article_list = []
        self.keyword_index = {}
        
        self.font_size = 'medium'
        self.line_spacing = 1.5
        self.margin = '1.2em'
        
    def create_epub(self, law_data: Dict, output_path: str = None) -> str:
        self.book = epub.EpubBook()
        self.chapters = []
        self.toc = []
        self.toc_sections = []
        self.article_ids = {}
        self.article_list = []
        self.keyword_index = {}
        
        metadata = law_data.get('metadata', {})
        content = law_data.get('content', [])
        
        self._build_article_index(content)
        self._build_keyword_index(content, metadata)
        
        self._set_enhanced_metadata(metadata, law_data)
        
        self._add_premium_css()
        
        self._create_premium_cover(metadata, law_data)
        
        self._create_legal_info_page(metadata, law_data)
        
        self._create_chapters(content, metadata)
        
        self._create_article_index_page()
        
        self._create_keyword_index_page()
        
        self._create_promulgation_appendix(metadata)
        
        self._build_enhanced_toc()
        
        self._set_spine()
        
        if not output_path:
            law_type = metadata.get('type', 'Ley')
            law_number = metadata.get('number', 'Unknown')
            output_path = f"{law_type}_{law_number}.epub"
        
        epub.write_epub(output_path, self.book, {})
        
        return output_path

    def _build_article_index(self, content: List[Dict]):
        article_count = 0
        current_chapter = 0
        current_titulo = None
        current_parrafo = None
        
        for item in content:
            if item.get('type') == 'titulo':
                current_chapter += 1
                current_titulo = item.get('text', '')
                current_parrafo = None
            elif item.get('type') == 'parrafo':
                current_parrafo = item.get('text', '')
            elif item.get('type') == 'articulo':
                article_title = item.get('title', '')
                match = re.search(
                    r'Art[íi]culo\s+(\d+(?:\s*(?:bis|ter|qu[aá]ter|quinquies|sexies|septies|octies|nonies|decies))?)', 
                    article_title, re.IGNORECASE
                )
                if match:
                    art_num = match.group(1).lower().replace(' ', '')
                    if current_chapter > 0:
                        file_ref = f'titulo_{current_chapter}.xhtml#art_{art_num}'
                    else:
                        file_ref = f'intro.xhtml#art_{art_num}'
                    
                    self.article_ids[art_num] = file_ref
                    self.article_list.append({
                        'number': art_num,
                        'title': article_title,
                        'file_ref': file_ref,
                        'parent_titulo': current_titulo,
                        'parent_parrafo': current_parrafo
                    })

    def _build_keyword_index(self, content: List[Dict], metadata: Dict):
        """Extract and index important legal keywords from the content."""
        legal_keywords = [
            'plazo', 'sancion', 'multa', 'pena', 'prohibicion', 'obligacion',
            'derecho', 'deber', 'facultad', 'competencia', 'jurisdiccion',
            'recurso', 'apelacion', 'nulidad', 'prescripcion', 'caducidad',
            'contrato', 'convenio', 'acuerdo', 'resolucion', 'decreto',
            'votacion', 'eleccion', 'escrutinio', 'sufragio', 'candidatura',
            'mesa', 'vocal', 'presidente', 'secretario', 'ministro',
            'tribunal', 'juez', 'fiscal', 'abogado', 'notario',
            'registro', 'inscripcion', 'certificado', 'documento',
            'patrimonio', 'propiedad', 'dominio', 'posesion', 'usufructo',
            'herencia', 'testamento', 'sucesion', 'donacion',
            'delito', 'falta', 'infraccion', 'crimen', 'cuasidelito'
        ]
        
        current_chapter = 0
        
        for item in content:
            if item.get('type') == 'titulo':
                current_chapter += 1
            elif item.get('type') == 'articulo':
                article_title = item.get('title', '')
                article_text = item.get('text', '').lower()
                
                art_match = re.search(r'Art[íi]culo\s+(\d+(?:\s*(?:bis|ter))?)', article_title, re.IGNORECASE)
                if not art_match:
                    continue
                    
                art_num = art_match.group(1).lower().replace(' ', '')
                if current_chapter > 0:
                    file_ref = f'titulo_{current_chapter}.xhtml#art_{art_num}'
                else:
                    file_ref = f'intro.xhtml#art_{art_num}'
                
                for keyword in legal_keywords:
                    if keyword in article_text:
                        if keyword not in self.keyword_index:
                            self.keyword_index[keyword] = []
                        if file_ref not in [x['ref'] for x in self.keyword_index[keyword]]:
                            self.keyword_index[keyword].append({
                                'ref': file_ref,
                                'art': art_num
                            })
        
        subjects = metadata.get('subjects', [])
        for subject in subjects:
            subject_lower = subject.lower()
            for word in subject_lower.split():
                if len(word) > 4 and word not in self.keyword_index:
                    self.keyword_index[word] = []

    def _create_keyword_index_page(self):
        """Create a professional keyword index page."""
        if not self.keyword_index:
            return
        
        sorted_keywords = sorted(
            [(k, v) for k, v in self.keyword_index.items() if v],
            key=lambda x: x[0]
        )
        
        if not sorted_keywords:
            return
        
        chapter = epub.EpubHtml(
            title='Indice de Materias',
            file_name='keyword_index.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        current_letter = ''
        sections_html = []
        
        for keyword, refs in sorted_keywords:
            first_letter = keyword[0].upper()
            if first_letter != current_letter:
                if current_letter:
                    sections_html.append('</div>')
                current_letter = first_letter
                sections_html.append(f'<div class="keyword-section"><h3 class="keyword-letter">{current_letter}</h3>')
            
            refs_html = ', '.join([f'<a href="{r["ref"]}">Art. {r["art"]}</a>' for r in refs[:8]])
            sections_html.append(f'<p class="keyword-entry"><strong>{keyword.capitalize()}</strong>: {refs_html}</p>')
        
        if sections_html:
            sections_html.append('</div>')
        
        body_content = f'''
<div class="keyword-index">
    <h1 class="no-break">Indice de Materias</h1>
    <p class="index-intro">Referencias a los principales conceptos juridicos contenidos en esta norma.</p>
    {''.join(sections_html)}
</div>
'''
        chapter.set_content(body_content)
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(chapter)

    def _set_enhanced_metadata(self, metadata: Dict, law_data: Dict):
        title = metadata.get('title', 'Ley Chile')
        law_type = metadata.get('type', 'Ley')
        law_number = metadata.get('number', '')
        
        full_title = f"{law_type} N° {law_number} - {title}" if law_number else title
        
        self.book.set_identifier(f'bcn-chile-{uuid.uuid4().hex[:8]}')
        self.book.set_title(full_title)
        self.book.set_language('es')
        
        self.book.add_author('Biblioteca del Congreso Nacional de Chile')
        
        organism = metadata.get('organism', '')
        if organism:
            self.book.add_metadata('DC', 'contributor', organism)
        
        self.book.add_metadata('DC', 'publisher', 'Biblioteca del Congreso Nacional de Chile')
        self.book.add_metadata('DC', 'source', law_data.get('url', ''))
        self.book.add_metadata('DC', 'date', datetime.now().strftime('%Y-%m-%d'))
        self.book.add_metadata('DC', 'rights', 'Documento publico - Republica de Chile')
        self.book.add_metadata('DC', 'type', 'Legislacion')
        self.book.add_metadata('DC', 'format', 'application/epub+zip')
        
        description = f"{law_type} {law_number}: {title}. Texto oficial de la Republica de Chile."
        self.book.add_metadata('DC', 'description', description)
        
        subjects = metadata.get('subjects', [])
        unique_subjects = list(dict.fromkeys(subjects))[:5]
        for subject in unique_subjects:
            self.book.add_metadata('DC', 'subject', subject)
        
        self.book.add_metadata('DC', 'subject', 'Legislacion chilena')
        self.book.add_metadata('DC', 'subject', 'Derecho')

    def _add_premium_css(self):
        sizes = self.FONT_SIZES.get(self.font_size, self.FONT_SIZES['medium'])
        
        bg_color = '#ffffff'
        text_color = '#1a1a1a'
        
        css_content = f'''
@charset "UTF-8";

/* ==========================================================================
   PREMIUM LEGAL DOCUMENT STYLESHEET
   Chilean Law ePub Generator - Professional Edition
   ========================================================================== */

/* --------------------------------------------------------------------------
   1. ROOT VARIABLES & BASE TYPOGRAPHY
   -------------------------------------------------------------------------- */

:root {{
    --primary-color: {self.CHILEAN_BLUE};
    --accent-color: {self.CHILEAN_RED};
    --gold-accent: {self.ACCENT_GOLD};
    --text-color: {text_color};
    --bg-color: {bg_color};
    --border-color: #e5e5e5;
    --muted-color: #6b7280;
    --highlight-bg: #f8f9fa;
}}

/* Modular Scale: 1.25 (Major Third) */
body {{
    font-family: "Palatino Linotype", Palatino, "Book Antiqua", Georgia, "Times New Roman", serif;
    font-size: {sizes['base']};
    line-height: {self.line_spacing};
    color: var(--text-color);
    background-color: var(--bg-color);
    margin: {self.margin};
    padding: 0;
    text-align: justify;
    text-justify: inter-word;
    hyphens: auto;
    -webkit-hyphens: auto;
    -moz-hyphens: auto;
    orphans: 3;
    widows: 3;
    word-spacing: 0.05em;
    letter-spacing: 0.01em;
}}

/* --------------------------------------------------------------------------
   2. HEADINGS - Typographic Hierarchy
   -------------------------------------------------------------------------- */

h1, h2, h3, h4, h5, h6 {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-weight: 600;
    line-height: 1.25;
    margin-top: 1.5em;
    margin-bottom: 0.75em;
    orphans: 4;
    widows: 4;
    page-break-after: avoid;
    -webkit-column-break-after: avoid;
    hyphens: none;
    -webkit-hyphens: none;
    -moz-hyphens: none;
    word-break: normal;
    overflow-wrap: normal;
}}

h1 {{
    font-size: {sizes['h1']};
    color: var(--primary-color);
    text-align: center;
    margin: 1.5em 0 1em 0;
    padding-bottom: 0.5em;
    border-bottom: 3px solid var(--primary-color);
    letter-spacing: 0.02em;
    text-transform: uppercase;
    page-break-before: always;
}}

h1.no-break {{
    page-break-before: auto;
}}

h2 {{
    font-size: 1.25em;
    color: var(--primary-color);
    margin: 1.5em 0 0.75em 0;
    padding-left: 0.75em;
    border-left: 4px solid var(--accent-color);
    background: linear-gradient(90deg, rgba(11,61,145,0.05) 0%, transparent 100%);
    padding: 0.5em 0.5em 0.5em 0.75em;
    page-break-inside: avoid;
    page-break-after: avoid;
    hyphens: none;
    -webkit-hyphens: none;
    -moz-hyphens: none;
}}

h3 {{
    font-size: {sizes['h3']};
    color: #2d3748;
    margin: 1.25em 0 0.5em 0;
    font-weight: 700;
}}

h4 {{
    font-size: 1.05em;
    color: #4a5568;
    font-weight: 600;
    margin: 1em 0 0.4em 0;
}}

/* --------------------------------------------------------------------------
   3. PARAGRAPHS & TEXT ELEMENTS
   -------------------------------------------------------------------------- */

p {{
    margin: 0.6em 0;
    text-indent: 1.5em;
}}

p.no-indent, 
p:first-of-type {{
    text-indent: 0;
}}

blockquote {{
    margin: 1.5em 2em;
    padding: 1em 1.5em;
    border-left: 4px solid var(--gold-accent);
    background-color: var(--highlight-bg);
    font-style: italic;
    color: var(--muted-color);
}}

/* --------------------------------------------------------------------------
   4. LEGAL DOCUMENT SPECIFIC STYLES
   -------------------------------------------------------------------------- */

/* Article Titles */
.articulo-titulo {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 1.05em;
    font-weight: 700;
    color: var(--primary-color);
    margin: 1.5em 0 0.5em 0;
    padding: 0.4em 0;
    border-bottom: 1px solid var(--border-color);
    page-break-after: avoid;
    page-break-inside: avoid;
    hyphens: none;
    -webkit-hyphens: none;
}}

.articulo-titulo a {{
    color: inherit;
    text-decoration: none;
}}

/* Article Content Container */
.articulo-contenido {{
    margin: 0.5em 0 1.5em 0;
    padding-left: 0;
}}

/* Incisos (numbered paragraphs within articles) */
.inciso {{
    margin: 0.4em 0 0.4em 2em;
    text-indent: 0;
    position: relative;
}}

.inciso::before {{
    content: "";
    position: absolute;
    left: -1em;
    top: 0.5em;
    width: 4px;
    height: 4px;
    background-color: var(--muted-color);
    border-radius: 50%;
}}

/* Letras (alphabetical sub-items) */
.letra {{
    margin: 0.3em 0 0.3em 3.5em;
    text-indent: 0;
    font-size: 0.95em;
}}

/* Numbered lists for legal structure */
ol.legal-list {{
    counter-reset: legal-counter;
    list-style: none;
    padding-left: 2em;
    margin: 0.5em 0;
}}

ol.legal-list li {{
    counter-increment: legal-counter;
    margin: 0.4em 0;
    position: relative;
}}

ol.legal-list li::before {{
    content: counter(legal-counter) ".";
    position: absolute;
    left: -2em;
    font-weight: 600;
    color: var(--primary-color);
}}

ol.legal-list.alpha {{
    counter-reset: alpha-counter;
}}

ol.legal-list.alpha li::before {{
    content: counter(alpha-counter, lower-alpha) ")";
    counter-increment: alpha-counter;
}}

/* Derogated article styling */
.derogado {{
    color: var(--muted-color);
    font-style: italic;
    text-decoration: line-through;
    opacity: 0.7;
}}

.derogado-notice {{
    display: inline-block;
    background-color: var(--accent-color);
    color: white;
    font-size: 0.75em;
    padding: 0.15em 0.5em;
    border-radius: 3px;
    margin-left: 0.5em;
    text-decoration: none;
    font-style: normal;
}}

/* --------------------------------------------------------------------------
   5. COVER PAGE STYLES
   -------------------------------------------------------------------------- */

.cover {{
    text-align: center;
    padding: 2em 1em;
    min-height: 90vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
}}

.cover-header {{
    margin-bottom: 2em;
}}

.cover-escudo {{
    font-size: 3em;
    color: var(--primary-color);
    margin-bottom: 0.5em;
}}

.cover-republica {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 0.9em;
    text-transform: uppercase;
    letter-spacing: 0.3em;
    color: var(--muted-color);
    margin-bottom: 0.5em;
}}

.cover-law-type {{
    font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 2.5em;
    font-weight: 700;
    color: var(--primary-color);
    margin: 0.5em 0;
    letter-spacing: 0.05em;
}}

.cover-law-number {{
    font-size: 3em;
    font-weight: 800;
    color: var(--accent-color);
    margin: 0.2em 0;
}}

.cover h1 {{
    font-size: 1.4em;
    color: var(--text-color);
    border: none;
    text-transform: none;
    margin: 1em 0;
    padding: 0;
    line-height: 1.4;
    page-break-before: auto;
}}

.cover-divider {{
    width: 60%;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--gold-accent), transparent);
    margin: 1.5em auto;
}}

.cover-organism {{
    font-size: 1em;
    color: var(--muted-color);
    font-style: italic;
    margin: 1em 0;
}}

.cover-subjects {{
    font-size: 0.85em;
    color: var(--primary-color);
    margin: 1em 0;
    padding: 0.75em 1.5em;
    background-color: var(--highlight-bg);
    border-radius: 4px;
    display: inline-block;
}}

.cover-metadata {{
    margin-top: 2em;
    padding: 1.5em;
    background-color: var(--highlight-bg);
    border: 1px solid var(--border-color);
    border-radius: 6px;
    max-width: 80%;
}}

.cover-source {{
    font-size: 0.8em;
    color: var(--muted-color);
    margin: 0.5em 0;
}}

.cover-footer {{
    margin-top: auto;
    padding-top: 2em;
    font-size: 0.75em;
    color: var(--muted-color);
}}

/* --------------------------------------------------------------------------
   6. LEGAL INFO PAGE STYLES
   -------------------------------------------------------------------------- */

.legal-info {{
    padding: 1em;
}}

.legal-info h1 {{
    page-break-before: auto;
}}

.info-section {{
    margin: 1.5em 0;
    padding: 1em;
    background-color: var(--highlight-bg);
    border-radius: 6px;
    border-left: 4px solid var(--primary-color);
}}

.info-section h3 {{
    margin-top: 0;
    color: var(--primary-color);
}}

.info-table {{
    width: 100%;
    border-collapse: collapse;
    margin: 1em 0;
}}

.info-table td {{
    padding: 0.5em;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
}}

.info-table td:first-child {{
    font-weight: 600;
    width: 35%;
    color: var(--primary-color);
}}

.timeline {{
    margin: 1em 0;
    padding-left: 1.5em;
    border-left: 2px solid var(--primary-color);
}}

.timeline-item {{
    margin: 1em 0;
    padding-left: 1em;
    position: relative;
}}

.timeline-item::before {{
    content: "";
    position: absolute;
    left: -1.65em;
    top: 0.4em;
    width: 10px;
    height: 10px;
    background-color: var(--accent-color);
    border-radius: 50%;
    border: 2px solid white;
}}

.timeline-date {{
    font-weight: 600;
    color: var(--primary-color);
}}

/* --------------------------------------------------------------------------
   7. ARTICLE INDEX STYLES
   -------------------------------------------------------------------------- */

.article-index {{
    padding: 1em;
}}

.article-index h1 {{
    page-break-before: auto;
}}

.index-section {{
    margin: 1.5em 0;
}}

.index-section h3 {{
    color: var(--primary-color);
    border-bottom: 2px solid var(--border-color);
    padding-bottom: 0.3em;
}}

.index-list {{
    list-style: none;
    padding: 0;
    margin: 0;
    column-count: 2;
    column-gap: 2em;
}}

.index-list li {{
    margin: 0.3em 0;
    padding: 0.2em 0;
    break-inside: avoid;
}}

.index-list a {{
    color: var(--text-color);
    text-decoration: none;
    display: block;
    padding: 0.2em 0.5em;
    border-radius: 3px;
    transition: background-color 0.2s;
}}

.index-list a:hover {{
    background-color: var(--highlight-bg);
}}

.index-list .art-num {{
    font-weight: 600;
    color: var(--primary-color);
}}

/* --------------------------------------------------------------------------
   8. ENCABEZADO (HEADER/PREAMBLE) STYLES
   -------------------------------------------------------------------------- */

.encabezado {{
    text-align: center;
    margin: 2em 1em;
    padding: 1.5em;
    background: linear-gradient(135deg, rgba(11,61,145,0.05) 0%, rgba(222,31,42,0.03) 100%);
    border: 1px solid var(--border-color);
    border-radius: 8px;
    font-style: italic;
    color: var(--muted-color);
}}

.encabezado p {{
    text-indent: 0;
    margin: 0;
    line-height: 1.8;
}}

/* --------------------------------------------------------------------------
   9. CROSS-REFERENCE LINKS
   -------------------------------------------------------------------------- */

a {{
    color: var(--primary-color);
    text-decoration: none;
}}

a:hover {{
    text-decoration: underline;
}}

.cross-ref {{
    color: var(--primary-color);
    text-decoration: none;
    border-bottom: 1px dotted var(--primary-color);
    padding-bottom: 1px;
}}

.cross-ref:hover {{
    background-color: rgba(11,61,145,0.1);
    border-bottom-style: solid;
}}

.back-link {{
    font-size: 0.8em;
    color: var(--muted-color);
    margin-left: 0.5em;
}}

/* --------------------------------------------------------------------------
   10. NAVIGATION & TOC STYLES
   -------------------------------------------------------------------------- */

nav#toc {{
    padding: 1em;
}}

nav#toc h1 {{
    page-break-before: auto;
}}

nav#toc ol {{
    list-style-type: none;
    padding-left: 0;
}}

nav#toc li {{
    margin: 0.5em 0;
}}

nav#toc a {{
    color: var(--text-color);
    text-decoration: none;
    display: block;
    padding: 0.3em 0;
}}

nav#toc a:hover {{
    color: var(--primary-color);
}}

nav#toc ol ol {{
    padding-left: 1.5em;
    margin-top: 0.3em;
}}

nav#toc ol ol li {{
    font-size: 0.95em;
}}

nav#toc ol ol ol {{
    font-size: 0.9em;
}}

/* --------------------------------------------------------------------------
   11. ACCESSIBILITY & PRINT STYLES
   -------------------------------------------------------------------------- */

/* Night/Dark mode support */
@media (prefers-color-scheme: dark) {{
    :root {{
        --primary-color: #4a90d9;
        --accent-color: #ff6b6b;
        --gold-accent: #ffd93d;
        --text-color: #e8e6e0;
        --bg-color: #1a1a1a;
        --border-color: #3d3d3d;
        --muted-color: #9ca3af;
        --highlight-bg: #2d2d2d;
    }}
    
    body {{
        background-color: var(--bg-color);
        color: var(--text-color);
    }}
    
    h1, h2 {{
        color: var(--primary-color);
    }}
    
    .cover-escudo {{
        color: var(--gold-accent);
    }}
    
    .encabezado {{
        background: linear-gradient(135deg, rgba(74,144,217,0.1) 0%, rgba(255,107,107,0.05) 100%);
    }}
    
    .info-section {{
        background-color: var(--highlight-bg);
    }}
    
    .cover-metadata {{
        background-color: var(--highlight-bg);
    }}
}}

/* Sepia reading mode class (for manual toggle) */
body.sepia {{
    --primary-color: #5c4033;
    --accent-color: #8b4513;
    --text-color: #3d2914;
    --bg-color: #f4ecd8;
    --border-color: #d4c4a8;
    --highlight-bg: #ebe3d1;
    background-color: var(--bg-color);
    color: var(--text-color);
}}

/* Print styles */
@media print {{
    body {{
        font-size: 11pt;
        line-height: 1.4;
        color: #000000;
        background: #ffffff;
    }}
    
    h1 {{
        page-break-before: always;
        color: #000000;
    }}
    
    h1.no-break {{
        page-break-before: auto;
    }}
    
    .articulo-titulo {{
        page-break-after: avoid;
    }}
    
    .articulo-contenido {{
        page-break-inside: avoid;
    }}
    
    .cover {{
        page-break-after: always;
    }}
    
    a {{
        color: #000000;
        text-decoration: underline;
    }}
    
    .cross-ref {{
        border-bottom: none;
    }}
}}

/* High contrast mode support */
@media (prefers-contrast: high) {{
    :root {{
        --text-color: #000000;
        --bg-color: #ffffff;
        --border-color: #000000;
        --primary-color: #000080;
        --accent-color: #800000;
    }}
    
    a, .cross-ref {{
        text-decoration: underline;
    }}
    
    h1, h2, h3 {{
        border-width: 2px;
    }}
}}

/* Reduced motion preference */
@media (prefers-reduced-motion: reduce) {{
    * {{
        transition: none !important;
        animation: none !important;
    }}
}}

/* Focus styles for keyboard navigation */
a:focus, 
button:focus {{
    outline: 2px solid var(--primary-color);
    outline-offset: 2px;
}}

/* Screen reader only content */
.sr-only {{
    position: absolute;
    width: 1px;
    height: 1px;
    padding: 0;
    margin: -1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
    white-space: nowrap;
    border: 0;
}}

/* Skip link for navigation */
.skip-link {{
    position: absolute;
    top: -40px;
    left: 0;
    background: var(--primary-color);
    color: white;
    padding: 8px;
    z-index: 100;
}}

.skip-link:focus {{
    top: 0;
}}

/* --------------------------------------------------------------------------
   12. RESPONSIVE ADJUSTMENTS
   -------------------------------------------------------------------------- */

@media screen and (max-width: 600px) {{
    body {{
        margin: 0.5em;
    }}
    
    h1 {{
        font-size: 1.5em;
    }}
    
    h2 {{
        font-size: 1.25em;
    }}
    
    .cover-law-number {{
        font-size: 2em;
    }}
    
    .index-list {{
        column-count: 1;
    }}
}}

/* --------------------------------------------------------------------------
   13. COMPACT LEGAL INFO PAGE
   -------------------------------------------------------------------------- */

.legal-info-compact {{
    padding: 1em;
    max-width: 100%;
}}

.legal-info-compact .info-title {{
    font-size: 1.4em;
    margin-bottom: 0.8em;
    page-break-before: auto;
}}

.info-table-compact {{
    width: 100%;
    border-collapse: collapse;
    font-size: 0.9em;
    margin: 0.5em 0;
}}

.info-table-compact td {{
    padding: 0.4em 0.5em;
    border-bottom: 1px solid var(--border-color);
    vertical-align: top;
}}

.info-table-compact td.label {{
    font-weight: 600;
    width: 25%;
    color: var(--primary-color);
    white-space: nowrap;
}}

.info-table-compact .compact-text {{
    font-size: 0.95em;
    line-height: 1.3;
}}

.legal-disclaimer {{
    font-size: 0.8em;
    color: var(--muted-color);
    font-style: italic;
    margin-top: 1em;
    text-align: center;
    text-indent: 0;
}}

/* --------------------------------------------------------------------------
   14. APPENDIX STYLES
   -------------------------------------------------------------------------- */

.appendix {{
    padding: 1em;
}}

.appendix h1 {{
    page-break-before: auto;
    font-size: 1.5em;
}}

.appendix h2 {{
    font-size: 1.2em;
    margin-top: 0.5em;
}}

.promulgation-text {{
    font-size: 0.9em;
    line-height: 1.6;
    font-style: italic;
    margin: 1em 0;
    padding: 1em;
    background-color: var(--highlight-bg);
    border-left: 3px solid var(--muted-color);
}}

/* --------------------------------------------------------------------------
   15. KEYWORD INDEX STYLES
   -------------------------------------------------------------------------- */

.keyword-index {{
    padding: 1em;
}}

.keyword-index h1 {{
    page-break-before: auto;
}}

.index-intro {{
    font-style: italic;
    color: var(--muted-color);
    margin-bottom: 1.5em;
    text-indent: 0;
}}

.keyword-section {{
    margin: 1em 0;
}}

.keyword-letter {{
    font-size: 1.3em;
    color: var(--primary-color);
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.2em;
    margin-bottom: 0.5em;
}}

.keyword-entry {{
    margin: 0.3em 0;
    text-indent: 0;
    font-size: 0.95em;
}}

.keyword-entry a {{
    color: var(--primary-color);
}}

.keyword-entry a:hover {{
    text-decoration: underline;
}}
'''
        
        nav_css = epub.EpubItem(
            uid="style_premium",
            file_name="style/premium.css",
            media_type="text/css",
            content=css_content.encode('utf-8')
        )
        self.book.add_item(nav_css)

    def _create_premium_cover(self, metadata: Dict, law_data: Dict):
        title = metadata.get('title', 'Ley Chile')
        law_type = metadata.get('type', 'Ley')
        law_number = metadata.get('number', '')
        organism = metadata.get('organism', '')
        subjects = metadata.get('subjects', [])
        source = metadata.get('source', '')
        id_version = law_data.get('id_version', '')
        
        cover_chapter = epub.EpubHtml(
            title='Portada',
            file_name='cover.xhtml',
            lang='es'
        )
        cover_chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        unique_subjects = list(dict.fromkeys(subjects))[:5]
        subjects_html = ''
        if unique_subjects:
            subjects_html = f'<p class="cover-subjects">{" | ".join([self._escape_html(s) for s in unique_subjects])}</p>'
        
        organism_html = ''
        if organism:
            organism_html = f'<p class="cover-organism">{self._escape_html(organism)}</p>'
        
        version_html = ''
        if id_version:
            version_html = f'<p class="cover-source">Version: {self._escape_html(id_version)}</p>'
        
        source_html = ''
        if source:
            source_html = f'<p class="cover-source">Publicado en: {self._escape_html(source)}</p>'
        
        body_content = f'''
<div class="cover">
    <div class="cover-header">
        <p class="cover-escudo">&#9733;</p>
        <p class="cover-republica">Republica de Chile</p>
    </div>
    
    <p class="cover-law-type">{self._escape_html(law_type)}</p>
    <p class="cover-law-number">N° {self._escape_html(law_number)}</p>
    
    <div class="cover-divider"></div>
    
    <h1 class="no-break">{self._escape_html(title)}</h1>
    
    {organism_html}
    {subjects_html}
    
    <div class="cover-metadata">
        {version_html}
        {source_html}
        <p class="cover-source">Fuente: Biblioteca del Congreso Nacional de Chile</p>
    </div>
    
    <div class="cover-footer">
        <p>Documento generado el {datetime.now().strftime('%d de %B de %Y')}</p>
        <p>Generado en base a la ultima version de la ley por Luis Aguilera Arteaga</p>
    </div>
</div>
'''
        cover_chapter.set_content(body_content)
        
        self.book.add_item(cover_chapter)
        self.chapters.append(cover_chapter)

    def _create_legal_info_page(self, metadata: Dict, law_data: Dict):
        chapter = epub.EpubHtml(
            title='Informacion del Documento',
            file_name='legal_info.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        law_type = metadata.get('type', 'Ley')
        law_number = metadata.get('number', '')
        title = metadata.get('title', '')
        organism = metadata.get('organism', '')
        source = metadata.get('source', '')
        subjects = metadata.get('subjects', [])
        derogation_dates = metadata.get('derogation_dates', [])
        
        unique_subjects = list(dict.fromkeys(subjects))[:8]
        subjects_str = ', '.join([self._escape_html(s) for s in unique_subjects]) if unique_subjects else 'No especificadas'
        
        timeline_items = ''
        if derogation_dates:
            dates_str = ' | '.join([self._escape_html(d) for d in derogation_dates[:5]])
            timeline_items = f'<tr><td>Modificaciones</td><td class="compact-text">{dates_str}</td></tr>'
        
        body_content = f'''
<div class="legal-info-compact">
    <h1 class="no-break info-title">Ficha del Documento</h1>
    
    <table class="info-table-compact">
        <tr><td class="label">Tipo</td><td>{self._escape_html(law_type)} N° {self._escape_html(law_number)}</td></tr>
        <tr><td class="label">Titulo</td><td class="compact-text">{self._escape_html(title)}</td></tr>
        <tr><td class="label">Organismo</td><td>{self._escape_html(organism) if organism else '—'}</td></tr>
        <tr><td class="label">Publicacion</td><td>{self._escape_html(source) if source else '—'}</td></tr>
        <tr><td class="label">Materias</td><td class="compact-text">{subjects_str}</td></tr>
        {timeline_items}
    </table>
    
    <p class="legal-disclaimer">Generado en base a la ultima version de la ley por Luis Aguilera Arteaga.<br/>Para efectos legales, consulte la fuente oficial en la BCN.</p>
</div>
'''
        chapter.set_content(body_content)
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(chapter)

    def _create_promulgation_appendix(self, metadata: Dict):
        promulgation = metadata.get('promulgation_text', '')
        if not promulgation:
            return
        
        chapter = epub.EpubHtml(
            title='Anexo: Texto de Promulgacion',
            file_name='anexo_promulgacion.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        body_content = f'''
<div class="appendix">
    <h1 class="no-break">Anexo</h1>
    <h2>Texto de Promulgacion</h2>
    <blockquote class="promulgation-text">{self._escape_html(promulgation)}</blockquote>
</div>
'''
        chapter.set_content(body_content)
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(chapter)

    def _create_article_index_page(self):
        if not self.article_list:
            return
        
        chapter = epub.EpubHtml(
            title='Indice de Articulos',
            file_name='article_index.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        grouped_articles = {}
        for art in self.article_list:
            titulo = art.get('parent_titulo', 'Sin Titulo')
            if titulo not in grouped_articles:
                grouped_articles[titulo] = []
            grouped_articles[titulo].append(art)
        
        sections_html = []
        for titulo, articles in grouped_articles.items():
            items_html = []
            for art in articles:
                items_html.append(
                    f'<li><a href="{art["file_ref"]}"><span class="art-num">Art. {art["number"]}</span></a></li>'
                )
            
            titulo_str = titulo if titulo else 'Disposiciones Generales'
            section_title = titulo_str[:60] + '...' if len(titulo_str) > 60 else titulo_str
            sections_html.append(f'''
            <div class="index-section">
                <h3>{self._escape_html(section_title)}</h3>
                <ul class="index-list">
                    {''.join(items_html)}
                </ul>
            </div>
            ''')
        
        body_content = f'''
<div class="article-index">
    <h1 class="no-break">Indice de Articulos</h1>
    <p class="no-indent">Total de articulos: {len(self.article_list)}</p>
    {''.join(sections_html)}
</div>
'''
        chapter.set_content(body_content)
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(chapter)

    def _create_chapters(self, content: List[Dict], metadata: Dict):
        if not content:
            self._create_empty_chapter(metadata)
            return
        
        current_titulo = None
        current_titulo_content = []
        chapter_count = 0
        pre_titulo_content = []
        
        for item in content:
            item_type = item.get('type', '')
            
            if item_type == 'encabezado':
                chapter = self._create_encabezado_chapter(item)
                self.book.add_item(chapter)
                self.chapters.append(chapter)
                self.toc.append(chapter)
            
            elif item_type == 'titulo':
                if current_titulo and current_titulo_content:
                    chapter = self._create_titulo_chapter(current_titulo, current_titulo_content, chapter_count)
                    self.book.add_item(chapter)
                    self.chapters.append(chapter)
                    self.toc_sections.append((chapter, current_titulo_content))
                    chapter_count += 1
                elif not current_titulo and pre_titulo_content:
                    chapter = self._create_intro_chapter(pre_titulo_content, metadata)
                    self.book.add_item(chapter)
                    self.chapters.append(chapter)
                    self.toc.append(chapter)
                    pre_titulo_content = []
                
                current_titulo = item
                current_titulo_content = []
            
            else:
                if current_titulo is None:
                    pre_titulo_content.append(item)
                else:
                    current_titulo_content.append(item)
        
        if current_titulo and current_titulo_content:
            chapter = self._create_titulo_chapter(current_titulo, current_titulo_content, chapter_count)
            self.book.add_item(chapter)
            self.chapters.append(chapter)
            self.toc_sections.append((chapter, current_titulo_content))
        
        if pre_titulo_content and not current_titulo:
            chapter = self._create_general_chapter(pre_titulo_content, metadata)
            self.book.add_item(chapter)
            self.chapters.append(chapter)
            self.toc.append(chapter)

    def _create_encabezado_chapter(self, item: Dict) -> epub.EpubHtml:
        text = item.get('text', 'Encabezado')
        
        chapter = epub.EpubHtml(
            title='Encabezado',
            file_name='encabezado.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        body_content = f'''
<div class="encabezado">
    <p>{self._escape_html(text)}</p>
</div>
'''
        chapter.set_content(body_content)
        
        return chapter

    def _format_section_title(self, text: str) -> str:
        """Format section titles with proper separators (TITULO I - Text or multiline)."""
        if not text:
            return text
        
        patterns = [
            (r'^(TITULO\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
            (r'^(Titulo\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
            (r'^(TÍTULO\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
            (r'^(Título\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
            (r'^(Párrafo\s+\d+[°º]?)\s+(.+)$', r'\1 – \2'),
            (r'^(PARRAFO\s+\d+[°º]?)\s+(.+)$', r'\1 – \2'),
            (r'^(Capítulo\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
            (r'^(CAPITULO\s+[IVXLCDM]+)\s+(.+)$', r'\1<br/>\2'),
        ]
        
        for pattern, replacement in patterns:
            match = re.match(pattern, text, re.IGNORECASE)
            if match:
                return re.sub(pattern, replacement, text, flags=re.IGNORECASE)
        
        return text

    def _create_intro_chapter(self, content: List[Dict], metadata: Dict) -> epub.EpubHtml:
        chapter = epub.EpubHtml(
            title='Disposiciones Preliminares',
            file_name='intro.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        html_parts = [
            '<a href="#main-content" class="skip-link">Saltar al contenido principal</a>\n',
            '<main id="main-content" role="main">\n',
            '<h1 class="no-break">Disposiciones Preliminares</h1>\n'
        ]
        
        for item in content:
            html_parts.append(self._render_content_item(item))
        
        html_parts.append('</main>\n')
        chapter.set_content(''.join(html_parts))
        
        return chapter

    def _create_titulo_chapter(self, titulo: Dict, content: List[Dict], index: int) -> epub.EpubHtml:
        titulo_text = titulo.get('text', f'Titulo {index + 1}')
        formatted_title = self._format_section_title(titulo_text)
        
        short_title = titulo_text[:50] + '...' if len(titulo_text) > 50 else titulo_text
        
        chapter = epub.EpubHtml(
            title=short_title,
            file_name=f'titulo_{index + 1}.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        html_parts = [
            '<a href="#main-content" class="skip-link">Saltar al contenido principal</a>\n',
            '<main id="main-content" role="main">\n',
            f'<article role="article" aria-labelledby="titulo-{index+1}">\n',
            f'<h1 id="titulo-{index+1}">{formatted_title}</h1>\n'
        ]
        
        for item in content:
            html_parts.append(self._render_content_item(item))
        
        if len(html_parts) == 4:
            html_parts.append('<p class="no-indent">Sin contenido adicional.</p>\n')
        
        html_parts.append('</article>\n')
        html_parts.append('</main>\n')
        chapter.set_content(''.join(html_parts))
        
        return chapter

    def _create_general_chapter(self, content: List[Dict], metadata: Dict) -> epub.EpubHtml:
        title = metadata.get('title', 'Contenido')
        
        chapter = epub.EpubHtml(
            title=title[:50],
            file_name='contenido.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        html_parts = [
            '<a href="#main-content" class="skip-link">Saltar al contenido principal</a>\n',
            '<main id="main-content" role="main">\n',
            f'<h1>{self._escape_html(title)}</h1>\n'
        ]
        
        for item in content:
            html_parts.append(self._render_content_item(item))
        
        html_parts.append('</main>\n')
        chapter.set_content(''.join(html_parts))
        
        return chapter

    def _render_content_item(self, item: Dict) -> str:
        item_type = item.get('type', '')
        
        if item_type == 'parrafo':
            parrafo_text = item.get('text', '')
            formatted_parrafo = self._format_section_title(parrafo_text)
            return f'<h2>{formatted_parrafo}</h2>\n'
        
        elif item_type == 'articulo':
            article_title = item.get('title', '')
            article_text = item.get('text', '')
            
            art_id = self._extract_article_id(article_title)
            
            is_derogado = 'derogad' in article_text.lower() if article_text else False
            
            html = ''
            if article_title:
                if art_id:
                    if is_derogado:
                        html += f'<h3 id="art_{art_id}" class="articulo-titulo derogado">{self._escape_html(article_title)}<span class="derogado-notice">DEROGADO</span></h3>\n'
                    else:
                        html += f'<h3 id="art_{art_id}" class="articulo-titulo">{self._escape_html(article_title)}</h3>\n'
                else:
                    html += f'<h3 class="articulo-titulo">{self._escape_html(article_title)}</h3>\n'
            
            if article_text and not is_derogado:
                formatted_text = self._format_article_content(article_text)
                html += f'<div class="articulo-contenido">{formatted_text}</div>\n'
            
            return html
        
        elif item_type == 'texto':
            text = item.get('text', '')
            if text:
                return f'<p>{self._escape_html(text)}</p>\n'
        
        return ''

    def _create_empty_chapter(self, metadata: Dict):
        title = metadata.get('title', 'Documento')
        
        chapter = epub.EpubHtml(
            title=title,
            file_name='contenido.xhtml',
            lang='es'
        )
        chapter.add_link(href='style/premium.css', rel='stylesheet', type='text/css')
        
        body_content = f'''
<h1 class="no-break">{self._escape_html(title)}</h1>
<p class="no-indent">No se pudo extraer el contenido de este documento.</p>
<p class="no-indent">Por favor, verifique la URL proporcionada e intente nuevamente.</p>
'''
        chapter.set_content(body_content)
        
        self.book.add_item(chapter)
        self.chapters.append(chapter)
        self.toc.append(chapter)

    def _extract_article_id(self, article_title: str) -> Optional[str]:
        if not article_title:
            return None
        match = re.search(
            r'Art[íi]culo\s+(\d+(?:\s*(?:bis|ter|qu[aá]ter|quinquies|sexies|septies|octies|nonies|decies))?)', 
            article_title, re.IGNORECASE
        )
        if match:
            return match.group(1).lower().replace(' ', '')
        return None

    def _add_cross_references(self, text: str) -> str:
        def replace_ref(match):
            full_match = match.group(0)
            art_num = match.group(1).lower().replace(' ', '')
            
            if art_num in self.article_ids:
                return f'<a href="{self.article_ids[art_num]}" class="cross-ref">{full_match}</a>'
            return full_match
        
        pattern = r'art[íi]culo\s+(\d+(?:\s*(?:bis|ter|qu[aá]ter|quinquies|sexies|septies|octies|nonies|decies))?)'
        return re.sub(pattern, replace_ref, text, flags=re.IGNORECASE)

    def _format_article_content(self, text: str) -> str:
        if not text:
            return '<p></p>'
        
        text_with_refs = self._add_cross_references(text)
        
        paragraphs = text_with_refs.split('\n\n')
        formatted_parts = []
        in_inciso_list = False
        in_letra_list = False
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            is_inciso = re.match(r'^(\d+)[°º.)\-]\s*(.*)$', para)
            is_letra = re.match(r'^([a-z])[.)]\s+(.*)$', para)
            
            if is_inciso:
                if in_letra_list:
                    formatted_parts.append('</ol>')
                    in_letra_list = False
                if not in_inciso_list:
                    formatted_parts.append('<ol class="legal-list" role="list">')
                    in_inciso_list = True
                content = is_inciso.group(2) if is_inciso.group(2) else ''
                escaped = self._escape_html_preserve_links(content)
                formatted_parts.append(f'<li>{escaped}</li>')
            elif is_letra:
                if not in_letra_list:
                    if not in_inciso_list:
                        formatted_parts.append('<ol class="legal-list" role="list">')
                        in_inciso_list = True
                    formatted_parts.append('<ol class="legal-list alpha" role="list">')
                    in_letra_list = True
                content = is_letra.group(2) if is_letra.group(2) else ''
                escaped = self._escape_html_preserve_links(content)
                formatted_parts.append(f'<li>{escaped}</li>')
            else:
                if in_letra_list:
                    formatted_parts.append('</ol>')
                    in_letra_list = False
                if in_inciso_list:
                    formatted_parts.append('</ol>')
                    in_inciso_list = False
                escaped = self._escape_html_preserve_links(para)
                formatted_parts.append(f'<p>{escaped}</p>')
        
        if in_letra_list:
            formatted_parts.append('</ol>')
        if in_inciso_list:
            formatted_parts.append('</ol>')
        
        if not formatted_parts:
            return f'<p>{self._escape_html_preserve_links(text_with_refs)}</p>'
        
        return '\n'.join(formatted_parts)

    def _escape_html(self, text: str) -> str:
        if not text:
            return ''
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;'))

    def _escape_html_preserve_links(self, text: str) -> str:
        if not text:
            return ''
        
        link_pattern = r'(<a\s+href="[^"]*"\s+class="cross-ref">)(.*?)(</a>)'
        
        parts = []
        last_end = 0
        
        for match in re.finditer(link_pattern, text):
            before = text[last_end:match.start()]
            parts.append(self._escape_html(before))
            
            parts.append(match.group(1))
            parts.append(self._escape_html(match.group(2)))
            parts.append(match.group(3))
            
            last_end = match.end()
        
        parts.append(self._escape_html(text[last_end:]))
        
        return ''.join(parts)

    def _build_enhanced_toc(self):
        toc_items = list(self.toc)
        
        for chapter, content in self.toc_sections:
            sub_items = []
            for item in content:
                if item.get('type') == 'parrafo':
                    parrafo_text = item.get('text', '')
                    if parrafo_text:
                        sub_items.append(epub.Link(
                            chapter.file_name,
                            parrafo_text[:40] + '...' if len(parrafo_text) > 40 else parrafo_text,
                            chapter.id + '_' + str(len(sub_items))
                        ))
            
            if sub_items:
                toc_items.append((chapter, sub_items))
            else:
                toc_items.append(chapter)
        
        self.book.toc = tuple(toc_items)
        
        self.book.add_item(epub.EpubNcx())
        self.book.add_item(epub.EpubNav())

    def _set_spine(self):
        self.book.spine = ['nav'] + self.chapters


def generate_law_epub(law_data: Dict, output_path: str = None, customization: Dict = None) -> str:
    generator = LawEpubGenerator(customization)
    return generator.create_epub(law_data, output_path)
