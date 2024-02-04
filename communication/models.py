class QueueItem:
    def __init__(self, id, item_id, to_id, amount, status, position) -> None:
        self.id = id
        self.item_id = item_id
        self.to_id = to_id
        self.amount = amount
        self.status = status
        self.position = position
    
    def __str__(self) -> str:
        return f"QueueItem: id={self.id}, item_id={self.item_id}, to_id={self.to_id}, amount={self.amount}, status={self.status}, position={self.position}"

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