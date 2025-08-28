
# inventario_sqlite.py
# -------------------------------------------------------------
# Sistema Avanzado de Gestión de Inventario (Consola + SQLite)
# Autor: (coloca tu nombre)
# Descripción:
#   - Programa de consola para gestionar productos de una tienda
#   - Estructurado con POO (Producto, Inventario)
#   - Usa colecciones (dict, list, set, tuple) para operaciones eficientes
#   - Persiste la información en SQLite (tabla 'productos')
#
# Instrucciones rápidas de uso:
#   1) python inventario_sqlite.py
#   2) Usa el menú para Añadir / Eliminar / Actualizar / Buscar / Mostrar
#
# Requisitos: Python 3.9+ (probado con la librería estándar)
# -------------------------------------------------------------

from __future__ import annotations
import sqlite3
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

# ---------------------------
# MODELO
# ---------------------------

@dataclass
class Producto:
    id: Optional[int]  # None hasta que se inserta en DB
    nombre: str
    cantidad: int
    precio: float

    # Propiedades para validar entradas (getters/setters implícitos con dataclass)
    def set_cantidad(self, nueva_cantidad: int) -> None:
        if not isinstance(nueva_cantidad, int) or nueva_cantidad < 0:
            raise ValueError("La cantidad debe ser un entero >= 0.")
        self.cantidad = nueva_cantidad

    def set_precio(self, nuevo_precio: float) -> None:
        if not isinstance(nuevo_precio, (int, float)) or nuevo_precio < 0:
            raise ValueError("El precio debe ser un número >= 0.")
        self.precio = float(nuevo_precio)

    def to_tuple(self) -> Tuple[Optional[int], str, int, float]:
        # Útil para depuración o inserciones
        return (self.id, self.nombre, self.cantidad, self.precio)

    def to_dict(self) -> Dict[str, object]:
        return {
            "id": self.id,
            "nombre": self.nombre,
            "cantidad": self.cantidad,
            "precio": self.precio,
        }

# ---------------------------
# REPOSITORIO + CACHÉ (Inventario)
# ---------------------------

class Inventario:
    def __init__(self, db_path: str = "inventario.db") -> None:
        self.db_path = db_path
        # Conexión y configuración de la tabla
        self.conn = sqlite3.connect(self.db_path)
        self.conn.execute(
            """CREATE TABLE IF NOT EXISTS productos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    cantidad INTEGER NOT NULL CHECK (cantidad >= 0),
                    precio REAL NOT NULL CHECK (precio >= 0)
                )"""
        )
        self.conn.commit()

        # Colecciones en memoria para operaciones rápidas
        # - dict: O(1) promedio para acceso por id
        self._productos_por_id: Dict[int, Producto] = {}
        # - dict nombre_idx: nombre normalizado -> set de ids (maneja duplicados de nombre)
        self._nombre_idx: Dict[str, Set[int]] = {}

        # Cargar DB a memoria
        self._cargar_desde_db()

    # ---------------------------
    # Utilidades internas de índice
    # ---------------------------
    def _normaliza(self, s: str) -> str:
        return s.strip().lower()

    def _indexar(self, p: Producto) -> None:
        if p.id is None:
            return
        self._productos_por_id[p.id] = p
        clave = self._normaliza(p.nombre)
        if clave not in self._nombre_idx:
            self._nombre_idx[clave] = set()
        self._nombre_idx[clave].add(p.id)

    def _desindexar(self, p: Producto) -> None:
        if p.id is None:
            return
        self._productos_por_id.pop(p.id, None)
        clave = self._normaliza(p.nombre)
        if clave in self._nombre_idx:
            self._nombre_idx[clave].discard(p.id)
            if not self._nombre_idx[clave]:
                self._nombre_idx.pop(clave, None)

    def _reindexar_nombre(self, p: Producto, nombre_anterior: str) -> None:
        # Cuando cambia el nombre, actualizamos índices
        if p.id is None:
            return
        clave_ant = self._normaliza(nombre_anterior)
        if clave_ant in self._nombre_idx:
            self._nombre_idx[clave_ant].discard(p.id)
            if not self._nombre_idx[clave_ant]:
                self._nombre_idx.pop(clave_ant, None)
        self._indexar(p)

    def _cargar_desde_db(self) -> None:
        self._productos_por_id.clear()
        self._nombre_idx.clear()
        cur = self.conn.execute("SELECT id, nombre, cantidad, precio FROM productos")
        for row in cur.fetchall():
            p = Producto(id=row[0], nombre=row[1], cantidad=row[2], precio=row[3])
            self._indexar(p)

    # ---------------------------
    # Operaciones CRUD
    # ---------------------------
    def anadir_producto(self, nombre: str, cantidad: int, precio: float) -> Producto:
        # Permite productos con el mismo nombre (se distinguen por id)
        if cantidad < 0 or precio < 0:
            raise ValueError("Cantidad y precio deben ser >= 0.")
        cur = self.conn.execute(
            "INSERT INTO productos (nombre, cantidad, precio) VALUES (?, ?, ?)",
            (nombre.strip(), int(cantidad), float(precio)),
        )
        self.conn.commit()
        nuevo_id = cur.lastrowid
        p = Producto(id=nuevo_id, nombre=nombre.strip(), cantidad=int(cantidad), precio=float(precio))
        self._indexar(p)
        return p

    def eliminar_producto(self, prod_id: int) -> bool:
        p = self._productos_por_id.get(prod_id)
        if not p:
            return False
        self.conn.execute("DELETE FROM productos WHERE id = ?", (prod_id,))
        self.conn.commit()
        self._desindexar(p)
        return True

    def actualizar_cantidad(self, prod_id: int, nueva_cantidad: int) -> bool:
        if nueva_cantidad < 0:
            raise ValueError("La cantidad debe ser >= 0.")
        p = self._productos_por_id.get(prod_id)
        if not p:
            return False
        self.conn.execute("UPDATE productos SET cantidad = ? WHERE id = ?", (int(nueva_cantidad), prod_id))
        self.conn.commit()
        p.set_cantidad(int(nueva_cantidad))
        # Índices no cambian (mismo nombre)
        return True

    def actualizar_precio(self, prod_id: int, nuevo_precio: float) -> bool:
        if nuevo_precio < 0:
            raise ValueError("El precio debe ser >= 0.")
        p = self._productos_por_id.get(prod_id)
        if not p:
            return False
        self.conn.execute("UPDATE productos SET precio = ? WHERE id = ?", (float(nuevo_precio), prod_id))
        self.conn.commit()
        p.set_precio(float(nuevo_precio))
        return True

    def actualizar_nombre(self, prod_id: int, nuevo_nombre: str) -> bool:
        p = self._productos_por_id.get(prod_id)
        if not p:
            return False
        nombre_anterior = p.nombre
        self.conn.execute("UPDATE productos SET nombre = ? WHERE id = ?", (nuevo_nombre.strip(), prod_id))
        self.conn.commit()
        p.nombre = nuevo_nombre.strip()
        self._reindexar_nombre(p, nombre_anterior)
        return True

    # ---------------------------
    # Lecturas / Búsquedas
    # ---------------------------
    def obtener_por_id(self, prod_id: int) -> Optional[Producto]:
        return self._productos_por_id.get(prod_id)

    def buscar_por_nombre(self, consulta: str) -> List[Producto]:
        # Búsqueda flexible: primero por coincidencia exacta (índice),
        # luego por subcadena case-insensitive (recorrido en memoria).
        q = self._normaliza(consulta)
        encontrados: List[Producto] = []
        # Coincidencia exacta vía índice
        for prod_id in self._nombre_idx.get(q, set()):
            encontrados.append(self._productos_por_id[prod_id])
        # Coincidencia parcial (subcadena)
        if not encontrados:
            for p in self._productos_por_id.values():
                if q in self._normaliza(p.nombre):
                    encontrados.append(p)
        return encontrados

    def listar_todos(self) -> List[Producto]:
        # Devuelve una lista ordenada por id para visualización estable
        return sorted(self._productos_por_id.values(), key=lambda p: p.id or 0)

    # ---------------------------
    # Cierre
    # ---------------------------
    def cerrar(self) -> None:
        self.conn.close()

