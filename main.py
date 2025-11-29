#!/usr/bin/env python3
"""
Punto de entrada principal para el generador de eBooks de Leyes Chilenas.

Uso:
    python main.py                    # Muestra ayuda
    python main.py <url>              # Descarga una ley específica
    python main.py --web              # Inicia la interfaz web (requiere streamlit)
"""

import sys

def main():
    if len(sys.argv) > 1:
        if sys.argv[1] == '--web':
            try:
                import subprocess
                subprocess.run([sys.executable, '-m', 'streamlit', 'run', 'app.py'])
            except ImportError:
                print("❌ Para usar la interfaz web, instala streamlit:")
                print("   pip install streamlit")
                sys.exit(1)
        else:
            # Usar CLI para procesar URLs
            from cli import main as cli_main
            cli_main()
    else:
        print(__doc__)
        print("\nEjemplos:")
        print('  python main.py "https://www.bcn.cl/leychile/navegar?idNorma=30082"')
        print('  python main.py "https://www.bcn.cl/leychile/navegar?idNorma=61107"')
        print('  python main.py --web  # Interfaz gráfica (requiere streamlit)')


if __name__ == "__main__":
    main()
