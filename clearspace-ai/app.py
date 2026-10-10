"""ClearSpace — run with: python -m streamlit run app.py"""
import json
from collections import Counter
from html import escape
from pathlib import Path
import streamlit as st
from dotenv import load_dotenv
from components.ui import theme, brand, heading, grid, COLORS
from services.models import CATEGORIES
from services.demo import load_demo
from services.file_reader import read_file
load_dotenv(Path(__file__).parent / '.env')
from services.ai_service import configured_provider, analyze_into, MAX_AI_CHARS
from services.duplicates import duplicate_groups
from services.search_service import search
from services.organizer import plan, approve

st.set_page_config(page_title='ClearSpace · A little more space to think', page_icon='🌿', layout='wide')
PAGES = ['Overview', 'All files', 'Smart collections', 'Duplicate files', 'Recently analyzed', 'Organization plan', 'Add files', 'Settings']
for key, value in {'docs': None, 'page': 'Overview', 'selected': None, 'dark': False, 'mode': configured_provider(), 'collection_filter': 'All', 'upload_version': 0}.items():
    if key not in st.session_state:
        st.session_state[key] = value
if st.session_state.docs is None:
    st.session_state.docs = load_demo()
docs = st.session_state.docs

def go(page):
    st.session_state.page = page
    st.session_state.selected = None

def open_doc(doc_id):
    st.session_state.selected = doc_id
    st.rerun()

with st.sidebar:
    brand()
    st.caption('YOUR INTELLIGENT WORKSPACE')
    st.divider()
    icons = ['dashboard', 'description', 'folder_open', 'content_copy', 'history', 'drive_file_move', 'upload_file', 'settings']
    for page, icon in zip(PAGES, icons):
        st.button(page, icon=f':material/{icon}:', key='nav_'+page,
                  type='primary' if st.session_state.page == page else 'secondary',
                  use_container_width=True, on_click=go, args=(page,))
    st.divider()
    st.toggle('Dark mode', key='dark')
    st.caption('PERSONAL WORKSPACE')
    st.write('ClearSpace demo studio')
    st.caption(f'{len(docs)} documents · session storage')
    st.caption('Demo results use local rules. Hosted AI runs only after your approval.')

theme(st.session_state.dark)
top_left, top_right = st.columns([5, 1])
with top_left:
    st.markdown('<div class="eyebrow">WORKSPACE / '+escape(st.session_state.page.upper())+'</div>', unsafe_allow_html=True)
with top_right:
    st.button('Add files', icon=':material/add:', type='primary', use_container_width=True, on_click=go, args=('Add files',))
query = st.text_input('Search your workspace', placeholder='Search ideas, not just filenames. Try “notes about photosynthesis”…', label_visibility='collapsed', key='search')
if st.session_state.mode == 'demo':
    st.caption('◌ DEMO MODE · Local keyword rules and text extracts. No AI requests are made.')
else:
    st.caption(f'PROVIDER: {st.session_state.mode.upper()} · Existing sample results remain labeled Demo.')


def analysis_controls(targets, key):
    provider = st.session_state.mode
    consent = True
    if provider != 'demo':
        consent = st.checkbox(f'Send filenames and the first {MAX_AI_CHARS:,} text characters per document to {provider}.', key='consent_'+key)
        st.caption('Only selected documents are sent. Longer files are analyzed from an excerpt; full extracted text remains searchable.')
    label = 'Run demo analysis' if provider == 'demo' else 'Analyze with '+provider
    if st.button(label, key='analyze_'+key, disabled=not targets or not consent, type='primary'):
        progress = st.progress(0, text='Preparing documents…')
        for i, doc in enumerate(targets):
            progress.progress(i / len(targets), text=f'Analyzing {i+1} of {len(targets)}: {doc.name}')
            analyze_into(doc, provider)
        failures = sum(d.status == 'Failed' for d in targets)
        st.session_state.notice = f'Analysis finished: {len(targets)-failures} completed, {failures} failed. Failed documents can be retried.'
        st.rerun()

