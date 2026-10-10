import json
from io import BytesIO
import httpx
import pytest
from pypdf import PdfWriter
from services.file_reader import read_file, MAX_BYTES
from services.duplicates import duplicate_groups
from services.ai_service import analyze_document, analyze_into, AnalysisError
from services.organizer import plan, approve
from services.search_service import search
from services.demo import load_demo


def test_exact_duplicates_use_bytes_not_names():
    a = read_file('a.txt', b'hello world')
    b = read_file('b.md', b'hello world')
    c = read_file('a.txt', b'hello other world')
    assert duplicate_groups([a,b,c]) == [[a,b]]

@pytest.mark.parametrize('name,content', [('x.exe',b'abc'),('x.txt',b''),('x.txt',b'\xff'),('x.txt',b'\x00abc'),('x.pdf',b'not a pdf'),('x.txt',b'x'*(MAX_BYTES+1)),('x.txt',b'x'*200001)])
def test_bad_uploads(name,content):
    with pytest.raises(ValueError):
        read_file(name, content)

def test_blank_pdf():
    writer = PdfWriter()
    writer.add_blank_page(width=100,height=100)
    stream = BytesIO()
    writer.write(stream)
    with pytest.raises(ValueError, match='No readable text'):
        read_file('scan.pdf',stream.getvalue())

def test_search_and_plan():
    docs = load_demo()
    assert len(docs) == 8
    assert len(duplicate_groups(docs)) == 1
    assert len(search(docs,'Find my notes about photosynthesis')) == 2
    assert search(docs,'Show me the project proposal with the budget')[0][0].name == 'project_v3.md'
    assert not search(docs,'quantum levitation')
    rows = plan(docs)
    approve(docs, [rows[0]['id']])
    assert len(plan(docs)) == len(rows)-1
    assert all(d.status == 'Demo' for d in docs)

def test_missing_credentials_does_not_fallback(monkeypatch):
    monkeypatch.delenv('DIGITALOCEAN_API_KEY', raising=False)
    doc = read_file('a.txt',b'some text about photosynthesis')
    analyze_into(doc, 'digitalocean')
    assert doc.status == 'Failed'
    assert not doc.summary
    assert 'Missing credentials' in doc.error

def test_live_adapters_and_validation(monkeypatch):
    monkeypatch.setenv('DIGITALOCEAN_API_KEY','test')
    monkeypatch.setenv('DIGITALOCEAN_MODEL','test-model')
    monkeypatch.setenv('SNOWFLAKE_PAT','test')
    monkeypatch.setenv('SNOWFLAKE_MODEL','test-model')
    monkeypatch.setenv('SNOWFLAKE_ACCOUNT_URL','https://example.snowflakecomputing.com')
    result = analyze_document('photosynthesis and chlorophyll are biology topics','x.txt','demo')
    urls = []
    def post(url, **kwargs):
        urls.append(url)
        assert len(json.loads(kwargs['json']['messages'][1]['content'])['document_text']) == 12000
        return httpx.Response(200,json={'choices':[{'message':{'content':json.dumps(result)}}]},request=httpx.Request('POST',url))
    monkeypatch.setattr(httpx,'post',post)
    for provider in ['digitalocean','snowflake']:
        assert analyze_document('x'*13000,'x.txt',provider) == result
    assert urls == ['https://inference.do-ai.run/v1/chat/completions','https://example.snowflakecomputing.com/api/v2/cortex/v1/chat/completions']
    monkeypatch.setattr(httpx,'post',lambda *a,**k:httpx.Response(200,json={'choices':[]},request=httpx.Request('POST','https://example.com')))
    with pytest.raises(AnalysisError,match='unreadable'):
        analyze_document('abc','x.txt','digitalocean')

def test_http_errors_are_safe(monkeypatch):
    monkeypatch.setenv('DIGITALOCEAN_API_KEY','secret')
    monkeypatch.setenv('DIGITALOCEAN_MODEL','test-model')
    monkeypatch.setattr(httpx,'post',lambda *a,**k:httpx.Response(401,text='secret private document',request=httpx.Request('POST','https://example.com')))
    doc = read_file('x.txt',b'private text')
    analyze_into(doc,'digitalocean')
    assert doc.status == 'Failed' and '401' in doc.error
    assert 'private' not in doc.error and 'secret' not in doc.error
