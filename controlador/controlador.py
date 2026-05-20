from modelo.modelo import *
from vista.vista import *
from base_datos import inicializar, validar, registrar as db_registrar
from exportar import exportar_pdf
from datetime import date
import os


class Controlador:
    """Controlador principal del patrón MVC.
    Conecta la vista con el modelo y maneja toda la lógica de la aplicación."""

    def __init__(self):
        # Inicializa la base de datos, el modelo y la vista
        inicializar()
        self.modelo = CalculadoraHuella()
        self.vista  = Vista()
        self.usuario_actual = None

        # Conecta los callbacks de la vista con los métodos del controlador
        self.vista.cb_login      = self.login
        self.vista.cb_agregar    = self.agregar
        self.vista.cb_nueva      = self.ir_a_form
        self.vista.cb_hoy        = self.mostrar_historial
        self.vista.cb_total      = self.exportar_pdf
        self.vista.cb_logout     = self.logout
        self.vista.cb_volver     = self.volver
        self.vista.cb_tab        = self.cambiar_tab
        self.vista.cb_eliminar   = self.eliminar
        self.vista.cb_registrar  = self.registrar

        self.vista.boton.configure(command=self.agregar)

    def login(self):
        """Analiza los datos ingresados, los compara y verifica que coincidan
        con los de acceso del usuario para dar entrada al sistema."""
        usuario  = self.vista.entry_usuario.get().strip().lower()
        password = self.vista.entry_pass.get()

        if validar(usuario, password):
            self.usuario_actual = usuario
            self.modelo.set_usuario(usuario)
            self.vista.mostrar_error_login("")
            self.vista.actualizar_meta(usuario, str(date.today()))
            self.vista.ir_a_dashboard()
            self.actualizar_stats()
        else:
            self.vista.mostrar_error_login("Usuario o contraseña incorrectos")

    def registrar(self):
        """Verifica los datos del usuario nuevo y confirma que cumplan
        ciertos requisitos y coincidan en ambos campos."""
        usuario   = self.vista.entry_reg_usuario.get().strip().lower()
        password  = self.vista.entry_reg_pass.get()
        confirmar = self.vista.entry_reg_confirmar.get()

        if not usuario or not password:
            self.vista.mostrar_error_registro("Completa todos los campos")
            return
        if len(password) < 4:
            self.vista.mostrar_error_registro("La contraseña debe tener al menos 4 caracteres")
            return
        if password != confirmar:
            self.vista.mostrar_error_registro("Las contraseñas no coinciden")
            return

        if db_registrar(usuario, password):
            self.vista.mostrar_error_registro("✅ Usuario creado, ya puedes iniciar sesión")
            self.vista.ir_a_login()
        else:
            self.vista.mostrar_error_registro("Ese nombre de usuario ya existe")

    def agregar(self):
        """Verifica que al agregar una actividad nueva los datos estén
        llenos de manera correcta y con el tipo de dato adecuado."""
        nombre   = self.vista.entry_nombre.get()
        cantidad = self.vista.entry_cantidad.get()
        fecha    = date.today().strftime("%d/%m/%Y")

        if not nombre or not cantidad:
            self.vista.mostrar_error_form("Completa todos los campos")
            return
        try:
            cantidad = float(cantidad)
        except ValueError:
            self.vista.mostrar_error_form("La cantidad debe ser un número")
            return

        tipo = self.vista.combo.get()

        if tipo == "Transporte":
            act = Transporte(nombre, cantidad, fecha)
        elif tipo == "Energia":
            act = Energia(nombre, cantidad, fecha)
        else:
            act = Alimentacion(nombre, cantidad, fecha)

        self.modelo.agregar_actividad(act)
        self.vista.limpiar_form()
        self.vista.mostrar_error_form("✅ Actividad agregada")
        self.actualizar_stats()

    def eliminar(self, act):
        """Elimina actividades ya registradas y actualiza la lista en pantalla."""
        self.modelo.eliminar_actividad(act)
        self.actualizar_stats()

    def mostrar_historial(self):
        """Muestra todas las actividades registradas organizadas por fecha."""
        self.vista.abrir_historial(self.modelo.todas_las_actividades())

    def exportar_pdf(self):
        """Exporta todas las actividades registradas a un archivo PDF."""
        try:
            actividades = self.modelo.todas_las_actividades()
            if not actividades:
                self.vista.mostrar_popup("Sin actividades", "No hay actividades para exportar.")
                return
            ruta = exportar_pdf(self.usuario_actual, actividades)
            self.vista.mostrar_popup("✅ PDF generado",
                                     f"Archivo guardado en:\n{ruta}")
        except Exception as e:
            self.vista.mostrar_popup("Error", f"No se pudo generar el PDF:\n{e}")

    def ir_a_form(self):
        """Navega al formulario de nueva actividad según la tab activa."""
        tab = self.vista.get_tab_actual()
        self.vista.ir_a_form(tab)

    def volver(self):
        """Regresa al usuario a la ventana principal donde puede ver su consumo."""
        self.actualizar_stats()
        self.vista.ir_a_dashboard()

    def cambiar_tab(self, tab):
        """Muestra las actividades dependiendo de su categoría seleccionada."""
        actividades = self.modelo.actividades_por_tipo(tab.lower())
        self.vista.mostrar_actividades(actividades)

    def actualizar_stats(self):
        """Actualiza las tarjetas de huella de hoy y huella total en el dashboard."""
        self.vista.actualizar_stat(
            hoy=self.modelo.calcular_hoy(),
            total=self.modelo.calcular_total()
        )
        tab = self.vista.get_tab_actual()
        self.cambiar_tab(tab)

    def logout(self):
        """Limpia los datos del usuario activo y regresa a la ventana inicial."""
        self.usuario_actual = None
        self.vista.ir_a_login()

    def ejecutar(self):
        """Inicia el loop principal de la aplicación."""
        self.vista.iniciar()