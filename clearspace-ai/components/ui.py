from html import escape
import streamlit as st

COLORS = ['#72927a', '#9a8db3', '#c39675', '#788faa', '#b2a263', '#a1aaa4']

def theme(dark):
    bg, surface, side, ink, muted, line, accent, tint = (
        ('#151c19', '#1e2822', '#19211c', '#ecf2eb', '#a3b2a7', '#334239', '#b5d3ae', '#28392b') if dark else
        ('#f7f8f5', '#ffffff', '#eff2eb', '#263a2d', '#788279', '#e0e6dd', '#476b4c', '#e9f0e4'))
    st.markdown(f'''<style>
    .stApp {{background:{bg};color:{ink}; --text-color:{ink}; --background-color:{bg}; --secondary-background-color:{side};}}
    [data-testid="stHeader"] {{background:{bg};}}
    [data-testid="stSidebar"] {{background:{side};border-right:1px solid {line};}}
    [data-testid="stSidebar"] * {{color:{ink};}}
    .block-container {{max-width:1280px;padding-top:2.7rem;padding-bottom:4rem;}}
    h1,h2,h3,p,label,[data-testid="stMetricValue"],[data-testid="stMetricLabel"] {{color:{ink};}}
    h1 {{font-size:2.5rem!important;letter-spacing:-1.4px;font-weight:550!important;}}
    h2 {{font-size:1.35rem!important;letter-spacing:-.4px;}}
    h3 {{font-size:1.07rem!important;}}
    [data-testid="stCaptionContainer"] p {{color:{muted};}}
    [data-testid="stMetric"] {{background:{surface};border:1px solid {line};border-radius:14px;padding:21px;}}
    [data-testid="stMetricValue"] {{font-size:2rem;font-weight:500;}}
    [data-testid="stVerticalBlockBorderWrapper"]>div {{border-color:{line}!important;border-radius:14px!important;}}
    [data-testid="stButton"] button,[data-testid="stDownloadButton"] button {{background:{surface};color:{ink};border:1px solid {line};border-radius:9px;transition:all .16s ease;}}
    [data-testid="stButton"] button:hover {{border-color:{accent};background:{tint};}}
    [data-testid="stButton"] button[kind="primary"] {{background:{accent};color:{bg};border-color:{accent};}}
    [data-testid="stButton"] button[kind="primary"] p {{color:{bg};}}
    [data-baseweb="input"],[data-baseweb="textarea"],[data-baseweb="select"]>div {{background:{surface}!important;color:{ink}!important;border-color:{line}!important;}}
    input,textarea {{color:{ink}!important;-webkit-text-fill-color:{ink}!important;}}
    [data-baseweb="select"] span {{color:{ink}!important;}}
    [data-baseweb="popover"] *,[role="listbox"] {{background:{surface};color:{ink};}}
    [data-testid="stFileUploaderDropzone"] {{background:{surface};border:1px dashed {accent};border-radius:14px;}}
    [data-testid="stFileUploaderDropzone"] * {{color:{ink};}}
    [data-testid="stExpander"] {{background:{surface};border-color:{line};}}
    [data-testid="stExpander"] summary,[data-testid="stAlert"] p {{color:{ink};}}
    .eyebrow {{font-size:11px;font-weight:600;letter-spacing:2px;color:{muted};margin-bottom:12px;}}
    .brand {{display:flex;gap:10px;align-items:center;font-size:23px;font-weight:600;letter-spacing:-.8px;margin-bottom:8px;}}
    .brand svg {{width:32px;height:32px;}}
    .hero {{background:{tint};border:1px solid {line};padding:24px 28px;border-radius:16px;position:relative;overflow:hidden;margin:8px 0 24px;}}
    .hero h3 {{font-size:1.35rem!important;margin:0 0 8px;}}
    .hero p {{margin:0;max-width:680px;color:{muted};font-size:14px;}}
    .tag {{display:inline-block;font-size:11px;background:{tint};color:{accent};border-radius:5px;padding:3px 7px;margin:0 5px 7px 0;}}
    .doc-title {{font-weight:600;font-size:15px;overflow-wrap:anywhere;margin:4px 0 8px;}}
    .doc-summary {{font-size:13px;color:{muted};line-height:1.65;min-height:62px;}}
    .meta {{font-size:11px;color:{muted};margin:9px 0;}}
    .collection {{height:95px;}}
    .collection-dot {{width:28px;height:7px;border-radius:8px;margin:6px 0 16px;}}
    .collection-title {{font-size:15px;font-weight:600;}}
    .bar-track {{height:7px;background:{line};border-radius:5px;margin:7px 0 14px;overflow:hidden;}}
    .bar-fill {{height:7px;border-radius:5px;}}
    .empty {{padding:45px 25px;text-align:center;border:1px dashed {line};border-radius:16px;}}
    .stCode pre {{background:{surface}!important;color:{ink}!important;}}
    @media(max-width:700px) {{.block-container{{padding:2rem 1rem;}}h1{{font-size:2rem!important;}}}}
    @media(prefers-reduced-motion:reduce) {{*{{transition:none!important;}}}}
    </style>''', unsafe_allow_html=True)

def brand():
    st.markdown('''<div class="brand"><svg viewBox="0 0 32 32" fill="none" aria-hidden="true"><rect width="32" height="32" rx="10" fill="#64836b"/><path d="M9 12h14M9 17h10M9 22h6" stroke="#f7faf3" stroke-width="2.5" stroke-linecap="round"/></svg>ClearSpace</div>''', unsafe_allow_html=True)

def heading(title, subtitle):
    st.title(title)
    st.caption(subtitle)

def file_card(doc, on_open, reason=''):
    with st.container(border=True):
        tags = f'<span class="tag">{escape(doc.kind)}</span><span class="tag">{escape(doc.status)}</span>'
        if doc.source == 'Sample':
            tags += '<span class="tag">Fictional sample</span>'
        st.markdown(tags + f'<div class="doc-title">{escape(doc.name)}</div><div class="doc-summary">{escape(doc.summary or "Ready for analysis. Open this document to explore its text.")[:260]}</div><div class="meta">{escape(doc.category)} · {doc.size/1024:.1f} KB</div>', unsafe_allow_html=True)
        if reason:
            st.caption(reason)
        if doc.error:
            st.error(doc.error)
        if st.button('Open document →', key='open_' + doc.id, use_container_width=True):
            on_open(doc.id)

def grid(docs, on_open, reasons=None):
    if not docs:
        st.markdown('<div class="empty"><h3>A little room for something new.</h3><p>Add documents or try a different search.</p></div>', unsafe_allow_html=True)
    for start in range(0, len(docs), 3):
        for col, doc in zip(st.columns(3), docs[start:start+3]):
            with col:
                file_card(doc, on_open, (reasons or {}).get(doc.id, ''))
