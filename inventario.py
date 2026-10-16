from datetime import datetime
import getpass
import os
import sqlite3


def limpiar_pantalla():
  os.system("cls" if os.name == "nt" else "clear")


# Conexión a la base de datos local
conn = sqlite3.connect("inventario_genericos.db")
cursor = conn.cursor()

# Crear tablas necesarias si no existen
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

# Crear usuario admin por defecto si no existe
cursor.execute("SELECT COUNT(*) FROM usuarios")
if cursor.fetchone()[0] == 0:
  cursor.execute(
      "INSERT INTO usuarios (usuario, password) VALUES (?, ?)",
      ("admin", "1234"),
  )
  conn.commit()


def login():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("   ACCESO AL SISTEMA - GENÉRICOS  ")
    print("==================================")
    print("Por favor, introduce tus datos de acceso.\n")

    usu = input("Usuario: ").strip().lower()
    if not usu:
      continue

    pwd = getpass.getpass("Contraseña: ").strip()

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario = ? AND password = ?",
        (usu, pwd),
    )
    resultado = cursor.fetchone()

    if resultado:
      print(f"\n¡Acceso concedido! Bienvenido, {usu}.")
      input("\nPresiona ENTER para entrar al sistema...")
      return True
    else:
      print("\n❌ Usuario o contraseña incorrectos.")
      op = (
          input(
              "¿Deseas intentar de nuevo? (Presiona ENTER para seguir o 's'"
              " para salir): "
          )
          .strip()
          .lower()
      )
      if op == "s":
        return False


def mostrar_lista_productos():
  cursor.execute(
      "SELECT nombre, stock_litros, costo_litro, precio_litro FROM productos"
  )
  rows = cursor.fetchall()
  if not rows:
    print("📋 (Aún no tienes productos registrados en la base de datos)")
    return False
  else:
    print("📋 PRODUCTOS REGISTRADOS ACTUALMENTE:")
    print("-" * 55)
    print(
        f"{'PRODUCTO':<18} | {'STOCK':<9} | {'COSTO/L':<9} | {'PRECIO/L':<9}"
    )
    print("-" * 55)
    for r in rows:
      print(f"{r[0]:<18} | {r[1]:<6.1f} L | ${r[2]:<8.2f} | ${r[3]:<8.2f}")
    print("-" * 55)
    return True


def cambiar_credenciales():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("   CAMBIAR USUARIO / CONTRASEÑA   ")
    print("==================================")
    print("(Escribe 'atras' para regresar)\n")

    usu_actual = input("Ingresa tu usuario actual: ").strip().lower()
    if usu_actual == "atras":
      return

    pwd_actual = getpass.getpass("Ingresa tu contraseña actual: ").strip()
    if pwd_actual.lower() == "atras":
      return

    cursor.execute(
        "SELECT id FROM usuarios WHERE usuario = ? AND password = ?",
        (usu_actual, pwd_actual),
    )
    resultado = cursor.fetchone()

    if not resultado:
      print(
          "\n❌ El usuario o la contraseña actual son incorrectos. Intenta de"
          " nuevo."
      )
      input("\nPresiona ENTER para continuar...")
      continue

    print("\n✅ Credenciales verificadas correctamente.")
    nuevo_usu = (
        input("Ingresa el NUEVO nombre de usuario: ").strip().lower()
    )
    if not nuevo_usu:
      print("El usuario no puede estar vacío.")
      input("\nPresiona ENTER para continuar...")
      continue

    nuevo_pwd = getpass.getpass("Ingresa la NUEVA contraseña: ").strip()
    if not nuevo_pwd:
      print("La contraseña no puede estar vacía.")
      input("\nPresiona ENTER para continuar...")
      continue

    try:
      cursor.execute(
          "UPDATE usuarios SET usuario = ?, password = ? WHERE usuario = ?",
          (nuevo_usu, nuevo_pwd, usu_actual),
      )
      conn.commit()
      print(
          f"\n🎉 ¡Credenciales actualizadas con éxito! Nuevo usuario:"
          f" {nuevo_usu}"
      )
    except Exception as e:
      print(f"\n⚠️ Error al actualizar (es posible que ese usuario ya exista): {e}")

    input("\nPresiona ENTER para volver al menú...")
    break


