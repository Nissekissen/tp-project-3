import psycopg2, os, time
from psycopg2.extras import RealDictCursor
# from dotenv import load_dotenv
import models, instructions
# from serial_comm import SerialComm



# load_dotenv()

# Global variables


cursor = None
conn = None

def connect():
    global cursor, conn
    conn = psycopg2.connect(
        database = "robotlager",
        user = "postgres",
        password = "postgres",
        host = 'localhost',
        port = 5432
    )
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    cursor.execute("SELECT version();")
    record = cursor.fetchone()
    # print("You are connected to - ", record, "\n")

try:
    connect()
except (Exception, psycopg2.Error) as error:
    print("Error while connecting to PostgreSQL", error)
    exit()


# # Get next queue item and send it off to the robot
# queue_item = get_next_queue_item()

# serial = SerialComm('COM4', 115200)

# if queue_item is not None:
#     print("Sending off queue item", queue_item.id)
#     # Send off to the robot
#     from_cell = get_cell_from_id(queue_item.from_id)
#     to_cell = get_cell_from_id(queue_item.to_id)

#     serial.send(f"{from_cell.x},{from_cell.y},{from_cell.z},{to_cell.x},{to_cell.y},{to_cell.z}".encode())

#     # Update the queue item status to 'In Progress'
#     cursor.execute(f"UPDATE queue_items SET status='In Progress' WHERE id={queue_item.id};")
#     conn.commit()

# print(get_next_instruction(conn, cursor))
# instructions.add_cells(conn, cursor)

# import serial_comm

# serial_conn = serial_comm.SerialComm('COM8', 9600)

# serial_conn.send(f'{from_cell.to_bytes()}{to_cell.to_bytes()}\n')
# cell = models.Cell(1, 3, 3, 3)
# print([ord(x) for x in cell.to_bytes()])
instructions.loop(conn, cursor)