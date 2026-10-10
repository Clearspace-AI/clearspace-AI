from pathlib import Path
from .file_reader import read_file
from .ai_service import analyze_into

def load_demo():
    docs = []
    for path in sorted((Path(__file__).resolve().parents[1] / 'data/demo_files').iterdir()):
        doc = read_file(path.name, path.read_bytes(), source='Sample')
        analyze_into(doc, 'demo')
        docs.append(doc)
    return docs