if 'notice' in st.session_state:
    st.info(st.session_state.pop('notice'))

selected = next((d for d in docs if d.id == st.session_state.selected), None)
if selected:
    if st.button('← Back to workspace'):
        st.session_state.selected = None
        st.rerun()
    heading(selected.name, f'{selected.kind} · {selected.size:,} bytes · Imported {selected.imported_at[:16]} UTC · {selected.source}')
    left, right = st.columns([1.6, 1])
    with left:
        st.subheader('Document preview')
        st.text_area('Extracted text', selected.text, height=440, disabled=True)
        st.caption('Text extraction runs on the machine hosting this app. Original files are never moved.')
    with right:
        st.subheader('Document intelligence')
        st.write('Status: '+selected.status+(' · manually edited' if selected.edited else ''))
        if selected.status == 'Demo':
            st.caption('Mock analysis: keyword classification and an extract, not an AI-generated summary.')
        if selected.error:
            st.error(selected.error)
        st.write(selected.summary or 'No summary yet.')
        st.caption(' · '.join(selected.keywords))
        st.write('Suggested collection: '+(selected.suggested_collection or 'Not analyzed'))
        st.caption(selected.reason)
        st.caption('Current collection: '+selected.collection)
        analysis_controls([selected], 'detail')
    with st.expander('Edit category and summary'):
        with st.form('edit_'+selected.id):
            category = st.selectbox('Category', CATEGORIES, index=CATEGORIES.index(selected.category))
            summary = st.text_area('Summary', selected.summary, max_chars=1200)
            if st.form_submit_button('Save changes'):
                selected.category, selected.summary, selected.edited = category, summary, True
                selected.suggested_collection = category
                selected.reason = 'Collection selected through your category edit.'
                st.rerun()
    related = [d for d in docs if d.id != selected.id and selected.category != 'Uncategorized' and d.category == selected.category][:3]
    if related:
        st.subheader('Related documents')
        grid(related, open_doc)
elif query.strip():
    heading('Find a little clarity.', 'Search across filenames, full extracted text, summaries, keywords, and categories. All meaningful query terms must match; this is keyword search, not semantic search.')
    results = search(docs, query)
    st.caption(f'{len(results)} matching documents')
    grid([r[0] for r in results], open_doc, {r[0].id:r[1] for r in results})
elif st.session_state.page == 'Overview':
    heading('A little more space to think.', 'Your documents, thoughtfully brought together. Find what matters and give everything a place.')
    groups = duplicate_groups(docs)
    counts = Counter(d.category for d in docs)
    cols = st.columns(4)
    values = [('Total documents', len(docs)), ('Documents analyzed', sum(d.status in {'Demo','AI analyzed'} for d in docs)), ('Smart collections', len({d.category for d in docs if d.category != 'Uncategorized'})), ('Extra duplicate copies', sum(len(g)-1 for g in groups))]
    for col, (label, value) in zip(cols, values):
        col.metric(label, value)
    st.caption(f"Analysis includes {sum(d.status == 'Demo' for d in docs)} demo results and {sum(d.status == 'AI analyzed' for d in docs)} real AI results.")
    st.markdown('<div class="hero"><div class="eyebrow">LESS SEARCHING. MORE DOING.</div><h3>From scattered files to a clearer mind.</h3><p>Explore your collections, rediscover a useful idea, or review a new home for your documents. You stay in control of every change.</p></div>', unsafe_allow_html=True)
    main, aside = st.columns([2.2, 1])
    with main:
        st.subheader('Your smart collections')
        for start in (0, 3):
            for col, cat, color in zip(st.columns(3), CATEGORIES[start:start+3], COLORS[start:start+3]):
                with col, st.container(border=True):
                    st.markdown(f'<div class="collection"><div class="collection-dot" style="background:{color}"></div><div class="collection-title">{escape(cat)}</div><div class="meta">{counts[cat]} documents</div></div>', unsafe_allow_html=True)
                    if st.button('Explore →', key='collection_'+cat, use_container_width=True):
                        st.session_state.collection_filter = cat
                        go('Smart collections')
                        st.rerun()
    with aside:
        st.subheader('A view of your library')
        with st.container(border=True):
            for cat, color in zip(CATEGORIES, COLORS):
                st.markdown(f'<div class="meta">{escape(cat)} <b style="float:right">{counts[cat]}</b></div><div class="bar-track"><div class="bar-fill" style="width:{100*counts[cat]/max(1,len(docs))}%;background:{color}"></div></div>', unsafe_allow_html=True)
            st.caption('Distribution by document count')
        st.button('Review organization plan →', use_container_width=True, on_click=go, args=('Organization plan',))
    st.subheader('Recently added')
    grid(sorted(docs, key=lambda d:d.imported_at, reverse=True)[:3], open_doc)
