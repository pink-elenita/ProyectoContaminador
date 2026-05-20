import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

# Configuración global del tema de la interfaz
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

# ── Paleta de colores del programa ───────────────────────────
BG_DARK      = "#1A0A2E"
BG_CARD      = "#2D1B4E"
BG_INPUT     = "#3D2460"
ACCENT_GRAD2 = "#7C3AED"
GREEN        = "#4ADE80"
GREEN_TEXT   = "#064E3B"
BORDER       = "#5B3A8A"
TEXT_PRIMARY = "#FFFFFF"
TEXT_MUTED   = "#A78CC0"
TEXT_LABEL   = "#C4A8E0"

# ── Fuentes ──────────────────────────────────────────────────
FONT_TITLE = ("Segoe UI Black", 22, "bold")
FONT_SUB   = ("Segoe UI Semibold", 13)
FONT_BODY  = ("Segoe UI", 12)
FONT_SMALL = ("Segoe UI", 11)

# ── Datos de la aplicación ───────────────────────────────────
TIPOS  = ["Transporte", "Energia", "Alimentacion"]
ICONOS = {"transporte": "🚗", "energia": "⚡", "alimentacion": "🌱"}
USUARIOS = {"admin": "1234", "elena": "pass", "usuario": "123"}


class Vista:
    """Vista principal del patrón MVC.
    Maneja las 4 pantallas de la aplicación como frames apilados."""

    def __init__(self):
        # Configuración de la ventana principal
        self.root = ctk.CTk()
        self.root.title("Calculadora Huella de Carbono")
        self.root.geometry("900x580")
        self.root.resizable(False, False)
        self.root.configure(fg_color=BG_DARK)

        # Callbacks que conecta el controlador con la vista
        self.cb_login     = None
        self.cb_agregar   = None
        self.cb_hoy       = None
        self.cb_total     = None
        self.cb_logout    = None
        self.cb_eliminar  = None
        self.cb_registrar = None

        # Estado de la tab activa en el dashboard
        self._tab_actual = "transporte"
        self._tab_btns   = {}

        # Construcción de todas las pantallas
        self._build_login()
        self._build_registro()
        self._build_dashboard()
        self._build_form()

        self._mostrar("login")

    # ── HELPERS — métodos reutilizables para construir la UI ─
    def _frame_base(self):
        """Crea un frame base que ocupa toda la ventana."""
        f = ctk.CTkFrame(self.root, fg_color=BG_DARK, corner_radius=0)
        f.place(relx=0, rely=0, relwidth=1, relheight=1)
        return f

    def _card(self, parent, **kw):
        """Crea una tarjeta con el estilo del programa."""
        defaults = dict(fg_color=BG_CARD, corner_radius=20,
                        border_width=1, border_color=BORDER)
        defaults.update(kw)
        return ctk.CTkFrame(parent, **defaults)

    def _label(self, parent, text, font=None, color=TEXT_PRIMARY, **kw):
        """Crea una etiqueta de texto con el estilo del programa."""
        return ctk.CTkLabel(parent, text=text,
                            font=font or FONT_BODY,
                            text_color=color, **kw)

    def _input(self, parent, placeholder=""):
        """Crea un campo de entrada de texto con el estilo del programa."""
        return ctk.CTkEntry(parent,
                            placeholder_text=placeholder,
                            fg_color=BG_INPUT,
                            border_color=BORDER,
                            border_width=1,
                            corner_radius=10,
                            text_color=TEXT_PRIMARY,
                            placeholder_text_color=TEXT_MUTED,
                            font=FONT_BODY,
                            height=40)

    def _btn_green(self, parent, text, cmd=None, width=200):
        """Crea un botón verde principal con el estilo del programa."""
        return ctk.CTkButton(parent, text=text, command=cmd,
                             fg_color=GREEN, hover_color="#86EFAC",
                             text_color=GREEN_TEXT,
                             font=("Segoe UI Black", 12, "bold"),
                             corner_radius=10, height=42, width=width)

    def _btn_outline(self, parent, text, cmd=None, width=180):
        """Crea un botón secundario con borde y el estilo del programa."""
        return ctk.CTkButton(parent, text=text, command=cmd,
                             fg_color="transparent",
                             border_color=BORDER, border_width=1,
                             hover_color=BG_INPUT,
                             text_color=TEXT_PRIMARY,
                             font=FONT_BODY,
                             corner_radius=10, height=36, width=width)

    # ── PANTALLA 1 — LOGIN ───────────────────────────────────
    def _build_login(self):
        """Construye los elementos de la pantalla inicial de inicio de sesión."""
        self._frame_login = self._frame_base()

        card = self._card(self._frame_login, width=400, height=520)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=36, pady=36)

        self._label(inner, "🌿", font=("Segoe UI", 36)).pack(pady=(0, 8))
        self._label(inner, "Calculadora Huella\nde Carbono", font=FONT_TITLE).pack()
        self._label(inner, '"Reduce tu Huella Hoy"',
                    font=("Segoe UI Italic", 11), color=TEXT_MUTED).pack(pady=(4, 20))

        self._label(inner, "Usuario", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_usuario = self._input(inner, "Tu nombre de usuario")
        self.entry_usuario.pack(fill="x", pady=(2, 10))

        self._label(inner, "Contraseña", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_pass = self._input(inner, "••••••••")
        self.entry_pass.configure(show="•")
        self.entry_pass.pack(fill="x", pady=(2, 4))

        self._lbl_error_login = self._label(inner, "", color="#FCA5A5", font=FONT_SMALL)
        self._lbl_error_login.pack(pady=(0, 10))

        self.boton_login = self._btn_green(inner, "INICIAR SESIÓN", width=330)
        self.boton_login.pack(fill="x")
        self.boton_login.configure(command=lambda: self.cb_login and self.cb_login())

        self._btn_outline(inner, "Crear cuenta nueva", width=330,
                          cmd=lambda: self.ir_a_registro()
                          ).pack(fill="x", pady=(10, 0))

    def mostrar_error_login(self, msg=""):
        """Muestra u oculta el mensaje de error en el login."""
        self._lbl_error_login.configure(text=msg)

    # ── PANTALLA 2 — REGISTRO ────────────────────────────────
    def _build_registro(self):
        """Construye los elementos de la pantalla de registro de nuevo usuario."""
        self._frame_reg = self._frame_base()

        card = self._card(self._frame_reg, width=400, height=530)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=36, pady=36)

        self._label(inner, "🌿", font=("Segoe UI", 36)).pack(pady=(0, 8))
        self._label(inner, "Crear cuenta", font=FONT_TITLE).pack()
        self._label(inner, "Únete y empieza a medir tu huella",
                    font=("Segoe UI Italic", 11), color=TEXT_MUTED).pack(pady=(4, 20))

        self._label(inner, "Usuario", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_reg_usuario = self._input(inner, "Elige un nombre de usuario")
        self.entry_reg_usuario.pack(fill="x", pady=(2, 10))

        self._label(inner, "Contraseña", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_reg_pass = self._input(inner, "Mínimo 4 caracteres")
        self.entry_reg_pass.configure(show="•")
        self.entry_reg_pass.pack(fill="x", pady=(2, 10))

        self._label(inner, "Confirmar contraseña", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_reg_confirmar = self._input(inner, "Repite tu contraseña")
        self.entry_reg_confirmar.configure(show="•")
        self.entry_reg_confirmar.pack(fill="x", pady=(2, 4))

        self._lbl_error_registro = self._label(inner, "", color="#FCA5A5", font=FONT_SMALL)
        self._lbl_error_registro.pack(pady=(0, 8))

        self._btn_green(inner, "CREAR CUENTA", width=330,
                        cmd=lambda: self.cb_registrar and self.cb_registrar()
                        ).pack(fill="x", pady=(0, 10))

        self._btn_outline(inner, "← Ya tengo cuenta", width=330,
                          cmd=lambda: self.ir_a_login()
                          ).pack(fill="x")

    def mostrar_error_registro(self, msg=""):
        """Muestra u oculta el mensaje de error en el registro."""
        self._lbl_error_registro.configure(text=msg)

    # ── PANTALLA 3 — DASHBOARD ───────────────────────────────
    def _build_dashboard(self):
        """Construye los elementos de la página principal donde se ven las actividades."""
        self._frame_dash = self._frame_base()

        # Header con título y botón de cerrar sesión
        header = ctk.CTkFrame(self._frame_dash, fg_color="transparent")
        header.pack(fill="x", padx=32, pady=(24, 0))

        left_h = ctk.CTkFrame(header, fg_color="transparent")
        left_h.pack(side="left", fill="x", expand=True)

        self._label(left_h, "Calculadora Huella de Carbono", font=FONT_TITLE).pack(anchor="w")
        self._lbl_meta = self._label(left_h, "Usuario:  ·  Fecha:",
                                      font=FONT_SMALL, color=TEXT_MUTED)
        self._lbl_meta.pack(anchor="w", pady=(2, 0))

        self._btn_outline(header, "Cerrar sesión",
                          cmd=lambda: self.cb_logout and self.cb_logout(),
                          width=140).pack(side="right")

        # Tarjetas de estadísticas
        stat_row = ctk.CTkFrame(self._frame_dash, fg_color="transparent")
        stat_row.pack(fill="x", padx=32, pady=(16, 0))

        self._card_hoy   = self._stat_card(stat_row, "Huella de Hoy", "0.00 kg CO₂")
        self._card_total = self._stat_card(stat_row, "Huella Total",  "0.00 kg CO₂")
        self._card_hoy.pack(side="left", padx=(0, 10))
        self._card_total.pack(side="left")

        # Tabs de categorías
        tab_frame = ctk.CTkFrame(self._frame_dash, fg_color="#0D0520", corner_radius=12)
        tab_frame.pack(fill="x", padx=32, pady=(20, 0))

        for t in ["transporte", "energia", "alimentacion"]:
            ico = ICONOS[t]
            btn = ctk.CTkButton(tab_frame,
                                text=f"{ico}  {t.capitalize()}",
                                command=lambda x=t: self._set_tab(x),
                                fg_color="transparent",
                                hover_color=BG_INPUT,
                                text_color=TEXT_MUTED,
                                font=("Segoe UI Black", 11, "bold"),
                                corner_radius=10, height=36)
            btn.pack(side="left", expand=True, fill="x", padx=4, pady=4)
            self._tab_btns[t] = btn

        self._set_tab("transporte", _init=True)

        # Lista de actividades con scroll
        list_card = self._card(self._frame_dash)
        list_card.pack(fill="both", expand=True, padx=32, pady=(14, 0))

        self._lbl_lista_vacia = self._label(list_card,
            "Sin actividades en esta categoría.\n¡Agrega una actividad! 👇",
            color=TEXT_MUTED, font=FONT_BODY)
        self._lbl_lista_vacia.pack(expand=True)

        self._scroll_lista = ctk.CTkScrollableFrame(list_card,
                                                     fg_color="transparent",
                                                     scrollbar_button_color=BORDER)
        self._scroll_lista.pack(fill="both", expand=True, padx=12, pady=12)

        # Botones de acción
        act_row = ctk.CTkFrame(self._frame_dash, fg_color="transparent")
        act_row.pack(fill="x", padx=32, pady=(12, 20))

        self._btn_green(act_row, "+ Registrar Nueva Actividad",
                        cmd=lambda: self.cb_nueva and self.cb_nueva(),
                        width=240).pack(side="left", padx=(0, 10))

        self._btn_outline(act_row, "📅 Historial",
                          cmd=lambda: self.cb_hoy and self.cb_hoy(),
                          width=140).pack(side="left", padx=(0, 10))

        self._btn_outline(act_row, "📄 Exportar PDF",
                          cmd=lambda: self.cb_total and self.cb_total(),
                          width=150).pack(side="left")

    def _stat_card(self, parent, label, value):
        """Crea una tarjeta de estadística con etiqueta y valor."""
        card = self._card(parent, width=200, height=80)
        card.pack_propagate(False)
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=18, pady=10)
        self._label(inner, label, font=FONT_SMALL, color=TEXT_MUTED).pack(anchor="w")
        lbl_val = self._label(inner, value, font=("Segoe UI Black", 20, "bold"))
        lbl_val.pack(anchor="w")
        card._val_label = lbl_val
        return card

    def _set_tab(self, tab, _init=False):
        """Muestra cada tab con sus respectivas actividades registradas."""
        self._tab_actual = tab
        for t, btn in self._tab_btns.items():
            if t == tab:
                btn.configure(fg_color=GREEN, text_color=GREEN_TEXT)
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_MUTED)
        if not _init:
            self._render_lista([])
            if self.cb_tab:
                self.cb_tab(tab)

    def get_tab_actual(self):
        """Retorna la tab activa actualmente."""
        return self._tab_actual

    def _render_lista(self, actividades):
        """Limpia la lista anterior y redibuja todas las actividades
        con su información y botón de eliminar."""
        for w in self._scroll_lista.winfo_children():
            w.destroy()

        if not actividades:
            self._lbl_lista_vacia.pack(expand=True)
            self._scroll_lista.pack_forget()
            return

        self._lbl_lista_vacia.pack_forget()
        self._scroll_lista.pack(fill="both", expand=True, padx=12, pady=12)

        for act in actividades:
            row = ctk.CTkFrame(self._scroll_lista, fg_color=BG_INPUT, corner_radius=10)
            row.pack(fill="x", pady=4)

            info = ctk.CTkFrame(row, fg_color="transparent")
            info.pack(side="left", padx=14, pady=10, expand=True, fill="x")

            self._label(info, act.nombre, font=FONT_SUB).pack(anchor="w")
            self._label(info, f"{act.cantidad} unidades · {act.fecha}",
                        font=FONT_SMALL, color=TEXT_MUTED).pack(anchor="w")

            self._label(row, f"{act.calcular_co2():.2f} kg CO₂",
                        font=("Segoe UI Black", 13, "bold"),
                        color=GREEN).pack(side="right", padx=8)

            ctk.CTkButton(row, text="🗑",
                          width=32, height=32,
                          fg_color="transparent",
                          hover_color="#4B1C1C",
                          text_color="#FCA5A5",
                          font=("Segoe UI", 14),
                          corner_radius=8,
                          command=lambda a=act: self.cb_eliminar and self.cb_eliminar(a)
                          ).pack(side="right", padx=(0, 6))

    def actualizar_stat(self, hoy=None, total=None):
        """Actualiza los valores de las tarjetas de huella de hoy y huella total."""
        if hoy is not None:
            self._card_hoy._val_label.configure(text=f"{hoy:.2f} kg CO₂")
        if total is not None:
            self._card_total._val_label.configure(text=f"{total:.2f} kg CO₂")

    def actualizar_meta(self, usuario, fecha):
        """Actualiza el nombre de usuario y fecha en el header del dashboard."""
        self._lbl_meta.configure(text=f"Usuario: {usuario}   ·   {fecha}")

    def mostrar_actividades(self, lista):
        """Manda la lista de actividades a renderizar en pantalla."""
        self._render_lista(lista)

    def mostrar_popup(self, titulo, mensaje):
        """Muestra una ventana emergente con un mensaje al usuario."""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title(titulo)
        ventana.geometry("420x200")
        ventana.resizable(False, False)
        ventana.configure(fg_color=BG_DARK)
        ventana.grab_set()

        card = self._card(ventana, width=380, height=160)
        card.place(relx=0.5, rely=0.5, anchor="center")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=24, pady=20)

        self._label(inner, titulo, font=FONT_SUB).pack(anchor="w")
        self._label(inner, mensaje, font=FONT_SMALL, color=TEXT_MUTED).pack(anchor="w", pady=(6, 14))
        self._btn_green(inner, "Aceptar", cmd=ventana.destroy, width=140).pack(anchor="e")

    def abrir_historial(self, actividades):
        """Abre una ventana de historial donde se pueden ver actividades por fecha."""
        ventana = ctk.CTkToplevel(self.root)
        ventana.title("Historial por fecha")
        ventana.geometry("560x480")
        ventana.resizable(False, False)
        ventana.configure(fg_color=BG_DARK)
        ventana.grab_set()

        header = ctk.CTkFrame(ventana, fg_color="transparent")
        header.pack(fill="x", padx=24, pady=(20, 0))
        self._label(header, "📅 Historial por fecha", font=FONT_TITLE).pack(anchor="w")

        # Obtiene fechas únicas ordenadas de más reciente a más antigua
        fechas = sorted(set(a.fecha for a in actividades), reverse=True)

        if not fechas:
            self._label(ventana, "No hay actividades registradas.",
                        color=TEXT_MUTED).pack(expand=True)
            return

        sel_row = ctk.CTkFrame(ventana, fg_color="transparent")
        sel_row.pack(fill="x", padx=24, pady=(14, 0))

        self._label(sel_row, "Fecha:", font=FONT_SMALL, color=TEXT_LABEL).pack(side="left", padx=(0, 10))

        combo_fecha = ctk.CTkComboBox(sel_row, values=fechas,
                                       fg_color=BG_INPUT,
                                       border_color=BORDER,
                                       button_color=BORDER,
                                       dropdown_fg_color=BG_CARD,
                                       text_color=TEXT_PRIMARY,
                                       font=FONT_BODY,
                                       width=200, height=36)
        combo_fecha.set(fechas[0])
        combo_fecha.pack(side="left")

        result_card = self._card(ventana)
        result_card.pack(fill="both", expand=True, padx=24, pady=(14, 20))

        scroll = ctk.CTkScrollableFrame(result_card, fg_color="transparent",
                                         scrollbar_button_color=BORDER)
        scroll.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_total = self._label(result_card, "", font=FONT_SUB, color=GREEN)
        lbl_total.pack(pady=(0, 8))

        def mostrar_fecha(fecha):
            """Filtra y muestra las actividades de la fecha seleccionada."""
            for w in scroll.winfo_children():
                w.destroy()

            acts_fecha = [a for a in actividades if a.fecha == fecha]

            if not acts_fecha:
                self._label(scroll, "Sin actividades en esta fecha.",
                            color=TEXT_MUTED).pack(expand=True, pady=20)
                lbl_total.configure(text="")
                return

            total = 0
            for act in acts_fecha:
                row = ctk.CTkFrame(scroll, fg_color=BG_INPUT, corner_radius=10)
                row.pack(fill="x", pady=4)

                info = ctk.CTkFrame(row, fg_color="transparent")
                info.pack(side="left", padx=14, pady=8, expand=True, fill="x")

                ico = ICONOS.get(act.tipo(), "")
                self._label(info, f"{ico} {act.nombre}", font=FONT_SUB).pack(anchor="w")
                self._label(info, act.tipo().capitalize(),
                            font=FONT_SMALL, color=TEXT_MUTED).pack(anchor="w")

                co2 = act.calcular_co2()
                total += co2
                self._label(row, f"{co2:.2f} kg CO₂",
                            font=("Segoe UI Black", 12, "bold"),
                            color=GREEN).pack(side="right", padx=14)

            lbl_total.configure(text=f"Total del día: {total:.2f} kg CO₂")

        combo_fecha.configure(command=mostrar_fecha)
        mostrar_fecha(fechas[0])

    # ── PANTALLA 4 — FORMULARIO NUEVA ACTIVIDAD ──────────────
    def _build_form(self):
        """Construye los elementos del formulario para registrar una nueva actividad."""
        self._frame_form = self._frame_base()

        self._btn_outline(self._frame_form, "← Volver al Dashboard",
                          cmd=lambda: self.cb_volver and self.cb_volver(),
                          width=200).pack(anchor="nw", padx=32, pady=(28, 0))

        card = self._card(self._frame_form, width=480, height=520)
        card.place(relx=0.5, rely=0.55, anchor="center")
        card.pack_propagate(False)

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(expand=True, fill="both", padx=40, pady=32)

        badge_wrap = ctk.CTkFrame(inner, fg_color=GREEN, corner_radius=20)
        badge_wrap.pack(anchor="w", pady=(0, 14))
        self._lbl_badge = ctk.CTkLabel(badge_wrap, text="🚗  TRANSPORTE",
                                        font=("Segoe UI Black", 11, "bold"),
                                        text_color=GREEN_TEXT)
        self._lbl_badge.pack(padx=14, pady=4)

        self._label(inner, "Nueva Actividad", font=FONT_TITLE).pack(anchor="w")
        self._lbl_form_cat = self._label(inner, "Categoría: Transporte",
                                          font=FONT_SMALL, color=TEXT_MUTED)
        self._lbl_form_cat.pack(anchor="w", pady=(2, 18))

        self._label(inner, "Categoría", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.combo = ctk.CTkComboBox(inner, values=TIPOS,
                                      fg_color=BG_INPUT,
                                      border_color=BORDER,
                                      button_color=BORDER,
                                      button_hover_color=ACCENT_GRAD2,
                                      dropdown_fg_color=BG_CARD,
                                      text_color=TEXT_PRIMARY,
                                      font=FONT_BODY,
                                      corner_radius=10, height=40,
                                      command=self._on_combo_change)
        self.combo.pack(fill="x", pady=(2, 10))

        self._label(inner, "Actividad", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_nombre = self._input(inner, "ej. Auto gasolina, Luz eléctrica…")
        self.entry_nombre.pack(fill="x", pady=(2, 10))

        self._label(inner, "Cantidad (km / kWh / kg)", font=FONT_SMALL, color=TEXT_LABEL).pack(anchor="w")
        self.entry_cantidad = self._input(inner, "ej. 30")
        self.entry_cantidad.pack(fill="x", pady=(2, 4))

        self._lbl_error_form = self._label(inner, "", color="#FCA5A5", font=FONT_SMALL)
        self._lbl_error_form.pack(pady=(0, 10))

        self.boton = self._btn_green(inner, "Agregar Actividad", width=400)
        self.boton.pack(fill="x")

    def _on_combo_change(self, val):
        """Actualiza el badge y la etiqueta de categoría al cambiar el combo."""
        iconos = {"Transporte": "🚗", "Energia": "⚡", "Alimentacion": "🌱"}
        ico = iconos.get(val, "")
        self._lbl_badge.configure(text=f"{ico}  {val.upper()}")
        self._lbl_form_cat.configure(text=f"Categoría: {val}")

    def mostrar_error_form(self, msg=""):
        """Muestra u oculta el mensaje de error en el formulario."""
        self._lbl_error_form.configure(text=msg)

    def limpiar_form(self):
        """Limpia los campos del formulario después de agregar una actividad."""
        self.entry_nombre.delete(0, "end")
        self.entry_cantidad.delete(0, "end")
        self._lbl_error_form.configure(text="")

    # ── NAVEGACIÓN ───────────────────────────────────────────
    def _mostrar(self, pantalla):
        """Muestra y oculta pantallas según lo que se necesite."""
        self._frame_login.place_forget()
        self._frame_reg.place_forget()
        self._frame_dash.place_forget()
        self._frame_form.place_forget()
        if pantalla == "login":
            self._frame_login.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif pantalla == "registro":
            self._frame_reg.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif pantalla == "dashboard":
            self._frame_dash.place(relx=0, rely=0, relwidth=1, relheight=1)
        elif pantalla == "form":
            self._frame_form.place(relx=0, rely=0, relwidth=1, relheight=1)

    def ir_a_dashboard(self):
        """Navega a la pantalla principal del dashboard."""
        self._mostrar("dashboard")

    def ir_a_registro(self):
        """Navega a la pantalla de registro limpiando los campos."""
        self.entry_reg_usuario.delete(0, "end")
        self.entry_reg_pass.delete(0, "end")
        self.entry_reg_confirmar.delete(0, "end")
        self._lbl_error_registro.configure(text="")
        self._mostrar("registro")

    def ir_a_form(self, tab="transporte"):
        """Navega al formulario con la categoría de la tab activa preseleccionada."""
        iconos_map = {"transporte":   "Transporte",
                      "energia":      "Energia",
                      "alimentacion": "Alimentacion"}
        self.combo.set(iconos_map.get(tab, "Transporte"))
        self._on_combo_change(iconos_map.get(tab, "Transporte"))
        self.limpiar_form()
        self._mostrar("form")

    def ir_a_login(self):
        """Limpia los datos del usuario y regresa a la pantalla inicial."""
        # Limpia los campos al cerrar sesión para que no queden visibles
        self.entry_usuario.delete(0, "end")
        self.entry_pass.delete(0, "end")
        self.mostrar_error_login("")
        self._mostrar("login")

    def iniciar(self):
        """Inicia el loop principal de la interfaz gráfica."""
        self.root.mainloop()