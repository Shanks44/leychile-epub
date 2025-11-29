#!/usr/bin/env python3
"""
CLI para descargar leyes chilenas desde la Biblioteca del Congreso Nacional
y convertirlas a formato ePub.

Uso:
    python cli.py <url_de_la_ley> [--output nombre_archivo.epub]
    python cli.py --batch archivo_urls.txt [--output-dir directorio]

Ejemplos:
    python cli.py "https://www.bcn.cl/leychile/navegar?idNorma=30082"
    python cli.py "https://www.bcn.cl/leychile/navegar?idNorma=61107" --output codigo_trabajo.epub
    python cli.py --batch urls.txt --output-dir ./epubs
"""

import argparse
import os
import sys
from pathlib import Path

from bcn_scraper import scrape_bcn_law
from epub_generator import generate_law_epub


def print_progress(progress: float, message: str):
    """Callback para mostrar progreso."""
    bar_length = 30
    filled = int(bar_length * progress)
    bar = '█' * filled + '░' * (bar_length - filled)
    print(f'\r[{bar}] {int(progress * 100):3d}% {message}', end='', flush=True)
    if progress >= 1.0:
        print()  # Nueva línea al completar


def process_single_url(url: str, output_path: str = None) -> str:
    """Procesa una URL individual y genera el ePub."""
    print(f"\n📥 Descargando ley desde: {url}")
    
    try:
        # Obtener datos de la ley
        law_data = scrape_bcn_law(url, print_progress)
        
        metadata = law_data.get('metadata', {})
        law_type = metadata.get('type', 'Ley')
        law_number = metadata.get('number', 'documento')
        title = metadata.get('title', 'Sin título')
        
        print(f"\n📋 Información de la ley:")
        print(f"   • Tipo: {law_type}")
        print(f"   • Número: {law_number}")
        print(f"   • Título: {title[:80]}{'...' if len(title) > 80 else ''}")
        
        # Estadísticas del contenido
        content = law_data.get('content', [])
        titulos = len([c for c in content if c.get('type') == 'titulo'])
        articulos = len([c for c in content if c.get('type') == 'articulo'])
        print(f"   • Títulos: {titulos}")
        print(f"   • Artículos: {articulos}")
        
        # Generar nombre de archivo si no se especificó
        if not output_path:
            safe_type = law_type.replace(' ', '_')
            safe_number = law_number.replace(' ', '_')
            output_path = f"{safe_type}_{safe_number}.epub"
        
        # Generar ePub
        print(f"\n📖 Generando ePub...")
        result_path = generate_law_epub(law_data, output_path)
        
        file_size = os.path.getsize(result_path)
        print(f"✅ ePub generado exitosamente: {result_path}")
        print(f"   Tamaño: {file_size / 1024:.1f} KB")
        
        return result_path
        
    except ValueError as e:
        print(f"\n❌ Error de URL: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error al procesar la ley: {e}")
        sys.exit(1)


def process_batch(input_file: str, output_dir: str = None) -> list:
    """Procesa múltiples URLs desde un archivo."""
    if not os.path.exists(input_file):
        print(f"❌ El archivo {input_file} no existe")
        sys.exit(1)
    
    # Leer URLs del archivo
    with open(input_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("❌ No se encontraron URLs en el archivo")
        sys.exit(1)
    
    print(f"\n📋 Se procesarán {len(urls)} leyes")
    
    # Crear directorio de salida si no existe
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    else:
        output_dir = '.'
    
    results = []
    successful = 0
    failed = 0
    
    for i, url in enumerate(urls, 1):
        print(f"\n{'='*60}")
        print(f"📌 Procesando {i}/{len(urls)}")
        
        try:
            # Obtener datos de la ley
            law_data = scrape_bcn_law(url, print_progress)
            
            metadata = law_data.get('metadata', {})
            law_type = metadata.get('type', 'Ley').replace(' ', '_')
            law_number = metadata.get('number', 'documento').replace(' ', '_')
            
            output_path = os.path.join(output_dir, f"{law_type}_{law_number}.epub")
            
            # Generar ePub
            result_path = generate_law_epub(law_data, output_path)
            
            results.append({
                'url': url,
                'success': True,
                'path': result_path,
                'title': metadata.get('title', 'Sin título')
            })
            successful += 1
            print(f"✅ Generado: {result_path}")
            
        except Exception as e:
            results.append({
                'url': url,
                'success': False,
                'error': str(e)
            })
            failed += 1
            print(f"❌ Error: {e}")
    
    # Resumen final
    print(f"\n{'='*60}")
    print(f"📊 Resumen:")
    print(f"   ✅ Exitosos: {successful}")
    print(f"   ❌ Fallidos: {failed}")
    print(f"   📁 Directorio: {os.path.abspath(output_dir)}")
    
    return results


def main():
    parser = argparse.ArgumentParser(
        description='Descarga leyes chilenas desde BCN y las convierte a ePub',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  %(prog)s "https://www.bcn.cl/leychile/navegar?idNorma=30082"
  %(prog)s "https://www.bcn.cl/leychile/navegar?idNorma=61107" -o codigo_trabajo.epub
  %(prog)s --batch urls.txt --output-dir ./epubs

El archivo para --batch debe contener una URL por línea.
Las líneas que comienzan con # son ignoradas.
        """
    )
    
    parser.add_argument(
        'url',
        nargs='?',
        help='URL de la ley en bcn.cl/leychile'
    )
    
    parser.add_argument(
        '-o', '--output',
        help='Nombre del archivo ePub de salida'
    )
    
    parser.add_argument(
        '-b', '--batch',
        help='Archivo con lista de URLs (una por línea)'
    )
    
    parser.add_argument(
        '-d', '--output-dir',
        default='.',
        help='Directorio para los archivos de salida (modo batch)'
    )
    
    args = parser.parse_args()
    
    print("╔══════════════════════════════════════════════════════════╗")
    print("║     🇨🇱  Generador de eBooks - Leyes Chile  🇨🇱            ║")
    print("║     Fuente: Biblioteca del Congreso Nacional             ║")
    print("╚══════════════════════════════════════════════════════════╝")
    
    if args.batch:
        # Modo batch
        process_batch(args.batch, args.output_dir)
    elif args.url:
        # Modo single
        process_single_url(args.url, args.output)
    else:
        parser.print_help()
        print("\n❌ Debes proporcionar una URL o usar --batch con un archivo")
        sys.exit(1)


if __name__ == '__main__':
    main()