elif st.session_state.page in {'All files', 'Smart collections', 'Recently analyzed'}:
    page = st.session_state.page
    heading(page, 'A home for every useful idea. Open a document to read, edit, or analyze it.')
    a,b,c = st.columns([2,1,1])
    categories = ['All'] + CATEGORIES
    category = a.selectbox('Category', categories, key='collection_filter')
    status = b.selectbox('Analysis status', ['All', 'Pending', 'Demo', 'AI analyzed', 'Failed'])
    sort = c.selectbox('Sort by', ['Newest', 'Name', 'Category', 'File size'])
    filtered = [d for d in docs if (category == 'All' or d.category == category) and (status == 'All' or d.status == status) and (page != 'Recently analyzed' or d.analyzed_at)]
    filtered = sorted(filtered, key=lambda d: {'Newest': d.analyzed_at if page == 'Recently analyzed' else d.imported_at, 'Name':d.name.lower(), 'Category':d.category, 'File size':d.size}[sort], reverse=sort in {'Newest','File size'})
    st.caption(f'{len(filtered)} documents')
    if page == 'Smart collections':
        assigned = Counter(d.collection for d in docs if d.collection != 'Inbox')
        if assigned:
            with st.expander('Approved collection folders'):
                for collection, count in assigned.items():
                    st.write(f'{collection} · {count} documents')
        st.caption('Category views update after analysis. Approve the organization plan to assign in-app folders.')
    grid(filtered, open_doc)
    pending = [d for d in filtered if d.status in {'Pending','Failed'}]
    if pending:
        with st.expander(f'Analyze or retry {len(pending)} pending / failed documents'):
            analysis_controls(pending, 'batch')
elif st.session_state.page == 'Duplicate files':
    heading('One idea. A few too many copies.', 'Exact byte-for-byte matches, verified with SHA-256. Nothing is deleted or moved.')
    groups = duplicate_groups(docs)
    if not groups:
        st.success('No exact duplicates found in this workspace.')
    for i, group in enumerate(groups):
        with st.container(border=True):
            st.subheader(f'{len(group)} matching copies · {(len(group)-1)*group[0].size/1024:.1f} KB extra')
            st.caption('SHA-256: '+group[0].digest)
            for doc in group:
                a,b = st.columns([5,1])
                a.write(f'{doc.name} · {doc.size:,} bytes · {doc.source}')
                if b.button('Inspect', key='dup_'+doc.id):
                    open_doc(doc.id)
