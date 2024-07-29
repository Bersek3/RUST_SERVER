import sqlite3

# Nombre del archivo de la base de datos
DB_PATH = 'data.db'

# Conectar a la base de datos (se creará si no existe)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Crear una tabla para almacenar el último tiempo de comprobación
cursor.execute('''
    CREATE TABLE IF NOT EXISTS last_checked (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL
    )
''')

# Insertar un registro inicial (opcional, si es necesario)
cursor.execute('''
    INSERT INTO last_checked (timestamp) VALUES ('1970-01-01T00:00:00Z')
''')

# Guardar los cambios y cerrar la conexión
conn.commit()
conn.close()
