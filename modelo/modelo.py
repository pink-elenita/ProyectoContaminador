from abc import ABC, abstractmethod
from datetime import date
import base_datos as bd


class Actividad(ABC):
    """Clase abstracta base para todas las actividades de huella de carbono.
    Define la estructura común que deben seguir Transporte, Energia y Alimentacion."""

    def __init__(self, nombre, cantidad, fecha=None, id_db=None):
        # Atributos privados con encapsulamiento — solo accesibles con getters/setters
        self._nombre   = nombre
        self._cantidad = cantidad
        self._fecha    = fecha or date.today().strftime("%d/%m/%Y")
        self._id_db    = id_db

    # ── Getters ──────────────────────────────────────────────
    @property
    def nombre(self):
        return self._nombre

    @property
    def cantidad(self):
        return self._cantidad

    @property
    def fecha(self):
        return self._fecha

    @property
    def id_db(self):
        """Retorna el ID en la base de datos."""
        return self._id_db

    # ── Setters ──────────────────────────────────────────────
    @nombre.setter
    def nombre(self, valor):
        """Establece el nombre validando que no esté vacío."""
        if not valor or not valor.strip():
            raise ValueError("El nombre no puede estar vacío")
        self._nombre = valor.strip()

    @cantidad.setter
    def cantidad(self, valor):
        """Establece la cantidad validando que sea positiva."""
        if valor <= 0:
            raise ValueError("La cantidad debe ser mayor a 0")
        self._cantidad = valor

    @fecha.setter
    def fecha(self, valor):
        """Establece la fecha de la actividad."""
        self._fecha = valor

    @id_db.setter
    def id_db(self, valor):
        """Establece el ID en la base de datos."""
        self._id_db = valor

    # ── Métodos abstractos ───────────────────────────────────
    @abstractmethod
    def calcular_co2(self):
        """Calcula el CO₂ generado según el tipo de actividad.
        Cada clase hija implementa su propio factor de emisión."""
        pass

    @abstractmethod
    def tipo(self):
        """Retorna el tipo de actividad como string."""
        pass

    def __str__(self):
        """Representación legible de la actividad."""
        return f"{self.tipo().capitalize()} | {self._nombre} | {self._cantidad} | {self._fecha} | {self.calcular_co2():.2f} kg CO₂"


class Transporte(Actividad):
    """Actividad de transporte. Factor de emisión: 0.21 kg CO₂ por km."""

    def __init__(self, nombre, cantidad, fecha=None, id_db=None):
        super().__init__(nombre, cantidad, fecha, id_db)

    def calcular_co2(self):
        """Multiplica la cantidad que el usuario utilizó por el factor de emisión
        de transporte (0.21 kg CO₂/km) para calcular el CO₂ de la actividad."""
        return self._cantidad * 0.21

    def tipo(self):
        return "transporte"


class Energia(Actividad):
    """Actividad de consumo energético. Factor de emisión: 0.50 kg CO₂ por kWh."""

    def __init__(self, nombre, cantidad, fecha=None, id_db=None):
        super().__init__(nombre, cantidad, fecha, id_db)

    def calcular_co2(self):
        """Multiplica la cantidad que el usuario utilizó por el factor de emisión
        de energía (0.50 kg CO₂/kWh) para calcular el CO₂ de la actividad."""
        return self._cantidad * 0.50

    def tipo(self):
        return "energia"


class Alimentacion(Actividad):
    """Actividad de alimentación. Factor de emisión: 2.50 kg CO₂ por kg de alimento."""

    def __init__(self, nombre, cantidad, fecha=None, id_db=None):
        super().__init__(nombre, cantidad, fecha, id_db)

    def calcular_co2(self):
        """Multiplica la cantidad que el usuario utilizó por el factor de emisión
        de alimentación (2.50 kg CO₂/kg) para calcular el CO₂ de la actividad."""
        return self._cantidad * 2.50

    def tipo(self):
        return "alimentacion"


# Diccionario para instanciar clases sin usar if/elif
CLASES = {
    "transporte":   Transporte,
    "energia":      Energia,
    "alimentacion": Alimentacion
}


class CalculadoraHuella:
    """Gestiona la colección de actividades del usuario activo."""

    def __init__(self):
        self._actividades = []  # Lista privada de actividades del usuario
        self._usuario     = None

    @property
    def usuario(self):
        """Retorna el usuario activo."""
        return self._usuario

    def set_usuario(self, usuario):
        """Carga las actividades del usuario desde la base de datos."""
        self._usuario     = usuario
        self._actividades = []
        for id_db, tipo, nombre, cantidad, fecha in bd.cargar_actividades(usuario):
            cls = CLASES.get(tipo) 
            if cls:
                self._actividades.append(cls(nombre, cantidad, fecha, id_db=id_db))

    def agregar_actividad(self, act):
        """Permite agregar y almacenar actividades nuevas registradas."""
        id_db = bd.guardar_actividad(self._usuario, act)
        act.id_db = id_db
        self._actividades.append(act)

    def eliminar_actividad(self, act):
        """Permite remover actividades ya registradas tanto del programa como de la base de datos."""
        bd.eliminar_actividad(act.id_db)
        self._actividades.remove(act)

    def calcular_total(self):
        """Suma el CO₂ de todas las actividades registradas sin importar la fecha."""
        return sum(a.calcular_co2() for a in self._actividades)

    def calcular_hoy(self):
        """Da formato a la fecha y suma el CO₂ de las actividades registradas hoy."""
        hoy = date.today().strftime("%d/%m/%Y")
        return sum(a.calcular_co2() for a in self._actividades if a.fecha == hoy)

    def actividades_por_tipo(self, tipo):
        """Regresa todas las actividades registradas que son del mismo tipo."""
        return [a for a in self._actividades if a.tipo() == tipo]

    def todas_las_actividades(self):
        """Retorna una copia de todas las actividades del usuario."""
        return list(self._actividades)