# ---------------------------
# Interfaz de Usuario (Consola)
# ---------------------------

def imprimir_producto(p: Producto) -> None:
    print(f"[ID {p.id:03d}] {p.nombre} | Cantidad: {p.cantidad} | Precio: ${p.precio:.2f}")

def menu() -> None:
    inv = Inventario()
    print("=== Sistema Avanzado de Gestión de Inventario (SQLite) ===")
    try:
        while True:
            print("""
------------------------------
1) Añadir producto
2) Eliminar producto (por ID)
3) Actualizar cantidad (por ID)
4) Actualizar precio (por ID)
5) Actualizar nombre (por ID)
6) Buscar por nombre
7) Mostrar todos
0) Salir
------------------------------
            """)
            opcion = input("Elige una opción: ").strip()

            try:
                if opcion == "1":
                    nombre = input("Nombre: ").strip()
                    cantidad = int(input("Cantidad (entero >= 0): "))
                    precio = float(input("Precio (>= 0): "))
                    p = inv.anadir_producto(nombre, cantidad, precio)
                    print("✓ Producto añadido:")
                    imprimir_producto(p)

                elif opcion == "2":
                    prod_id = int(input("ID del producto a eliminar: "))
                    ok = inv.eliminar_producto(prod_id)
                    print("✓ Eliminado" if ok else "✗ ID no encontrado")

                elif opcion == "3":
                    prod_id = int(input("ID del producto: "))
                    nueva = int(input("Nueva cantidad (>= 0): "))
                    ok = inv.actualizar_cantidad(prod_id, nueva)
                    print("✓ Actualizado" if ok else "✗ ID no encontrado")

                elif opcion == "4":
                    prod_id = int(input("ID del producto: "))
                    nuevo = float(input("Nuevo precio (>= 0): "))
                    ok = inv.actualizar_precio(prod_id, nuevo)
                    print("✓ Actualizado" if ok else "✗ ID no encontrado")

                elif opcion == "5":
                    prod_id = int(input("ID del producto: "))
                    nuevo = input("Nuevo nombre: ").strip()
                    ok = inv.actualizar_nombre(prod_id, nuevo)
                    print("✓ Actualizado" if ok else "✗ ID no encontrado")

                elif opcion == "6":
                    consulta = input("Buscar por nombre: ").strip()
                    resultados = inv.buscar_por_nombre(consulta)
                    if resultados:
                        print(f"✓ {len(resultados)} producto(s) encontrados:")
                        for p in resultados:
                            imprimir_producto(p)
                    else:
                        print("✗ Sin coincidencias.")

                elif opcion == "7":
                    productos = inv.listar_todos()
                    if not productos:
                        print("Inventario vacío.")
                    else:
                        for p in productos:
                            imprimir_producto(p)

                elif opcion == "0":
                    print("Hasta luego 👋")
                    break

                else:
                    print("Opción inválida. Intenta de nuevo.")

            except ValueError as ve:
                print(f"Entrada inválida: {ve}")

    finally:
        inv.cerrar()

# ---------------------------
# Punto de entrada
# ---------------------------
if __name__ == "__main__":
    menu()
