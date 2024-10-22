from typing import Callable, List, Optional
from dataclasses import dataclass


@dataclass
class Record:
    id: int
    title: str
    content: str
    similarity: float
    importance: int


class VectorStore:
    query_store: Callable[[str], List[Record]]
    add_record: Callable[[Record], None]
    on_init: Callable[[], None]

    def __init__(
        self,
        query_store: Callable[[str], List[Record]],
        add_record: Callable[[Record], None],
        on_init: Optional[Callable[[], None]] = None,
    ) -> None:
        self.query_store = query_store
        self.add_record = add_record
        if on_init:
            self.on_init = on_init
