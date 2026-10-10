import re
STOP = set('find my me about which document documents discusses show the a an with notes imported of for and in to is does please i'.split())

def search(documents, query):
    terms = [t for t in re.findall(r'\w+', query.lower()) if t not in STOP]
    results = []
    for doc in documents:
        fields = {'Filename': doc.name, 'Category': doc.category, 'Keywords': ' '.join(doc.keywords), 'Summary': doc.summary, 'Text': doc.text}
        matched = {term for term in terms if any(term in value.lower() for value in fields.values())}
        if terms and len(matched) != len(set(terms)):
            continue
        reason, score = '', 0
        for field, value in fields.items():
            hits = [t for t in terms if t in value.lower()]
            if hits:
                score += len(hits) * (3 if field in {'Filename', 'Keywords'} else 1)
                if not reason:
                    index = value.lower().find(hits[0])
                    reason = f'{field}: …{value[max(0,index-35):index+140]}…'
        results.append((doc, reason, score))
    return sorted(results, key=lambda r: r[2], reverse=True)
