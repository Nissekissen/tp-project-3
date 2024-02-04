import psycopg2, os, time
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import models

load_dotenv()

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
    print("You are connected to - ", record, "\n")

def cell_to_byte(cell: models.Cell):
    # format: 00XXYYZZ wherex, y and z are from 0-3
    return int('{0:08b}'.format((cell.x << 4) + (cell.y << 2) + (cell.z)), 2)

def get_queue_items():
    global cursor
    cursor.execute("SELECT * FROM queue_items;")
    records = cursor.fetchall()

    queue_items = []

    for record in records:
        queue_items.append(models.QueueItem(record['id'], record['item_id'], record['to_id'], record['amount'], record['status'], int(record['position'])))
    
    print(queue_items)

    return queue_items

def get_items():
    global cursor
    cursor.execute("SELECT * FROM items;")
    records = cursor.fetchall()

    items = []

    for record in records:
        items.append(models.Item(record['id'], record['name'], record['amount'], record['cell_id']))
    
    print(items)

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

    return models.Cell(record['id'], record['x'], record['y'], record['z'])

try:
    connect()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    exit()

queue_items = get_queue_items()
print(type(queue_items[0].position))
queue_items.sort(key=lambda x: x.position)
print(bin(cell_to_byte(cell=models.Cell(0, 1, 2, 3))))