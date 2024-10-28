from typing import Callable, List, Optional
from dataclasses import dataclass


@dataclass
class Record:
    id: Optional[int]
    title: str
    content: str
    type: str
    similarity: Optional[float]
    importance: int


class VectorStore:
    name: str
    query_store: Callable[[str], List[Record]]
    add_record: Callable[[Record], None]
    on_init: Callable[[], None]

    def __init__(
        self,
        name: str,
        query_store: Callable[[str], List[Record]],
        add_record: Callable[[Record], None],
        on_init: Optional[Callable[[], None]] = None,
    ) -> None:
        self.name = name
        self.query_store = query_store
        self.add_record = add_record
        if on_init:
            self.on_init = on_init

        self.on_init()

    def query(self, query: str) -> List[Record]:
        return self.query_store(query)

    def add(self, record: Record) -> None:
        self.add_record(record)
