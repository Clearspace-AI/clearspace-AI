from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from uuid import uuid4

CATEGORIES = ['Study & Research', 'Work & Projects', 'Personal', 'Finance & Administration', 'Reference & Reading', 'Uncategorized']

@dataclass
class Document:
    name: str
    text: str
    size: int
    digest: str
    kind: str
    id: str = field(default_factory=lambda: uuid4().hex)
    imported_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    category: str = 'Uncategorized'
    summary: str = ''
    keywords: list[str] = field(default_factory=list)
    suggested_collection: str = ''
    reason: str = ''
    collection: str = 'Inbox'
    status: str = 'Pending'
    source: str = 'Upload'
    analyzed_at: str = ''
    error: str = ''
    edited: bool = False

    def to_dict(self):
        return asdict(self)