elif st.session_state.page == 'Organization plan':
    heading('Everything in its place.', 'Review suggested folders before applying. Approval changes collections inside this app only.')
    rows = plan(docs)
    if not rows:
        st.success('You’re all caught up. Analyze new documents to generate suggestions.')
    chosen = []
    for row in rows:
        with st.container(border=True):
            if st.checkbox(row['Original filename'], key='approve_'+row['id']):
                chosen.append(row['id'])
            st.caption(f"{row['Current location']} → {row['Proposed destination']} · {row['Analysis']}")
            st.write(row['Reason'])
    if rows:
        if st.button(f'Approve {len(chosen)} selected suggestions', disabled=not chosen, type='primary'):
            approve(docs, chosen)
            st.session_state.notice = f'Assigned {len(chosen)} documents to in-app collections.'
            st.rerun()
        st.download_button('Download proposed plan', json.dumps(rows, indent=2), 'clearspace-plan.json', 'application/json')
elif st.session_state.page == 'Add files':
    heading('Make room for a clearer workspace.', 'Drop in a few documents. We’ll extract their text locally on the app server, ready for you to explore.')
    st.caption('TXT, MD, text-based PDF · 10 MB/file · 100 PDF pages · 200,000 extracted characters · 100 documents/workspace')
    uploads = st.file_uploader('Drag documents here, or browse files', type=['txt','md','pdf'], accept_multiple_files=True, key='uploader_'+str(st.session_state.upload_version))
    if st.button('Import selected files', disabled=not uploads, type='primary'):
        progress = st.progress(0)
        errors, added = [], 0
        for i, file in enumerate(uploads):
            try:
                if len(docs) >= 100:
                    raise ValueError('Workspace limit reached (100 files). Start a new session or clear the workspace in Settings.')
                docs.append(read_file(file.name, file.getvalue()))
                added += 1
            except ValueError as exc:
                errors.append(f'{file.name}: {exc}')
            progress.progress((i+1)/len(uploads))
        st.session_state.import_errors = errors
        st.session_state.notice = f'Imported {added} documents. They are pending analysis; duplicate copies are kept for review.'
        st.session_state.upload_version += 1
        st.rerun()
    for error in st.session_state.get('import_errors', []):
        st.error(error)
    pending = [d for d in docs if d.status in {'Pending','Failed'}]
    if pending:
        st.subheader('Ready to understand your files?')
        selected_ids = st.multiselect('Select documents to analyze', [d.id for d in pending], default=[d.id for d in pending], format_func=lambda id:next(d.name for d in pending if d.id == id))
        analysis_controls([d for d in pending if d.id in selected_ids], 'imports')
    st.info('Original files stay where they are. Importing sends files to the machine hosting Streamlit; hosted AI receives text only when you approve analysis.')
elif st.session_state.page == 'Settings':
    heading('Your space, your preferences.', 'Keep the workflow simple. Configure provider credentials on the server in .env.')
    options = ['demo','digitalocean','snowflake']
    if st.session_state.mode not in options:
        st.error('Unknown AI_PROVIDER in .env. Select an available mode below.')
        st.session_state.mode = 'demo'
    st.selectbox('Analysis provider', options, key='mode')
    st.caption('Changing this setting does not re-analyze documents. Open a document to run the selected provider. No credentials are shown or stored in the browser.')
    st.subheader('Storage & privacy')
    st.write('This MVP stores extracted text and metadata only in your Streamlit session. A session reset or server restart can clear the workspace. Uploaded originals are not written to disk by this app.')
    st.write('Download your current index for a local record. It contains full extracted text; keep it private. Importing this JSON backup is not implemented in this version.')
    st.download_button('Download workspace index', json.dumps([d.to_dict() for d in docs], indent=2), 'clearspace-workspace.json', 'application/json')
    st.subheader('Repeat the demo')
    confirm = st.checkbox('I understand this replaces the current in-app workspace.')
    a,b = st.columns(2)
    if a.button('Reset to fictional sample files', disabled=not confirm):
        st.session_state.docs = load_demo()
        st.session_state.upload_version += 1
        st.session_state.import_errors = []
        st.rerun()
    if b.button('Start with an empty workspace', disabled=not confirm):
        st.session_state.docs = []
        st.session_state.upload_version += 1
        st.session_state.import_errors = []
        st.rerun()
