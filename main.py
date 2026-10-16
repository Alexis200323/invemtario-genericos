from datetime import datetime
import os
import sqlite3
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.scrollview import ScrollView
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.utils import platform
from kivy.properties import ObjectProperty, StringProperty


# Colores de la app
COLOR_PRIMARY = (0.15, 0.35, 0.65, 1)      # Azul oscuro
COLOR_SECONDARY = (0.20, 0.55, 0.40, 1)    # Verde
COLOR_DANGER = (0.75, 0.20, 0.20, 1)       # Rojo
COLOR_BG = (0.95, 0.95, 0.97, 1)           # Fondo claro
COLOR_CARD = (1, 1, 1, 1)
COLOR_TEXT = (0.15, 0.15, 0.20, 1)


def get_db_path():
    """Devuelve la ruta correcta de la base de datos (funciona en Android y PC)."""
    app = App.get_running_app()
    if app:
        return os.path.join(app.user_data_dir, "inventario_genericos.db")
    return "inventario_genericos.db"


def init_db():
    """Crea las tablas si no existen y el usuario admin por defecto."""
    db_path = get_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario TEXT UNIQUE,
            password TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS productos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT UNIQUE,
            stock_litros REAL,
            costo_litro REAL,
            precio_litro REAL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movimientos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT,
            tipo TEXT,
            producto TEXT,
            litros REAL,
            monto_total REAL,
            ganancia REAL
        )
    """)
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM usuarios")
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
            ("admin", "1234"),
        )
        conn.commit()

    conn.close()


def mostrar_popup(titulo, mensaje, color=COLOR_PRIMARY):
    """Muestra un popup simple de información."""
    content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
    content.add_widget(Label(
        text=mensaje,
        color=COLOR_TEXT,
        text_size=(Window.width * 0.7, None),
        halign="center",
        valign="middle",
        font_size="16sp"
    ))
    btn = Button(
        text="Aceptar",
        size_hint_y=None,
        height=dp(45),
        background_color=color,
        background_normal=""
    )
    popup = Popup(
        title=titulo,
        content=content,
        size_hint=(0.85, 0.4),
        auto_dismiss=False,
        title_color=COLOR_PRIMARY,
        title_size="18sp"
    )
    btn.bind(on_release=popup.dismiss)
    content.add_widget(btn)
    popup.open()


# ==================== PANTALLAS ====================

class LoginScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        layout = BoxLayout(orientation="vertical", padding=dp(30), spacing=dp(20))

        # Título
        layout.add_widget(Label(
            text="CONTROL DE GENÉRICOS",
            font_size="26sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        ))
        layout.add_widget(Label(
            text="Inicia sesión para continuar",
            font_size="15sp",
            color=(0.4, 0.4, 0.45, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        # Espacio
        layout.add_widget(Label(size_hint_y=0.15))

        # Usuario
        layout.add_widget(Label(
            text="Usuario",
            font_size="14sp",
            color=COLOR_TEXT,
            size_hint_y=None,
            height=dp(25),
            halign="left"
        ))
        self.usuario = TextInput(
            hint_text="Ej: admin",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)],
            background_color=(1, 1, 1, 1)
        )
        layout.add_widget(self.usuario)

        # Contraseña
        layout.add_widget(Label(
            text="Contraseña",
            font_size="14sp",
            color=COLOR_TEXT,
            size_hint_y=None,
            height=dp(25)
        ))
        self.password = TextInput(
            hint_text="••••",
            password=True,
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        layout.add_widget(self.password)

        # Botón entrar
        btn_login = Button(
            text="ENTRAR",
            size_hint_y=None,
            height=dp(52),
            background_color=COLOR_PRIMARY,
            background_normal="",
            font_size="17sp",
            bold=True
        )
        btn_login.bind(on_release=self.intentar_login)
        layout.add_widget(btn_login)

        layout.add_widget(Label(size_hint_y=0.3))

        # Nota
        layout.add_widget(Label(
            text="Usuario por defecto: admin  |  Contraseña: 1234",
            font_size="12sp",
            color=(0.5, 0.5, 0.55, 1),
            size_hint_y=None,
            height=dp(30)
        ))

        self.add_widget(layout)

    def intentar_login(self, instance):
        usu = self.usuario.text.strip().lower()
        pwd = self.password.text.strip()

        if not usu or not pwd:
            mostrar_popup("Error", "Por favor completa todos los campos.", COLOR_DANGER)
            return

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE usuario = ? AND password = ?",
            (usu, pwd)
        )
        resultado = cursor.fetchone()
        conn.close()

        if resultado:
            self.manager.current = "menu"
            self.usuario.text = ""
            self.password.text = ""
        else:
            mostrar_popup("Acceso denegado", "Usuario o contraseña incorrectos.", COLOR_DANGER)


class MenuScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(12))

        # Header
        root.add_widget(Label(
            text="MENÚ PRINCIPAL",
            font_size="24sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(50)
        ))

        # Botones del menú
        botones = [
            ("1. Ver Inventario y Stock", "inventario", COLOR_PRIMARY),
            ("2. Agregar Nuevo Producto", "agregar", COLOR_SECONDARY),
            ("3. Registrar Entrada (Compra)", "entrada", COLOR_PRIMARY),
            ("4. Registrar Salida (Venta)", "salida", COLOR_SECONDARY),
            ("5. Ver Balance Financiero", "balance", COLOR_PRIMARY),
            ("6. Eliminar Producto", "eliminar", COLOR_DANGER),
            ("7. Cambiar Usuario / Contraseña", "credenciales", (0.45, 0.35, 0.65, 1)),
            ("8. Cerrar Sesión", "login", (0.4, 0.4, 0.45, 1)),
        ]

        for texto, pantalla, color in botones:
            btn = Button(
                text=texto,
                size_hint_y=None,
                height=dp(52),
                background_color=color,
                background_normal="",
                font_size="15sp",
                bold=True
            )
            btn.bind(on_release=lambda inst, p=pantalla: self.ir_a(p))
            root.add_widget(btn)

        self.add_widget(root)

    def ir_a(self, pantalla):
        self.manager.transition.direction = "left"
        self.manager.current = pantalla


class InventarioScreen(Screen):
    def on_enter(self):
        self.actualizar_lista()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(15), spacing=dp(10))

        root.add_widget(Label(
            text="INVENTARIO ACTUAL",
            font_size="22sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        # Scroll con la lista
        self.scroll = ScrollView(do_scroll_x=False)
        self.lista = GridLayout(cols=1, spacing=dp(8), size_hint_y=None, padding=dp(5))
        self.lista.bind(minimum_height=self.lista.setter("height"))
        self.scroll.add_widget(self.lista)
        root.add_widget(self.scroll)

        # Botón volver
        btn_volver = Button(
            text="← Volver al Menú",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def actualizar_lista(self):
        self.lista.clear_widgets()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre, stock_litros, costo_litro, precio_litro FROM productos ORDER BY nombre"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.lista.add_widget(Label(
                text="Aún no hay productos registrados.",
                color=(0.5, 0.5, 0.55, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        # Encabezado
        header = BoxLayout(size_hint_y=None, height=dp(35), spacing=dp(5))
        for txt, w in [("PRODUCTO", 0.35), ("STOCK", 0.20), ("COSTO/L", 0.225), ("PRECIO/L", 0.225)]:
            header.add_widget(Label(
                text=txt,
                bold=True,
                color=COLOR_PRIMARY,
                size_hint_x=w,
                font_size="13sp"
            ))
        self.lista.add_widget(header)

        for nombre, stock, costo, precio in rows:
            fila = BoxLayout(size_hint_y=None, height=dp(42), spacing=dp(5))
            fila.add_widget(Label(text=nombre.title(), size_hint_x=0.35, color=COLOR_TEXT, font_size="14sp"))
            fila.add_widget(Label(text=f"{stock:.1f} L", size_hint_x=0.20, color=COLOR_TEXT, font_size="14sp"))
            fila.add_widget(Label(text=f"${costo:.2f}", size_hint_x=0.225, color=COLOR_TEXT, font_size="14sp"))
            fila.add_widget(Label(text=f"${precio:.2f}", size_hint_x=0.225, color=COLOR_TEXT, font_size="14sp"))
            self.lista.add_widget(fila)

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class AgregarProductoScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(12))

        root.add_widget(Label(
            text="AGREGAR PRODUCTO",
            font_size="22sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        # Nombre
        root.add_widget(Label(text="Nombre del producto", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.nombre = TextInput(
            hint_text="Ej: Cloro, Cera parafinada",
            multiline=False,
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        root.add_widget(self.nombre)

        # Costo
        root.add_widget(Label(text="Costo por litro ($)", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.costo = TextInput(
            hint_text="0.00",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        root.add_widget(self.costo)

        # Precio
        root.add_widget(Label(text="Precio de venta por litro ($)", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.precio = TextInput(
            hint_text="0.00",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        root.add_widget(self.precio)

        root.add_widget(Label(size_hint_y=0.1))

        # Botones
        btn_guardar = Button(
            text="GUARDAR PRODUCTO",
            size_hint_y=None,
            height=dp(52),
            background_color=COLOR_SECONDARY,
            background_normal="",
            font_size="16sp",
            bold=True
        )
        btn_guardar.bind(on_release=self.guardar)
        root.add_widget(btn_guardar)

        btn_volver = Button(
            text="← Cancelar",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def guardar(self, instance):
        nombre = self.nombre.text.strip().lower()
        if not nombre:
            mostrar_popup("Error", "El nombre no puede estar vacío.", COLOR_DANGER)
            return

        try:
            costo = float(self.costo.text.strip() or 0)
            precio = float(self.precio.text.strip() or 0)
        except ValueError:
            mostrar_popup("Error", "Costo y precio deben ser números válidos.", COLOR_DANGER)
            return

        try:
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO productos (nombre, stock_litros, costo_litro, precio_litro) VALUES (?, 0, ?, ?)",
                (nombre, costo, precio)
            )
            conn.commit()
            conn.close()
            mostrar_popup("Éxito", f"Producto '{nombre.title()}' agregado correctamente.", COLOR_SECONDARY)
            self.nombre.text = ""
            self.costo.text = ""
            self.precio.text = ""
        except sqlite3.IntegrityError:
            mostrar_popup("Error", f"El producto '{nombre}' ya existe.", COLOR_DANGER)
        except Exception as e:
            mostrar_popup("Error", f"Ocurrió un error: {e}", COLOR_DANGER)

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class EntradaScreen(Screen):
    def on_enter(self):
        self.cargar_productos()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        root.add_widget(Label(
            text="REGISTRAR ENTRADA",
            font_size="22sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        root.add_widget(Label(
            text="Selecciona el producto:",
            size_hint_y=None,
            height=dp(28),
            color=COLOR_TEXT
        ))

        self.scroll = ScrollView(do_scroll_x=False, size_hint_y=0.45)
        self.lista_prod = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_prod.bind(minimum_height=self.lista_prod.setter("height"))
        self.scroll.add_widget(self.lista_prod)
        root.add_widget(self.scroll)

        self.producto_seleccionado = None
        self.lbl_seleccionado = Label(
            text="Ningún producto seleccionado",
            size_hint_y=None,
            height=dp(30),
            color=(0.5, 0.5, 0.55, 1),
            font_size="14sp"
        )
        root.add_widget(self.lbl_seleccionado)

        root.add_widget(Label(text="Litros que entran:", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.litros = TextInput(
            hint_text="0.0",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        root.add_widget(self.litros)

        btn_guardar = Button(
            text="REGISTRAR ENTRADA",
            size_hint_y=None,
            height=dp(52),
            background_color=COLOR_SECONDARY,
            background_normal="",
            font_size="16sp",
            bold=True
        )
        btn_guardar.bind(on_release=self.registrar)
        root.add_widget(btn_guardar)

        btn_volver = Button(
            text="← Volver",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def cargar_productos(self):
        self.lista_prod.clear_widgets()
        self.producto_seleccionado = None
        self.lbl_seleccionado.text = "Ningún producto seleccionado"
        self.litros.text = ""

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, stock_litros, costo_litro FROM productos ORDER BY nombre")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.lista_prod.add_widget(Label(
                text="No hay productos. Agrega uno primero.",
                color=(0.5, 0.5, 0.55, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for nombre, stock, costo in rows:
            btn = Button(
                text=f"{nombre.title()}  |  Stock: {stock:.1f} L  |  Costo: ${costo:.2f}",
                size_hint_y=None,
                height=dp(48),
                background_color=(0.9, 0.92, 0.95, 1),
                background_normal="",
                color=COLOR_TEXT,
                font_size="14sp"
            )
            btn.bind(on_release=lambda inst, n=nombre, s=stock, c=costo: self.seleccionar(n, s, c))
            self.lista_prod.add_widget(btn)

    def seleccionar(self, nombre, stock, costo):
        self.producto_seleccionado = {"nombre": nombre, "stock": stock, "costo": costo}
        self.lbl_seleccionado.text = f"Seleccionado: {nombre.title()}"
        self.lbl_seleccionado.color = COLOR_SECONDARY

    def registrar(self, instance):
        if not self.producto_seleccionado:
            mostrar_popup("Error", "Selecciona un producto primero.", COLOR_DANGER)
            return

        try:
            litros = float(self.litros.text.strip() or 0)
            if litros <= 0:
                raise ValueError
        except ValueError:
            mostrar_popup("Error", "Ingresa una cantidad válida de litros.", COLOR_DANGER)
            return

        nombre = self.producto_seleccionado["nombre"]
        costo = self.producto_seleccionado["costo"]
        inversion = litros * costo
        nuevo_stock = self.producto_seleccionado["stock"] + litros

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET stock_litros = ? WHERE nombre = ?",
            (nuevo_stock, nombre)
        )
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "INSERT INTO movimientos (fecha, tipo, producto, litros, monto_total, ganancia) VALUES (?, 'ENTRADA', ?, ?, ?, 0)",
            (fecha, nombre, litros, inversion)
        )
        conn.commit()
        conn.close()

        mostrar_popup(
            "Entrada registrada",
            f"Se agregaron {litros} L de {nombre.title()}\nInversión: ${inversion:,.2f}",
            COLOR_SECONDARY
        )
        self.cargar_productos()

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class SalidaScreen(Screen):
    def on_enter(self):
        self.cargar_productos()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        root.add_widget(Label(
            text="REGISTRAR VENTA",
            font_size="22sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        root.add_widget(Label(
            text="Selecciona el producto:",
            size_hint_y=None,
            height=dp(28),
            color=COLOR_TEXT
        ))

        self.scroll = ScrollView(do_scroll_x=False, size_hint_y=0.45)
        self.lista_prod = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_prod.bind(minimum_height=self.lista_prod.setter("height"))
        self.scroll.add_widget(self.lista_prod)
        root.add_widget(self.scroll)

        self.producto_seleccionado = None
        self.lbl_seleccionado = Label(
            text="Ningún producto seleccionado",
            size_hint_y=None,
            height=dp(30),
            color=(0.5, 0.5, 0.55, 1),
            font_size="14sp"
        )
        root.add_widget(self.lbl_seleccionado)

        root.add_widget(Label(text="Litros vendidos:", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.litros = TextInput(
            hint_text="0.0",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
            padding=[dp(12), dp(12)]
        )
        root.add_widget(self.litros)

        btn_guardar = Button(
            text="REGISTRAR VENTA",
            size_hint_y=None,
            height=dp(52),
            background_color=COLOR_SECONDARY,
            background_normal="",
            font_size="16sp",
            bold=True
        )
        btn_guardar.bind(on_release=self.registrar)
        root.add_widget(btn_guardar)

        btn_volver = Button(
            text="← Volver",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def cargar_productos(self):
        self.lista_prod.clear_widgets()
        self.producto_seleccionado = None
        self.lbl_seleccionado.text = "Ningún producto seleccionado"
        self.litros.text = ""

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT nombre, stock_litros, costo_litro, precio_litro FROM productos ORDER BY nombre"
        )
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.lista_prod.add_widget(Label(
                text="No hay productos. Agrega uno primero.",
                color=(0.5, 0.5, 0.55, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for nombre, stock, costo, precio in rows:
            btn = Button(
                text=f"{nombre.title()}  |  Stock: {stock:.1f} L  |  Precio: ${precio:.2f}",
                size_hint_y=None,
                height=dp(48),
                background_color=(0.9, 0.92, 0.95, 1),
                background_normal="",
                color=COLOR_TEXT,
                font_size="14sp"
            )
            btn.bind(on_release=lambda inst, n=nombre, s=stock, c=costo, p=precio: self.seleccionar(n, s, c, p))
            self.lista_prod.add_widget(btn)

    def seleccionar(self, nombre, stock, costo, precio):
        self.producto_seleccionado = {
            "nombre": nombre,
            "stock": stock,
            "costo": costo,
            "precio": precio
        }
        self.lbl_seleccionado.text = f"Seleccionado: {nombre.title()}"
        self.lbl_seleccionado.color = COLOR_SECONDARY

    def registrar(self, instance):
        if not self.producto_seleccionado:
            mostrar_popup("Error", "Selecciona un producto primero.", COLOR_DANGER)
            return

        try:
            litros = float(self.litros.text.strip() or 0)
            if litros <= 0:
                raise ValueError
        except ValueError:
            mostrar_popup("Error", "Ingresa una cantidad válida de litros.", COLOR_DANGER)
            return

        if litros > self.producto_seleccionado["stock"]:
            mostrar_popup(
                "Stock insuficiente",
                f"Solo tienes {self.producto_seleccionado['stock']:.1f} L disponibles.",
                COLOR_DANGER
            )
            return

        nombre = self.producto_seleccionado["nombre"]
        costo = self.producto_seleccionado["costo"]
        precio = self.producto_seleccionado["precio"]
        total_venta = litros * precio
        total_costo = litros * costo
        ganancia = total_venta - total_costo
        nuevo_stock = self.producto_seleccionado["stock"] - litros

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE productos SET stock_litros = ? WHERE nombre = ?",
            (nuevo_stock, nombre)
        )
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        cursor.execute(
            "INSERT INTO movimientos (fecha, tipo, producto, litros, monto_total, ganancia) VALUES (?, 'VENTA', ?, ?, ?, ?)",
            (fecha, nombre, litros, total_venta, ganancia)
        )
        conn.commit()
        conn.close()

        mostrar_popup(
            "Venta registrada",
            f"Venta: ${total_venta:,.2f}\nGanancia neta: ${ganancia:,.2f}",
            COLOR_SECONDARY
        )
        self.cargar_productos()

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class BalanceScreen(Screen):
    def on_enter(self):
        self.actualizar()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(15))

        root.add_widget(Label(
            text="BALANCE FINANCIERO",
            font_size="22sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        self.lbl_inversion = Label(
            text="Total Invertido: $0.00",
            font_size="17sp",
            color=COLOR_TEXT,
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(self.lbl_inversion)

        self.lbl_ventas = Label(
            text="Total Ventas Brutas: $0.00",
            font_size="17sp",
            color=COLOR_TEXT,
            size_hint_y=None,
            height=dp(40)
        )
        root.add_widget(self.lbl_ventas)

        self.lbl_ganancia = Label(
            text="Ganancia Neta: $0.00",
            font_size="20sp",
            bold=True,
            color=COLOR_SECONDARY,
            size_hint_y=None,
            height=dp(50)
        )
        root.add_widget(self.lbl_ganancia)

        root.add_widget(Label(size_hint_y=0.4))

        btn_volver = Button(
            text="← Volver al Menú",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def actualizar(self):
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()

        cursor.execute("SELECT SUM(monto_total) FROM movimientos WHERE tipo = 'ENTRADA'")
        total_inv = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(monto_total) FROM movimientos WHERE tipo = 'VENTA'")
        total_ventas = cursor.fetchone()[0] or 0.0

        cursor.execute("SELECT SUM(ganancia) FROM movimientos WHERE tipo = 'VENTA'")
        total_gan = cursor.fetchone()[0] or 0.0

        conn.close()

        self.lbl_inversion.text = f"Total Invertido (Compras):  ${total_inv:,.2f}"
        self.lbl_ventas.text = f"Total Ventas Brutas:  ${total_ventas:,.2f}"
        self.lbl_ganancia.text = f"Ganancia Neta Acumulada:  ${total_gan:,.2f}"

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class EliminarScreen(Screen):
    def on_enter(self):
        self.cargar_productos()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(10))

        root.add_widget(Label(
            text="ELIMINAR PRODUCTO",
            font_size="22sp",
            bold=True,
            color=COLOR_DANGER,
            size_hint_y=None,
            height=dp(45)
        ))

        root.add_widget(Label(
            text="Toca el producto que deseas eliminar:",
            size_hint_y=None,
            height=dp(30),
            color=COLOR_TEXT
        ))

        self.scroll = ScrollView(do_scroll_x=False)
        self.lista_prod = GridLayout(cols=1, spacing=dp(6), size_hint_y=None)
        self.lista_prod.bind(minimum_height=self.lista_prod.setter("height"))
        self.scroll.add_widget(self.lista_prod)
        root.add_widget(self.scroll)

        btn_volver = Button(
            text="← Volver",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def cargar_productos(self):
        self.lista_prod.clear_widgets()
        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute("SELECT nombre, stock_litros FROM productos ORDER BY nombre")
        rows = cursor.fetchall()
        conn.close()

        if not rows:
            self.lista_prod.add_widget(Label(
                text="No hay productos para eliminar.",
                color=(0.5, 0.5, 0.55, 1),
                size_hint_y=None,
                height=dp(40)
            ))
            return

        for nombre, stock in rows:
            btn = Button(
                text=f"{nombre.title()}  (Stock: {stock:.1f} L)",
                size_hint_y=None,
                height=dp(50),
                background_color=(0.95, 0.85, 0.85, 1),
                background_normal="",
                color=COLOR_DANGER,
                font_size="15sp"
            )
            btn.bind(on_release=lambda inst, n=nombre: self.confirmar_eliminar(n))
            self.lista_prod.add_widget(btn)

    def confirmar_eliminar(self, nombre):
        content = BoxLayout(orientation="vertical", padding=dp(20), spacing=dp(15))
        content.add_widget(Label(
            text=f"¿Estás seguro de eliminar\n'{nombre.title()}'?",
            color=COLOR_TEXT,
            halign="center",
            font_size="16sp"
        ))

        btns = BoxLayout(spacing=dp(10), size_hint_y=None, height=dp(45))
        btn_si = Button(text="Sí, eliminar", background_color=COLOR_DANGER, background_normal="")
        btn_no = Button(text="Cancelar", background_color=(0.5, 0.5, 0.55, 1), background_normal="")

        popup = Popup(
            title="Confirmar eliminación",
            content=content,
            size_hint=(0.85, 0.4),
            auto_dismiss=False
        )

        def eliminar(instance):
            conn = sqlite3.connect(get_db_path())
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
            conn.commit()
            conn.close()
            popup.dismiss()
            mostrar_popup("Eliminado", f"Producto '{nombre.title()}' eliminado.", COLOR_SECONDARY)
            self.cargar_productos()

        btn_si.bind(on_release=eliminar)
        btn_no.bind(on_release=popup.dismiss)
        btns.add_widget(btn_si)
        btns.add_widget(btn_no)
        content.add_widget(btns)
        popup.open()

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


class CredencialesScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.build_ui()

    def build_ui(self):
        root = BoxLayout(orientation="vertical", padding=dp(25), spacing=dp(10))

        root.add_widget(Label(
            text="CAMBIAR CREDENCIALES",
            font_size="20sp",
            bold=True,
            color=COLOR_PRIMARY,
            size_hint_y=None,
            height=dp(45)
        ))

        root.add_widget(Label(text="Usuario actual", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.usu_actual = TextInput(multiline=False, size_hint_y=None, height=dp(45), font_size="15sp", padding=[dp(10), dp(10)])
        root.add_widget(self.usu_actual)

        root.add_widget(Label(text="Contraseña actual", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.pwd_actual = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(45), font_size="15sp", padding=[dp(10), dp(10)])
        root.add_widget(self.pwd_actual)

        root.add_widget(Label(text="Nuevo usuario", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.nuevo_usu = TextInput(multiline=False, size_hint_y=None, height=dp(45), font_size="15sp", padding=[dp(10), dp(10)])
        root.add_widget(self.nuevo_usu)

        root.add_widget(Label(text="Nueva contraseña", size_hint_y=None, height=dp(25), color=COLOR_TEXT))
        self.nuevo_pwd = TextInput(password=True, multiline=False, size_hint_y=None, height=dp(45), font_size="15sp", padding=[dp(10), dp(10)])
        root.add_widget(self.nuevo_pwd)

        root.add_widget(Label(size_hint_y=0.05))

        btn_guardar = Button(
            text="ACTUALIZAR CREDENCIALES",
            size_hint_y=None,
            height=dp(50),
            background_color=(0.45, 0.35, 0.65, 1),
            background_normal="",
            font_size="15sp",
            bold=True
        )
        btn_guardar.bind(on_release=self.actualizar)
        root.add_widget(btn_guardar)

        btn_volver = Button(
            text="← Volver",
            size_hint_y=None,
            height=dp(48),
            background_color=(0.4, 0.4, 0.45, 1),
            background_normal=""
        )
        btn_volver.bind(on_release=lambda x: self.volver())
        root.add_widget(btn_volver)

        self.add_widget(root)

    def actualizar(self, instance):
        usu = self.usu_actual.text.strip().lower()
        pwd = self.pwd_actual.text.strip()
        nuevo_u = self.nuevo_usu.text.strip().lower()
        nuevo_p = self.nuevo_pwd.text.strip()

        if not all([usu, pwd, nuevo_u, nuevo_p]):
            mostrar_popup("Error", "Completa todos los campos.", COLOR_DANGER)
            return

        conn = sqlite3.connect(get_db_path())
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id FROM usuarios WHERE usuario = ? AND password = ?",
            (usu, pwd)
        )
        if not cursor.fetchone():
            conn.close()
            mostrar_popup("Error", "Usuario o contraseña actual incorrectos.", COLOR_DANGER)
            return

        try:
            cursor.execute(
                "UPDATE usuarios SET usuario = ?, password = ? WHERE usuario = ?",
                (nuevo_u, nuevo_p, usu)
            )
            conn.commit()
            conn.close()
            mostrar_popup("Éxito", f"Credenciales actualizadas.\nNuevo usuario: {nuevo_u}", COLOR_SECONDARY)
            self.usu_actual.text = ""
            self.pwd_actual.text = ""
            self.nuevo_usu.text = ""
            self.nuevo_pwd.text = ""
        except sqlite3.IntegrityError:
            conn.close()
            mostrar_popup("Error", "Ese nombre de usuario ya existe.", COLOR_DANGER)

    def volver(self):
        self.manager.transition.direction = "right"
        self.manager.current = "menu"


# ==================== APP PRINCIPAL ====================

class InventarioApp(App):
    def build(self):
        # Inicializar base de datos
        init_db()

        # Configurar color de fondo
        Window.clearcolor = COLOR_BG

        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(LoginScreen(name="login"))
        sm.add_widget(MenuScreen(name="menu"))
        sm.add_widget(InventarioScreen(name="inventario"))
        sm.add_widget(AgregarProductoScreen(name="agregar"))
        sm.add_widget(EntradaScreen(name="entrada"))
        sm.add_widget(SalidaScreen(name="salida"))
        sm.add_widget(BalanceScreen(name="balance"))
        sm.add_widget(EliminarScreen(name="eliminar"))
        sm.add_widget(CredencialesScreen(name="credenciales"))

        return sm


if __name__ == "__main__":
    InventarioApp().run()
