from psycopg2.extras import RealDictCursor

STATUS_QUEUED = 0
STATUS_IN_PROGRESS = 1
STATUS_COMPLETED = 2
STATUS_FAILED = 3

TYPE_ORDER = 0
TYPE_RESTOCK = 1
TYPE_CREATED = 2
TYPE_DELETED = 3

class QueueItem:
    def __init__(self, id, item_id, amount, status, type, paused) -> None:
        self.id = id
        self.item_id = item_id
        self.amount = amount
        self.status = status
        self.type = type
        self.paused = paused # if the item is paused, the user will have to manually restart the queue item
    
    def __str__(self) -> str:
        return f"QueueItem: id={self.id}, item_id={self.item_id}, amount={self.amount}, status={self.status}, type={self.type}"

class Item:
    def __init__(self, id, name, amount, cell_id) -> None:
        self.id = id
        self.name = name
        self.amount = amount
        self.cell_id = cell_id

class Cell:
    def __init__(self, id, x, y, z, box) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.z = z
        self.box = box
    
    def __str__(self) -> str:
        return f"Cell: id={self.id}, x={self.x}, y={self.y}, z={self.z}"
    
    def to_bytes(self) -> bytes:
        # if x is 0 -> 100, if x is 1 -> 75 if x is 2 -> 50
        real_x = 0
        if self.x == 0:
            real_x = 100
        elif self.x == 1:
            real_x = 75
        elif self.x == 2:
            real_x = 50
        else:
            real_x = 0

        real_y = 0
        if self.y == 0:
            real_y = 100
        elif self.y == 1:
            real_y = 50
        elif self.y == 2:
            real_y = 0
        else:
            real_y = 100

        # if z is 0 -> 100, if z is 1 -> 75, if z ia 1 -> 60
        real_z = 0
        if self.z == 0:
            real_z = 100
        elif self.z == 1:
            real_z = 75
        elif self.z == 2:
            real_z = 60
        else:
            real_z = 100

        return_value = bytes([real_x, real_y, real_z])
        print(return_value)
        return return_value

class Instruction:
    def __init__(self, id, from_id, to_id, pause) -> None:
        self.id = id
        self.from_id = from_id
        self.to_id = to_id
        self.pause = pause
    
    def __str__(self) -> str:
        return f"Instruction: id={self.id}, from_id={self.from_id}, to_id={self.to_id} pause={self.pause}"
    
    def to_bytes(self, cursor: RealDictCursor) -> bytes:
        cursor.execute(f"SELECT * FROM cells WHERE id={self.from_id};")
        record = cursor.fetchone()
        from_cell = Cell(**record)

        cursor.execute(f"SELECT * FROM cells WHERE id={self.to_id};")
        record = cursor.fetchone()
        to_cell = Cell(**record)
        print(from_cell.to_bytes(), to_cell.to_bytes())
        return b''.join([from_cell.to_bytes(), to_cell.to_bytes()])