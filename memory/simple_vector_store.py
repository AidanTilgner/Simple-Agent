import os
from typing import List
from memory.vector_store import VectorStore, Record

svs_url = ""

test_records = [
    Record(
        id=1,
        title="Test Record 1",
        content="This is the content of test record 1.",
        similarity=0.9,
        importance=1,
    ),
    Record(
        id=2,
        title="Test Record 2",
        content="This is the content of test record 2.",
        similarity=0.8,
        importance=2,
    ),
]


def query_simple_vector_store(query: str) -> List[Record]:
    return test_records


def add_simple_vector_store_record(record: Record) -> None:
    test_records.append(record)


def on_svs_init():
    global svs_url

    svs_url = os.environ.get("SVS_URL", "")
    if not svs_url:
        raise ValueError("SVS_URL not set")


SVSVectorStore = VectorStore(
    query_store=query_simple_vector_store,
    add_record=add_simple_vector_store_record,
    on_init=on_svs_init,
)
