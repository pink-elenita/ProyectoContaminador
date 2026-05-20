import sqlite3
import hashlib
import os

# Guarda la BD en Documentos del usuario para que nunca se pierda
BASE_DIR = os.path.join(os.path.expanduser("~"), "Documents", "ProyectoContaminador")
os.makedirs(BASE_DIR, exist_ok=True)
DB = os.path.join(BASE_DIR, "usuarios.db")


def _hash(password):
    """Convierte la contraseña en un hash seguro para no guardarla en texto plano."""
    return hashlib.sha256(password.encode()).hexdigest()


def inicializar():
    """Crea las tablas de la base de datos si no existen e inserta los usuarios predeterminados."""
    with sqlite3.connect(DB) as con:
        # Crea la tabla de usuarios si no existe
        con.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password TEXT NOT NULL
            )
        """)
        # Crea la tabla de actividades si no existe
        con.execute("""
            CREATE TABLE IF NOT EXISTS actividades (
                id       INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                tipo     TEXT NOT NULL,
                nombre   TEXT NOT NULL,
                cantidad REAL NOT NULL,
                fecha    TEXT NOT NULL,
                FOREIGN KEY (username) REFERENCES usuarios(username)
            )
        """)
        # Inserta usuarios predeterminados si no existen
        for user, pwd in [("admin", "1234"), ("elena", "pass"), ("fer", "123")]:
            con.execute("INSERT OR IGNORE INTO usuarios VALUES (?, ?)",
                        (user, _hash(pwd)))
        con.commit()


def validar(username, password):
    """Conecta los usuarios y contraseñas con la base de datos y verifica que coincidan."""
    with sqlite3.connect(DB) as con:
        row = con.execute(
            "SELECT 1 FROM usuarios WHERE username=? AND password=?",
            (username, _hash(password))
        ).fetchone()
    return row is not None


def registrar(username, password):
    """Registra un usuario nuevo en la base de datos.
    Devuelve True si se creó correctamente, False si el usuario ya existe."""
    try:
        with sqlite3.connect(DB) as con:
            con.execute("INSERT INTO usuarios VALUES (?, ?)",
                        (username, _hash(password)))
            con.commit()
        return True
    except sqlite3.IntegrityError:
        return False


def guardar_actividad(username, actividad):
    """Guarda las actividades registradas permanentemente en la base de datos."""
    with sqlite3.connect(DB) as con:
        cur = con.execute(
            "INSERT INTO actividades (username, tipo, nombre, cantidad, fecha) VALUES (?,?,?,?,?)",
            (username, actividad.tipo(), actividad.nombre, actividad.cantidad, actividad.fecha)
        )
        con.commit()
        return cur.lastrowid


def eliminar_actividad(id_actividad):
    """Elimina las actividades de la base de datos de forma permanente."""
    with sqlite3.connect(DB) as con:
        con.execute("DELETE FROM actividades WHERE id=?", (id_actividad,))
        con.commit()


def cargar_actividades(username):
    """Carga todas las actividades del usuario desde la base de datos al iniciar sesión."""
    with sqlite3.connect(DB) as con:
        rows = con.execute(
            "SELECT id, tipo, nombre, cantidad, fecha FROM actividades WHERE username=?",
            (username,)
        ).fetchall()
    return rows