def agregar_producto():
  while True:
    limpiar_pantalla()
    print("\n--- AGREGAR NUEVO PRODUCTO ---")
    print("(Escribe 'atras' en cualquier momento para regresar)\n")

    nombre = (
        input("Nombre del producto (ej. Cloro, Cera parafinada): ")
        .strip()
        .lower()
    )
    if nombre == "atras":
      return

    if not nombre:
      print("El nombre no puede estar vacío.")
      input("\nPresiona ENTER para intentar de nuevo...")
      continue

    val_costo = input("Costo de producción/compra por litro ($): ").strip()
    if val_costo.lower() == "atras":
      continue
    try:
      costo = float(val_costo)
    except ValueError:
      print("Valor inválido. Intenta de nuevo.")
      input("\nPresiona ENTER para continuar...")
      continue

    val_precio = input("Precio de venta por litro ($): ").strip()
    if val_precio.lower() == "atras":
      continue
    try:
      precio = float(val_precio)
    except ValueError:
      print("Valor inválido. Intenta de nuevo.")
      input("\nPresiona ENTER para continuar...")
      continue

    try:
      cursor.execute(
          "INSERT INTO productos (nombre, stock_litros, costo_litro,"
          " precio_litro) VALUES (?, 0, ?, ?)",
          (nombre, costo, precio),
      )
      conn.commit()
      print(f"\n✅ ¡Producto '{nombre}' agregado con éxito!")
    except Exception as e:
      print(f"\n⚠️ Error (es posible que el producto ya exista): {e}")

    input("\nPresiona ENTER para volver al menú...")
    break


def registrar_entrada():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("  REGISTRAR ENTRADA (COMPRA/STOCK) ")
    print("==================================")
    print("(Escribe 'atras' para regresar)\n")

    hay_productos = mostrar_lista_productos()
    if not hay_productos:
      input("\nPresiona ENTER para volver al menú...")
      return

    nombre = (
        input("\nEscribe el nombre del producto al que entra stock: ")
        .strip()
        .lower()
    )
    if nombre == "atras":
      return

    cursor.execute(
        "SELECT id, stock_litros, costo_litro FROM productos WHERE nombre = ?",
        (nombre,),
    )
    prod = cursor.fetchone()

    if not prod:
      print(
          f"\n❌ El producto '{nombre}' no existe. Verifícalo en la lista o"
          " agrégalo primero."
      )
      input("\nPresiona ENTER para intentar de nuevo...")
      continue

    val_litros = input("Cantidad de litros que entran al stock: ").strip()
    if val_litros.lower() == "atras":
      continue
    try:
      litros = float(val_litros)
    except ValueError:
      print("Por favor ingresa un número válido.")
      input("\nPresiona ENTER para continuar...")
      continue

    costo_actual = prod[2]
    inversion_total = litros * costo_actual
    nuevo_stock = prod[1] + litros

    cursor.execute(
        "UPDATE productos SET stock_litros = ? WHERE nombre = ?",
        (nuevo_stock, nombre),
    )

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO movimientos (fecha, tipo, producto, litros, monto_total,"
        " ganancia) VALUES (?, 'ENTRADA', ?, ?, ?, 0)",
        (fecha, nombre, litros, inversion_total),
    )
    conn.commit()
    print("\n✅ ¡Entrada registrada con éxito!")
    print(
        f"Litros sumados: {litros} L | Inversión:"
        f" ${inversion_total:,.2f}"
    )
    input("\nPresiona ENTER para volver al menú...")
    break


def registrar_salida():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("    REGISTRAR SALIDA (VENTA)      ")
    print("==================================")
    print("(Escribe 'atras' para regresar)\n")

    hay_productos = mostrar_lista_productos()
    if not hay_productos:
      input("\nPresiona ENTER para volver al menú...")
      return

    nombre = (
        input("\nEscribe el nombre del producto a vender: ").strip().lower()
    )
    if nombre == "atras":
      return

    cursor.execute(
        "SELECT id, stock_litros, costo_litro, precio_litro FROM productos WHERE"
        " nombre = ?",
        (nombre,),
    )
    prod = cursor.fetchone()

    if not prod:
      print(f"\n❌ El producto '{nombre}' no existe en la lista.")
      input("\nPresiona ENTER para intentar de nuevo...")
      continue

    val_litros = input("Cantidad de litros vendidos: ").strip()
    if val_litros.lower() == "atras":
      continue
    try:
      litros = float(val_litros)
    except ValueError:
      print("Por favor ingresa un número válido.")
      input("\nPresiona ENTER para continuar...")
      continue

    if litros > prod[1]:
      print(
          f"\n⚠️ ¡Alerta! Stock insuficiente. Solo tienes {prod[1]} L"
          " disponibles."
      )
      input("\nPresiona ENTER para corregir...")
      continue

    costo_litro = prod[2]
    precio_litro = prod[3]
    total_venta = litros * precio_litro
    total_costo = litros * costo_litro
    ganancia = total_venta - total_costo

    nuevo_stock = prod[1] - litros
    cursor.execute(
        "UPDATE productos SET stock_litros = ? WHERE nombre = ?",
        (nuevo_stock, nombre),
    )

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
    cursor.execute(
        "INSERT INTO movimientos (fecha, tipo, producto, litros, monto_total,"
        " ganancia) VALUES (?, 'VENTA', ?, ?, ?, ?)",
        (fecha, nombre, litros, total_venta, ganancia),
    )
    conn.commit()

    print("\n✅ ¡Venta registrada con éxito!")
    print(f"Dinero recibido (Venta): ${total_venta:,.2f}")
    print(f"Ganancia neta: ${ganancia:,.2f}")
    input("\nPresiona ENTER para volver al menú...")
    break


