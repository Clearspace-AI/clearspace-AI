from hashlib import sha256
from io import BytesIO
from pathlib import PurePath
from pypdf import PdfReader
from .models import Document

MAX_BYTES = 10 * 1024 * 1024
MAX_CHARS = 200_000

def read_file(name: str, content: bytes, source='Upload') -> Document:
    name = PurePath(name.replace('\\', '/')).name
    kind = PurePath(name).suffix.lower()
    if kind not in {'.txt', '.md', '.pdf'}:
        raise ValueError('Supported formats: TXT, Markdown, and text-based PDF.')
    if not content:
        raise ValueError('This file is empty.')
    if len(content) > MAX_BYTES:
        raise ValueError('This file exceeds the 10 MB limit.')
    if kind == '.pdf':
        try:
            reader = PdfReader(BytesIO(content))
            if reader.is_encrypted:
                raise ValueError('Encrypted PDFs are not supported. Upload an unlocked copy.')
            if len(reader.pages) > 100:
                raise ValueError('PDFs are limited to 100 pages.')
            parts, total = [], 0
            for page in reader.pages:
                # Guard against extremely large decompressed page streams.
                stream = page.get_contents()
                if stream is not None and len(stream.get_data()) > 5_000_000:
                    raise ValueError('This PDF page is too complex to extract safely.')
                part = page.extract_text() or ''
                total += len(part)
                if total > MAX_CHARS:
                    raise ValueError('Extracted text exceeds 200,000 characters.')
                parts.append(part)
            text = '\n'.join(parts)
        except ValueError:
            raise
        except Exception:
            raise ValueError('Could not extract this PDF. Try exporting a text-based copy.') from None
    else:
        try:
            text = content.decode('utf-8-sig')
        except UnicodeDecodeError:
            raise ValueError('Please save text files using UTF-8 encoding.') from None
        if '\x00' in text:
            raise ValueError('This looks like a binary file rather than plain text.')
    text = text.strip()
    if not text:
        raise ValueError('No readable text found. Scanned PDFs need OCR, which is not included.')
    if len(text) > MAX_CHARS:
        raise ValueError('Extracted text exceeds 200,000 characters.')
    return Document(name=name, text=text, size=len(content), digest=sha256(content).hexdigest(), kind=kind[1:].upper(), source=source)
