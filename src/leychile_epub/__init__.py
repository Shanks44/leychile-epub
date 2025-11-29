"""
LeyChile ePub Generator
=======================

Generador de libros electrónicos (ePub) para legislación chilena.

Este paquete permite convertir leyes, decretos y otras normas de la
Biblioteca del Congreso Nacional de Chile en archivos ePub profesionales.

Ejemplo de uso (v2 - recomendado):
    >>> from leychile_epub.scraper_v2 import BCNLawScraperV2
    >>> from leychile_epub.generator_v2 import EPubGeneratorV2
    >>> scraper = BCNLawScraperV2()
    >>> norma = scraper.scrape("https://www.leychile.cl/Navegar?idNorma=1058072")
    >>> generator = EPubGeneratorV2()
    >>> epub_path = generator.generate(norma, "output/ley.epub")

Ejemplo de uso (v1 - legacy):
    >>> from leychile_epub import BCNLawScraper, LawEpubGenerator
    >>> scraper = BCNLawScraper()
    >>> law_data = scraper.scrape_law("https://www.leychile.cl/Navegar?idNorma=242302")
    >>> generator = LawEpubGenerator()
    >>> epub_path = generator.generate(law_data)

Author: Luis Aguilera Arteaga <luis@aguilera.cl>
License: MIT
"""

__version__ = "1.5.0"
__author__ = "Luis Aguilera Arteaga"
__email__ = "luis@aguilera.cl"
__license__ = "MIT"

from .config import Config
from .exceptions import (
    GeneratorError,
    LeyChileError,
    NetworkError,
    ScraperError,
    ValidationError,
)
from .generator import LawEpubGenerator
from .scraper import BCNLawScraper

__all__ = [
    # Clases principales
    "BCNLawScraper",
    "LawEpubGenerator",
    "Config",
    # Excepciones
    "LeyChileError",
    "ScraperError",
    "GeneratorError",
    "ValidationError",
    "NetworkError",
    # Metadata
    "__version__",
    "__author__",
    "__email__",
]