def eliminar_producto():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("        ELIMINAR PRODUCTO         ")
    print("==================================")
    print("(Escribe 'atras' para regresar)\n")

    hay_productos = mostrar_lista_productos()
    if not hay_productos:
      input("\nPresiona ENTER para volver al menú...")
      return

    nombre = (
        input("\nEscribe el nombre exacto del producto a eliminar: ")
        .strip()
        .lower()
    )
    if nombre == "atras":
      return

    cursor.execute("SELECT id FROM productos WHERE nombre = ?", (nombre,))
    prod = cursor.fetchone()

    if not prod:
      print(f"\n❌ No se encontró el producto '{nombre}'. Revisa bien la lista.")
      input("\nPresiona ENTER para intentar de nuevo...")
      continue

    confirmacion = (
        input(f"¿Estás 100% seguro de eliminar '{nombre}'? (s/n): ")
        .strip()
        .lower()
    )
    if confirmacion == "s":
      cursor.execute("DELETE FROM productos WHERE nombre = ?", (nombre,))
      conn.commit()
      print(f"\n✅ ¡Producto '{nombre}' eliminado con éxito!")
    else:
      print("\nOperación cancelada. No se borró nada.")

    input("\nPresiona ENTER para volver al menú...")
    break


def ver_inventario():
  limpiar_pantalla()
  print("\n--- INVENTARIO ACTUAL (STOCK) ---")
  mostrar_lista_productos()
  input("\nPresiona ENTER para volver al menú...")


def ver_balance():
  limpiar_pantalla()
  print("\n--- BALANCE FINANCIERO GENERAL ---")
  cursor.execute("SELECT SUM(monto_total) FROM movimientos WHERE tipo = 'ENTRADA'")
  total_inv = cursor.fetchone()[0] or 0.0

  cursor.execute("SELECT SUM(ganancia) FROM movimientos WHERE tipo = 'VENTA'")
  total_gan = cursor.fetchone()[0] or 0.0

  cursor.execute("SELECT SUM(monto_total) FROM movimientos WHERE tipo = 'VENTA'")
  total_ventas = cursor.fetchone()[0] or 0.0

  print(f"\nTotal Invertido (Compras/Insumos): ${total_inv:,.2f}")
  print(f"Total Ventas Brutas:              ${total_ventas:,.2f}")
  print(f"Ganancia Neta Acumulada:          ${total_gan:,.2f}")
  input("\nPresiona ENTER para volver al menú...")


def menu():
  while True:
    limpiar_pantalla()
    print("==================================")
    print("   CONTROL DE GENÉRICOS (OFFLINE)")
    print("==================================")
    print("1. Ver Inventario y Stock")
    print("2. Agregar Nuevo Producto")
    print("3. Registrar Entrada (Compra/Insumos)")
    print("4. Registrar Salida (Venta)")
    print("5. Ver Balance (Inversión vs Ganancia)")
    print("6. Eliminar Producto")
    print("7. Cambiar Usuario o Contraseña")
    print("8. Salir")

    op = input("\nElige una opción (1-8): ").strip()

    if op == "1":
      ver_inventario()
    elif op == "2":
      agregar_producto()
    elif op == "3":
      registrar_entrada()
    elif op == "4":
      registrar_salida()
    elif op == "5":
      ver_balance()
    elif op == "6":
      eliminar_producto()
    elif op == "7":
      cambiar_credenciales()
    elif op == "8":
      limpiar_pantalla()
      print("¡Saliendo! Tus datos están seguros.")
      break
    else:
      print("\n⚠️ Opción inválida. Elige un número del 1 al 8.")
      input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
  if login():
    menu()
