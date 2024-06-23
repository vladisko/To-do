import sqlite3
from rich import print
from rich.tree import Tree
from re import fullmatch

import os

connection = sqlite3.connect('tasks.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Tasks (
name TEXT,
runtime TEXT
)
''')


def create(name: str, runtime: str = '') -> None:
    cursor.execute(
        'INSERT INTO Tasks (name, runtime) VALUES (?, ?)', (name, runtime,))
    connection.commit()


def delete(index: int) -> None:
    cursor.execute(f'''
    SELECT EXISTS(SELECT 1 FROM Tasks WHERE rowid = ?)
    ''', (index,))

    if cursor.fetchone()[0]:
        cursor.execute(f'''
        DELETE FROM Tasks
        WHERE rowid = ?
        ''', (index,))
        connection.commit()
    else:
        print('Invalid row_id')


def edit(index: int, name: str = '', runtime: str = '') -> None:
    if name and runtime:
        cursor.execute('UPDATE Tasks SET name = ?, runtime = ? WHERE rowid = ?',
                       (name, runtime, index,))
        connection.commit()
        return

    if name:
        cursor.execute('UPDATE Tasks SET name = ? WHERE rowid = ?',
                       (name, index,))
        connection.commit()
        return

    cursor.execute('UPDATE Tasks SET runtime = ? WHERE rowid = ?',
                   (runtime, index,))
    connection.commit()


def is_db_empty() -> bool:
    cursor.execute(f'''
    SELECT * FROM Tasks
    ''')

    if cursor.fetchone() is None:
        print("There's nothing here.")
        return True

    return False


def tasks() -> None:
    cursor.execute(f'''
    SELECT rowid, name, runtime FROM Tasks
    ''')

    tree = Tree('[slate_blue1]TASKS')

    for row in cursor.fetchall():
        row_id, name, runtime = row[0], row[1], row[2]

        tree.add(
            f'{row_id}. [dark_khaki]{name} [dark_sea_green]{runtime}\n')

    print(tree)


while True:
    command = input()
    os.system('cls')
    cmd = command.split(' ', 1)[0]

    match cmd:
        case 'task':
            if len(command.split(' ')[1:]) >= 2:
                *name, runtime = command.split(' ')[1:]

                if fullmatch(r'\d{2}:\d{2}', runtime):
                    name = ' '.join(name)

                    create(name, runtime)

                    continue

            if len(command.split(' ', 1)[1:]) >= 1:
                create(name=command.split(' ', 1)[1])

        case 'delete':
            if is_db_empty():
                continue

            if len(command.split(' ', 1)) == 2:
                delete(index=command.split(' ', 1)[1])

        case 'edit':
            if len(command.split(' ')[1:]) >= 3:
                row_id, *name, runtime = command.split(' ')[1:]

                if fullmatch(r'\d{2}:\d{2}', runtime):
                    name = ' '.join(name)

                    edit(row_id, name, runtime)

                    continue

            if len(command.split(' ')[1:]) >= 2:
                values = command.split(' ', 2)

                if fullmatch(r'\d{2}:\d{2}', values[2]):
                    edit(index=values[1], runtime=values[2])
                    continue

                edit(index=values[1], name=values[2])

        case 'tasks':
            if is_db_empty():
                continue

            tasks()
