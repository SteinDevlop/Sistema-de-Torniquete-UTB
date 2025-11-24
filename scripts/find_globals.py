#!/usr/bin/env python3
"""
Simple scanner para listar definiciones de funciones top-level en `src/frontend`.
Ayuda a encontrar nombres globales potencialmente conflictivos (p.ej. editarUsuario, mostrarModal, etc.).

Uso:
    python scripts/find_globals.py

Salida: imprime nombre de archivo y lista de funciones encontradas.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src' / 'frontend'
FUNC_RE = re.compile(r'^\s*function\s+([a-zA-Z0-9_]+)\s*\(', re.MULTILINE)
EXTS = ('.html', '.htm', '.js')

def scan_file(path: Path):
    txt = path.read_text(encoding='utf-8')
    return FUNC_RE.findall(txt)

def main():
    results = {}
    for f in sorted(ROOT.rglob('*')):
        if f.is_file() and f.suffix.lower() in EXTS:
            try:
                funcs = scan_file(f)
                if funcs:
                    results[str(f.relative_to(ROOT.parent))] = funcs
            except Exception as e:
                print('Error reading', f, e)

    if not results:
        print('No functions top-level encontradas.'); return

    print('Funciones top-level encontradas en frontend:')
    for k, v in results.items():
        print('-', k)
        for fn in v:
            print('   -', fn)

    print('\nRecomendación: revisar funciones con nombres comunes (editarUsuario, mostrarModal, mostrarModalAcceso, etc.) y exponer explícitamente en window.* cuando correspondan.')

if __name__ == '__main__':
    main()
