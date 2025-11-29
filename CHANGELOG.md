# Changelog

Todos los cambios notables de este proyecto serán documentados en este archivo.

El formato está basado en [Keep a Changelog](https://keepachangelog.com/es-ES/1.0.0/),
y este proyecto adhiere a [Semantic Versioning](https://semver.org/lang/es/).

## [Unreleased]

### Agregado
- Interfaz de línea de comandos (CLI) para uso sin interfaz gráfica
- Soporte para procesamiento por lotes de múltiples leyes
- Documentación completa del proyecto
- Archivos de comunidad (CODE_OF_CONDUCT, CONTRIBUTING, etc.)

### Cambiado
- Migración del proyecto desde Replit a desarrollo local
- Actualización del README con documentación completa

### Eliminado
- Archivos específicos de Replit (replit.md, store.json, uv.lock)

## [1.0.0] - 2024-11-29

### Agregado
- Scraper para la API XML de la Biblioteca del Congreso Nacional (BCN)
- Generador de ePub con formato premium y estilos profesionales
- Interfaz web con Streamlit para uso interactivo
- Clasificación automática de tipos de normas (leyes, códigos, decretos, etc.)
- Tabla de contenidos interactiva en los ePub generados
- Índice de palabras clave
- Sistema de referencias cruzadas
- Metadatos completos en los ePub (autor, fecha, identificadores)
- Atribución automática al creador del documento

### Características del ePub
- Portada personalizada con información de la norma
- Estilos CSS profesionales para lectura cómoda
- Navegación jerárquica (títulos, capítulos, artículos)
- Compatible con todos los lectores de ePub estándar
- Optimizado para e-readers (Kindle, Kobo, etc.)

---

## Tipos de Cambios

- `Agregado` para nuevas funcionalidades
- `Cambiado` para cambios en funcionalidades existentes
- `Obsoleto` para funcionalidades que serán eliminadas próximamente
- `Eliminado` para funcionalidades eliminadas
- `Corregido` para corrección de bugs
- `Seguridad` para vulnerabilidades

[Unreleased]: https://github.com/laguileracl/leychile-epub/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/laguileracl/leychile-epub/releases/tag/v1.0.0
