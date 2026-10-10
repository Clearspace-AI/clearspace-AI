import re

def folder_name(value):
    return re.sub(r'[^\w &-]', '', value).strip()[:80] or 'Uncategorized'

def plan(documents):
    return [{'id': d.id, 'Original filename': d.name, 'Current location': d.collection,
             'Suggested collection': d.suggested_collection, 'Proposed destination': f'Library/{folder_name(d.suggested_collection)}/{d.name}',
             'Reason': d.reason, 'Analysis': d.status}
            for d in documents if d.status in {'Demo', 'AI analyzed'} and d.suggested_collection and d.collection != d.suggested_collection]

def approve(documents, ids):
    for d in documents:
        if d.id in ids and d.status in {'Demo', 'AI analyzed'}:
            d.collection = d.suggested_collection
