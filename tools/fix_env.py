import sys
from pathlib import Path
p = Path(__file__).resolve().parent.parent / '.env'
if not p.exists():
    print('.env not found')
    sys.exit(1)
raw = p.read_bytes()
text = None
for enc in ('utf-8','utf-16','latin-1'):
    try:
        text = raw.decode(enc)
        print('decoded using',enc)
        break
    except Exception:
        pass
if text is None:
    print('failed to decode .env')
    sys.exit(2)
# write utf-8 without BOM
p.write_text(text, encoding='utf-8')
print('rewrote .env as utf-8')
