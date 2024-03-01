import psycopg2
from psycopg2.extras import RealDictCursor
import models
import serial_comm
import time

OUTPUT_CELL_ID = 28
INPUT_CELL_ID = 29

def get_next_queue_item(conn: psycopg2.extensions.connection, cursor: RealDictCursor) -> models.QueueItem:
    cursor.execute(f"SELECT * FROM queue_items WHERE status < 2 ORDER BY id ASC LIMIT 1;")
    record = cursor.fetchone()
    if record:
        queue_item = models.QueueItem(**record)
        return queue_item
    else:
        return None

def get_next_instruction(conn: psycopg2.extensions.connection, cursor: RealDictCursor) -> models.Instruction:

    cursor.execute(f'SELECT * FROM instructions ORDER BY id ASC LIMIT 1;')
    record = cursor.fetchone();

    if record:
        instruction = models.Instruction(**record)
        return instruction
    else:
        return None

def get_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor):

    cursor.execute(f'SELECT * FROM instructions ORDER BY id ASC;')
    records = cursor.fetchall()

    if not records:
        return []
    
    return [models.Instruction(**record) for record in records]

def add_instruction(conn: psycopg2.extensions.connection, cursor: RealDictCursor, from_id, to_id, paused=False) -> models.Instruction:
    cursor.execute(f"INSERT INTO instructions (from_id, to_id, pause) VALUES ({from_id}, {to_id}, {paused}); SELECT * FROM instructions ORDER BY id DESC LIMIT 1;")
    conn.commit()
    record = cursor.fetchone()

    if record is None:
        return None

    return models.Instruction(**record)

def order_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor, queue_item: models.QueueItem):
    instructions = []

    # Get the cell of the item
    cursor.execute(f'SELECT * FROM items WHERE id={queue_item.item_id};')
    record = cursor.fetchone()
    item = models.Item(**record)


    cursor.execute(f'SELECT * FROM cells WHERE id={item.cell_id};')
    record = cursor.fetchone()
    from_cell = models.Cell(**record)

    cursor.execute(f'SELECT * FROM cells WHERE id={OUTPUT_CELL_ID};')
    record = cursor.fetchone()
    to_cell = models.Cell(**record)

    # get all the cells in the same x and y as the from_cell
    cursor.execute(f'SELECT * FROM cells WHERE x={from_cell.x} AND y={from_cell.y} AND z > {from_cell.z} ORDER BY z DESC;')
    records = cursor.fetchall()
    cells = [models.Cell(**record) for record in records]

    temp_instructions = []

    for cell in cells:
        # check if there is a box in the cell (if the cell has the property box set to true)
        if not cell.box:
            continue

        # Find a cell to move the box to
        found_cell = bfs_search(conn, cursor, cell)

        print(found_cell.x, found_cell.y, found_cell.z)

        instruction = add_instruction(conn, cursor, cell.id, found_cell.id)
        instructions.append(instruction)
        temp_instructions.append(instruction)
    
    # Add the instruction to actually move the right box
    instruction = add_instruction(conn, cursor, from_cell.id, to_cell.id, True)
    instructions.append(instruction)

    # Add the instructions to move the boxes back (except for the last one)

    # for i in range(len(instructions) - 1, -1, -1):
    #     instruction = add_instruction(conn, cursor, instructions[i].to_id, instructions[i].from_id)
    #     instructions.append(instruction)
    instructions.append(add_instruction(conn, cursor, to_cell.id, from_cell.id, False))

    for i in range(len(temp_instructions) - 1, -1, -1):
        instruction = add_instruction(conn, cursor, temp_instructions[i].to_id, temp_instructions[i].from_id)
        instructions.append(instruction)
    

    return instructions

def restock_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor, queue_item: models.QueueItem):
    '''
    This function takes in a queue item of type restock and turns it into a series of instructions.
    The instructions are to move the box from the restock location to the correct location.
    Should be the same as order_to_instructions
    '''

    return order_to_instructions(conn, cursor, queue_item)

def created_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor, queue_item: models.QueueItem):
    '''
    This function takes in a queue item of type created and turns it into a series of instructions.
    The instructions are to find an empty cell, set the cell_id of the item to that cell, move the box in that cell
    to the output cell, then move it back to an empty spot.
    '''

    # Find an empty cell with no empty cells beneath it.

    instructions = []

    cursor.execute(f'SELECT * FROM cells;')
    records = cursor.fetchall()
    cells = [models.Cell(**record) for record in records]
    found_cell = None

    # sort cells into 3 dimensional array where the first index is the x, the second is the y and the third is the z
    sorted_cells = [[[] for _ in range(3)] for _ in range(3)]
    # print(sorted_cells[0][0])
    for cell in cells:
        if cell.x == 3: #output box
            continue 
        # print(cell.x, cell.y, cell.z)

        sorted_cells[cell.x][cell.y].append(cell)
    
    for x in range(3):
        for y in range(3):
            for z in range(3):
                # get the first empty cell from the bottom
                # check if there is an item in the cell
                
                cursor.execute(f'SELECT * FROM items WHERE cell_id={sorted_cells[x][y][z].id};')
                record = cursor.fetchone()
                
                if record is None and sorted_cells[x][y][z].box: 
                    # there is no item in the cell and there is a box there, found!
                    print("Found cell:", sorted_cells[x][y][z])
                    found_cell = sorted_cells[x][y][z]
                    break
            
            if found_cell != None:
                break
        if found_cell != None:
            break

    cursor.execute(f'UPDATE items SET cell_id={found_cell.id} WHERE id={queue_item.item_id};')
    conn.commit()

    # 

    # sample queue_item
    queue_item = models.QueueItem(0, queue_item.item_id, 0, models.STATUS_QUEUED, models.TYPE_ORDER, False)
    return order_to_instructions(conn, cursor, queue_item)

