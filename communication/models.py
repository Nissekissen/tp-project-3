STATUS_QUEUED = 0
STATUS_IN_PROGRESS = 1
STATUS_COMPLETED = 2
STATUS_FAILED = 3

TYPE_ORDER = 0
TYPE_RESTOCK = 1
TYPE_CREATED = 2
TYPE_DELETED = 3

class QueueItem:
    def __init__(self, id, item_id, from_id, to_id, amount, position, status, _type) -> None:
        self.id = id
        self.item_id = item_id
        self.amount = amount
        self.status = status
    
    def __str__(self) -> str:
        return f"QueueItem: id={self.id}, item_id={self.item_id}, from_id={self.from_id}, to_id={self.to_id}, amount={self.amount}, status={self.status}, position={self.position}, type={self.type}"

class Item:
    def __init__(self, id, name, amount, cell_id) -> None:
        self.id = id
        self.name = name
        self.amount = amount
        self.cell_id = cell_id

class Cell:
    def __init__(self, id, x, y, z) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.z = z
    
    def to_bytes(self) -> bytes:
        return bytes([self.x, self.y, self.z])

class Instruction:
    def __init__(self, id, from_id, to_id) -> None:
        self.id = id
        self.from_id = from_id
        self.to_id = to_id
    
    def __str__(self) -> str:
        return f"Instruction: id={self.id}, from_id={self.from_id}, to_id={self.to_id}"
    
    def to_bytes(self) -> bytes:
        return bytes([self.from_id.to_bytes(), self.to_id.to_bytes()])