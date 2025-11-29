"""
Entry point para ejecutar el módulo como script.

Uso:
    python -m leychile_epub https://www.leychile.cl/Navegar?idNorma=242302

Author: Luis Aguilera Arteaga <luis@aguilera.cl>
"""

from .cli import main

if __name__ == "__main__":
    main()
