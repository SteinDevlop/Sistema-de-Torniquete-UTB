#!/usr/bin/env python3
"""
Script seguro para reemplazar patrones simples de estilos inline por clases CSS.
Actualmente reemplaza únicamente casos sencillos de `style="display:none"` (y variantes)
por la clase `d-none`. Si encuentra un atributo `class` existente lo fusiona.

Uso:
    python scripts/replace_inline_styles.py

Genera respaldos de los archivos modificados con extensión `.bak`.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / 'src' / 'frontend'
PATTERN_CLASS_BEFORE = re.compile(r'(class\s*=\s*"([^"]*)")\s*(style\s*=\s*"\s*display\s*:\s*none\s*;?\s*")', flags=re.IGNORECASE)
PATTERN_STYLE_BEFORE = re.compile(r'style\s*=\s*"\s*display\s*:\s*none\s*;?\s*"\s*(class\s*=\s*"([^"]*)")', flags=re.IGNORECASE)
PATTERN_STYLE_ALONE = re.compile(r'style\s*=\s*"\s*display\s*:\s*none\s*;?\s*"', flags=re.IGNORECASE)

EXTS = ('.html', '.htm', '.js')

def process_file(path: Path):
    txt = path.read_text(encoding='utf-8')
    orig = txt
    changed = False

    # class before style
    def repl_class_before(m):
        cls = m.group(2).strip()
        new_cls = (cls + ' d-none').strip()
        return f'class="{new_cls}"'

    txt, n1 = PATTERN_CLASS_BEFORE.subn(repl_class_before, txt)
    if n1:
        changed = True

    # style before class
    def repl_style_before(m):
        cls = m.group(2).strip()
        new_cls = (cls + ' d-none').strip()
        return f'class="{new_cls}"'

    txt, n2 = PATTERN_STYLE_BEFORE.subn(repl_style_before, txt)
    if n2:
        changed = True

    # style alone -> add class attribute
    def repl_style_alone(m):
        return 'class="d-none"'

    txt, n3 = PATTERN_STYLE_ALONE.subn(repl_style_alone, txt)
    if n3:
        changed = True

    if changed and txt != orig:
        bak = path.with_suffix(path.suffix + '.bak')
        path.replace(bak)
        path.write_text(txt, encoding='utf-8')
        print(f'Updated {path} (backup at {bak.name})')

def main():
    print('Scanning frontend for inline display:none patterns...')
    files = list(ROOT.rglob('*'))
    for f in files:
        if f.is_file() and f.suffix.lower() in EXTS:
            try:
                process_file(f)
            except Exception as e:
                print('Error processing', f, e)

    print('Done. Revisa los archivos modificados y prueba la app.')

if __name__ == '__main__':
    main()
