import psycopg2
from psycopg2.extras import RealDictCursor
import models
import serial_comm
import time

def get_next_instruction(conn: psycopg2.extensions.connection, cursor: RealDictCursor) -> models.Instruction:

    cursor.execute(f'SELECT * FROM instructions ORDER BY id ASC LIMIT 1;')
    record = cursor.fetchone();

    if record:
        instruction = models.Instruction(**record)
        return instruction
    else:
        return None

def get_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor) -> [models.Instruction]:

    cursor.execute(f'SELECT * FROM instructions ORDER BY id ASC;')
    records = cursor.fetchall()

    if not records:
        return []
    
    return [models.Instruction(**record) for record in records]

def add_instruction(conn: psycopg2.extensions.connection, cursor: RealDictCursor, from_id, to_id) -> models.Instruction:
    cursor.execute(f"INSERT INTO instructions (from_id, to_id) VALUES ({from_id}, {to_id}); SELECT * FROM instructions ORDER BY id DESC LIMIT 1;")
    conn.commit()
    record = cursor.fetchone()

def queue_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor) -> [models.Instruction]:
    '''
    Basically the brain of this program. It takes in a queue item and turns it into a series of instructions.
    The problem, or the "hard" part of this, is that there might be boxes above the box that we want to pick up.
    Therefore, the program needs to check all the other boxes in the pile and move them (generate instructions) for
    them before moving the box we want to pick up.

    '''

    queue_item = get_next_queue_item(conn, cursor)

    if queue_item is None:
        return []
    
    instructions = []

    # Get the cell of the queue item
    cursor.execute(f'SELECT * FROM cells WHERE id={queue_item.from_id};')
    record = cursor.fetchone()
    from_cell = models.Cell(**record)

    cursor.execute(f'SELECT * FROM cells WHERE id={queue_item.to_id};')
    record = cursor.fetchone()
    to_cell = models.Cell(**record)

    # get all the cells in the same x and y as the from_cell
    cursor.execute(f'SELECT * FROM cells WHERE x={from_cell.x} AND y={from_cell.y}; AND z != {from_cell.z} ORDER BY z DESC;')
    records = cursor.fetchall()
    cells = [models.Cell(**record) for record in records]

    for cell in cells:
        # check if there is a box in the cell (if there is an item with that cell_id)
        cursor.execute(f'SELECT * FROM items WHERE cell_id={cell.id};')
        record = cursor.fetchone()

        if not record:
            continue

        # Find a cell to move the box to
        found_cell = bfs_search(conn, cursor, cell)

        instruction = add_instruction(conn, cursor, cell.id, found_cell.id)
        instructions.append(instruction)
    
    # Add the instruction to actually move the right box
    instruction = add_instruction(conn, cursor, from_cell.id, to_cell.id)
    instructions.append(instruction)

    # Add the instructions to move the boxes back (except for the last one)

    for i in range(len(instructions) - 1, -1, -1):
        instruction = add_instruction(conn, cursor, instructions[i].to_id, instructions[i].from_id)
        instructions.append(instruction)

    return instructions
            
def bfs_search(conn: psycopg2.extensions.connection, cursor: RealDictCursor, cell: models.Cell) -> models.Cell:
    # Find a cell to move the box to
    found = False
    queue = [(cell.x, cell.y)]  # Start BFS from the current cell
    visited = set()  # Keep track of visited cells to avoid cycles

    found_cell = None

    while queue and not found_cell:
        x, y = queue.pop(0)  # Dequeue a cell
        visited.add((x, y))  # Mark the cell as visited

        # Check all the nearby cells (x + 1, x - 1, y + 1, y - 1)
        for dx, dy in [(1, 0), (-1, 0), (0, 1), (0, -1)]:
            nx, ny = x + dx, y + dy

            # Check if the cell is valid and has not been visited yet
            if (nx, ny) not in visited:
                cursor.execute(f'SELECT * FROM cells WHERE x={nx} AND y={ny} ORDER BY Z DESC;')
                records = cursor.fetchall()
                nearby_cells = [models.Cell(**record) for record in records]

                for nearby_cell in nearby_cells:
                    cursor.execute(f'SELECT * FROM items WHERE cell_id={nearby_cell.id};')
                    record = cursor.fetchone()

                    if record is None:
                        found_cell = nearby_cell
                        break

                if not found_cell:
                    # Enqueue the cell for the next level of BFS
                    queue.append((nx, ny))

            if found:
                break
        
    return found_cell

def loop(conn: psycopg2.extensions.connection, cursor: RealDictCursor):

    serial_conn = serial_comm.SerialComm('COM5', 9600)

    while True:
        status = serial_conn.get_status()

        if status != b'0': # Waiting
            continue
        
        next_instruction = get_next_instruction(conn, cursor)
        if next_instruction is None:
            # there are no instructions, get next queue item
            queue_to_instructions(conn, cursor)
            cursor.execute(f"SELECT * FROM queue_items ORDER BY position ASC LIMIT 1;");
            record = cursor.fetchone()
            queue_item = models.QueueItem(**record)

            cursor.execute(f"UPDATE queue_items SET status=1 WHERE id={queue_item.id};")
            continue

        serial_conn.send(next_instruction.to_bytes())
        cursor.execute(f"DELETE FROM instructions WHERE id={next_instruction.id};")

        time.sleep(1)

def add_cells(conn: psycopg2.extensions.connection, cursor: RealDictCursor):
    cursor.execute("TRUNCATE TABLE cells;")
    for x in range(5):
        for y in range(5):
            for z in range(3):
                cursor.execute(f"INSERT INTO cells (x, y, z) VALUES ({x}, {y}, {z});")
    conn.commit()