def deleted_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor, queue_item: models.QueueItem):
    '''
    This function takes in a queue item of type deleted and turns it into a series of instructions.
    The instructions are to move the box from the cell to the output cell, then move it back to an empty spot.
    It should also delete the item from the database.
    '''

    cursor.execute(f'DELETE FROM items WHERE id={queue_item.item_id};')
    conn.commit()

    return order_to_instructions(conn, cursor, queue_item)
    pass

def queue_to_instructions(conn: psycopg2.extensions.connection, cursor: RealDictCursor):
    '''
    Basically the brain of this program. It takes in a queue item and turns it into a series of instructions.
    The problem, or the "hard" part of this, is that there might be boxes above the box that we want to pick up.
    Therefore, the program needs to check all the other boxes in the pile and move them (generate instructions) for
    them before moving the box we want to pick up.

    '''

    queue_item = get_next_queue_item(conn, cursor)

    if queue_item is None:
        return []

    if queue_item.status >= models.STATUS_IN_PROGRESS:
        return []
    
    if queue_item.type == models.TYPE_ORDER:
        return order_to_instructions(conn, cursor, queue_item)
    elif queue_item.type == models.TYPE_RESTOCK:
        return restock_to_instructions(conn, cursor, queue_item)
    elif queue_item.type == models.TYPE_CREATED:
        return created_to_instructions(conn, cursor, queue_item)
    elif queue_item.type == models.TYPE_DELETED:
        return deleted_to_instructions(conn, cursor, queue_item)
    
    
            
def bfs_search(conn: psycopg2.extensions.connection, cursor: RealDictCursor, cell: models.Cell) -> models.Cell:
    """
    Perform a breadth-first search (BFS) to find a cell to move the box to.

    Args:
        conn (psycopg2.extensions.connection): The database connection.
        cursor (RealDictCursor): The database cursor.
        cell (models.Cell): The current cell.

    Returns:
        models.Cell: The found cell to move the box to, or None if no cell is found.
    """
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
                # Since we only move to the 3rd level, we can just check if that cell is empty
                cursor.execute(f'SELECT * FROM cells WHERE x={nx} AND y={ny} AND z=2;')
                record = cursor.fetchone()
                nearby_cell = models.Cell(**record)

                if not nearby_cell.box:
                    found_cell = nearby_cell
                    found = True
                    break

                if not found_cell:
                    # Enqueue the cell for the next level of BFS
                    queue.append((nx, ny))

            if found:
                break
        
    return found_cell

def loop(conn: psycopg2.extensions.connection, cursor: RealDictCursor):

    serial_conn = serial_comm.SerialComm('COM8', 9600)

    paused = False
    queue_item = None

    while True:
        
        next_instruction = get_next_instruction(conn, cursor)
        if next_instruction is None:
            print("No instructions")
            # there are no instructions, get next queue item
            queue_to_instructions(conn, cursor)
            queue_item = get_next_queue_item(conn, cursor)

            if queue_item is None:
                print("No queue items")
                time.sleep(1)
                continue

            # if the queue item has status 1, it has already been processed and can be skipped
            if queue_item.status == 1:
                print("Queue item already processed, skipping")
                # set the status to 2 and continue
                cursor.execute(f"UPDATE queue_items SET status=2 WHERE id={queue_item.id};")
                # cursor.execute(f"DELETE FROM instructions WHERE id={next_instruction.id};")
                # delete all instructions
                cursor.execute(f"DELETE FROM instructions;")
                conn.commit()
                continue
            elif queue_item.status == 2:
                print("Queue item already processed, deleting")
                # delete the queue item
                cursor.execute(f"DELETE FROM queue_items WHERE id={queue_item.id};")
                conn.commit()
                continue

            cursor.execute(f"UPDATE queue_items SET status=1 WHERE id={queue_item.id};")
            conn.commit()
            continue
        
        if paused:
            # the last instruction was a pause, wait for the pause to be over
            # To find out if the pause is over or not, we need to check the "paused" column in the next queue_item
            cursor.execute("SELECT * FROM queue_items ORDER BY id ASC LIMIT 1;")
            record = cursor.fetchone()
            queue_item = models.QueueItem(**record)

            print("Paused!", queue_item)
            if queue_item is None:
                print("Paused and no queue item?")
                time.sleep(1)
                continue

            if queue_item.paused:
                print("Paused and the current queue item is paused, waiting for resume")
                time.sleep(1)
                continue

            paused = False
        
        print("Next Instruction:", next_instruction)

        if next_instruction.pause:
            # the instruction is a pause, set the paused variable to True and continue
            paused = True

            # update the queue_item to paused
            cursor.execute(f"UPDATE queue_items SET paused=True WHERE id=(SELECT id FROM queue_items ORDER BY id ASC LIMIT 1);")
            conn.commit()

        # serial_conn.send(next_instruction.to_bytes())
        # print("Sending to serial:", str(next_instruction.to_bytes(cursor)))
        serial_conn.send_instruction(next_instruction, cursor)
        cursor.execute(f"DELETE FROM instructions WHERE id={next_instruction.id};")
        conn.commit()

        # wait until the arduino sends "Done!" back
        while True:
            data = serial_conn.read()
            if data != b'':
                print(data)
            if data == b'Done!\r\n':
                break
            time.sleep(1)
        time.sleep(1)

def add_cells(conn: psycopg2.extensions.connection, cursor: RealDictCursor):
    cursor.execute("TRUNCATE TABLE cells;")
    for x in range(3):
        for y in range(3):
            for z in range(3):
                cursor.execute(f"INSERT INTO cells (x, y, z) VALUES ({x}, {y}, {z});")
    conn.commit()