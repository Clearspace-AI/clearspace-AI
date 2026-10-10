from collections import defaultdict

def duplicate_groups(documents):
    groups = defaultdict(list)
    for doc in documents:
        groups[doc.digest].append(doc)
    return [group for group in groups.values() if len(group) > 1]
