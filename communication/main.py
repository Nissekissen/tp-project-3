import psycopg2, os, time
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import models

load_dotenv()

# Global variables
OUTPUT_CELL_ID = 1
INPUT_CELL_ID = 2

cursor = None

def connect():
    global cursor
    conn = psycopg2.connect(
        database = os.getenv("DB_NAME"),
        user = os.getenv("DB_USER"),
        password = os.getenv("DB_PASSWORD"),
        host = 'db',
        port = 5432
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    # print("You are connected to - ", record, "\n")

def cell_to_byte(cell: models.Cell):
    # format: 00XXYYZZ wherex, y and z are from 0-3
    return int('{0:08b}'.format((cell.x << 4) + (cell.y << 2) + (cell.z)), 2)

def get_queue_items() -> [models.QueueItem]:
    global cursor
    cursor.execute("SELECT * FROM queue_items;")
    records = cursor.fetchall()

    queue_items = []

    for record in records:
        queue_items.append(models.QueueItem(record['id'], record['item_id'], record['from_id'], record['to_id'], record['amount'], int(record['position']), record['status'], record['type']))

    return queue_items

def get_next_queue_item() -> models.QueueItem:
    global cursor
    cursor.execute("SELECT * FROM queue_items WHERE type='transfer' ORDER BY position ASC LIMIT 1;")

    record = cursor.fetchone()

    # print(record)

    if record is None:
        return None
    
    return models.QueueItem(record['id'], record['item_id'], record['from_id'], record['to_id'], record['amount'], int(record['position']), record['status'], record['type'])

def get_items() -> [models.Item]:
    global cursor
    cursor.execute("SELECT * FROM items;")
    records = cursor.fetchall()

    items = []

    for record in records:
        items.append(models.Item(record['id'], record['name'], record['amount'], record['cell_id']))
    
    # print("shit", items)

    return items

def get_item_from_id(id):
    global cursor
    cursor.execute(f"SELECT * FROM items WHERE id={id};")
    record = cursor.fetchone()

    return models.Item(record['id'], record['name'], record['amount'], record['cell_id'])

def get_cell_from_id(id):
    global cursor
    cursor.execute(f"SELECT * FROM cells WHERE id={id};")
    record = cursor.fetchone()

    # print("shit", record)
    return models.Cell(record['id'], record['x'], record['y'], record['z'])

def add_item_to_queue(item_id: int, from_id: int, to_id: int, amount: int, status: str, position: int, _type: str):
    
    cursor.execute(f"INSERT INTO queue_items (item_id, from_id, to_id, amount, status, position, type) VALUES ({item_id}, {from_id}, {to_id}, {amount}, '{status}', {position}, '{_type}')")
    


try:
    connect()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    exit()

queue_items: [models.QueueItem] = get_queue_items()

# print(queue_items[0])
# print(queue_items[1])

print(queue_items)



for queue_item in queue_items:

    print(queue_item)

    # Generate the from and to cells from item_id
    item = get_item_from_id(queue_item.item_id)
    # print("what? ", item.cell_id)

    from_cell = get_cell_from_id(item.cell_id)
    # To cell is the output box
    to_cell = get_cell_from_id(OUTPUT_CELL_ID)

    # Create new queue item with the same item_id, but the new from_id, to_id and status
    add_item_to_queue(int(item.id), int(from_cell.id), int(to_cell.id), int(item.amount), 'queued', 0, 'transfer')


queue_items: [models.QueueItem] = get_queue_items()

print(len(queue_items))
