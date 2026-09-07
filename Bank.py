import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
import json
import os
from datetime import datetime, timedelta
import hashlib
import re
import random
import sys

# Intentar importar winsound (solo Windows)
try:
    import winsound
    SOUND_AVAILABLE = True
except ImportError:
    SOUND_AVAILABLE = False

DB_FILE = "aura_banco_corporativo.json"

def cargar_datos():
    """Carga los datos desde el archivo JSON"""
    if os.path.exists(DB_FILE):
        try:
            with open(DB_FILE, "r", encoding="utf-8") as f:
                datos = json.load(f)
                # Asegurar campos básicos
                if "usuarios" not in datos:
                    datos["usuarios"] = {}
                if "inflacion" not in datos:
                    datos["inflacion"] = 1.0
                if "logros" not in datos:
                    datos["logros"] = {}
                return datos
        except (json.JSONDecodeError, IOError):
            print("Error al cargar datos, creando nueva base de datos")
    return {"usuarios": {}, "inflacion": 1.0, "logros": {}}

def guardar_datos(datos):
    """Guarda los datos en el archivo JSON"""
    try:
        with open(DB_FILE, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=4, ensure_ascii=False)
        return True
    except IOError as e:
        print(f"Error al guardar datos: {e}")
        return False

def hash_password(password):
    """Encripta la contraseña usando SHA-256 con salt"""
    salt = "aura_salt_2024"
    return hashlib.sha256((salt + password).encode()).hexdigest()

def play_sound(frequency=1000, duration=100):
    """Reproduce un sonido simple si está disponible"""
    if SOUND_AVAILABLE:
        try:
            winsound.Beep(frequency, duration)
        except:
            pass

# ============ CLASES DE MINIJUEGOS (con recompensas reducidas) ============

class FlappyBirdGame:
    """Minijuego de Flappy Bird (recompensa reducida a 50 por punto)"""
    def __init__(self, parent, color_fondo, color_texto):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🎮 Flappy Bird")
        self.ventana.geometry("400x600")
        self.ventana.configure(bg="#87CEEB")
        self.ventana.resizable(False, False)
       
        self.canvas = tk.Canvas(self.ventana, width=400, height=600, bg="#87CEEB", highlightthickness=0)
        self.canvas.pack()
       
        self.pajaro_y = 300
        self.pajaro_x = 100
        self.velocidad = 0
        self.gravedad = 0.5
        self.salto = -10
        self.tuberias = []
        self.puntuacion = 0
        self.juego_activo = True
        self.pausa = False
        self.tuberia_velocidad = 5
        self.tuberia_ancho = 60
        self.espacio_tuberias = 200
        self.tuberia_frecuencia = 100
        self.frame_count = 0
        self.dificultad = 1
        self.recompensa_por_punto = 50  # Reducido de 100
       
        self.pajaro = self.canvas.create_oval(
            self.pajaro_x - 15, self.pajaro_y - 15,
            self.pajaro_x + 15, self.pajaro_y + 15,
            fill="#FFD700", outline="#FFA500", width=2
        )
        self.ojo = self.canvas.create_oval(
            self.pajaro_x + 2, self.pajaro_y - 10,
            self.pajaro_x + 8, self.pajaro_y - 4,
            fill="white", outline="black"
        )
        self.pico = self.canvas.create_polygon(
            self.pajaro_x + 10, self.pajaro_y - 2,
            self.pajaro_x + 20, self.pajaro_y + 3,
            self.pajaro_x + 10, self.pajaro_y + 8,
            fill="#FF6347"
        )
       
        self.label_puntuacion = tk.Label(self.ventana, text="Puntuación: 0",
                                        font=("Segoe UI", 16, "bold"),
                                        bg="#87CEEB", fg="white")
        self.label_puntuacion.place(x=10, y=10)
       
        self.nubes = []
        for _ in range(3):
            x = random.randint(0, 400)
            y = random.randint(20, 150)
            nube = self.canvas.create_oval(x, y, x+60, y+30, fill="white", outline="")
            self.nubes.append(nube)
       
        self.suelo = self.canvas.create_rectangle(0, 560, 400, 600, fill="#8B4513", outline="")
       
        self.ventana.bind("<space>", lambda e: self.saltar())
        self.ventana.bind("<Button-1>", lambda e: self.saltar())
        self.ventana.bind("<Up>", lambda e: self.saltar())
        self.ventana.bind("<p>", lambda e: self.toggle_pausa())
        self.ventana.bind("<P>", lambda e: self.toggle_pausa())
       
        self.canvas.create_text(200, 250,
                               text="ESPACIO/CLICK: saltar\nP: pausa",
                               font=("Segoe UI", 12, "bold"),
                               fill="white", justify="center")
       
        self.resultado = 0
        self.actualizar()
       
    def saltar(self):
        if self.juego_activo and not self.pausa:
            self.velocidad = self.salto
            play_sound(800, 50)
           
    def toggle_pausa(self):
        if self.juego_activo:
            self.pausa = not self.pausa
            if self.pausa:
                self.canvas.create_text(200, 300, text="PAUSA", font=("Segoe UI", 24, "bold"), fill="red", tags="pausa")
            else:
                self.canvas.delete("pausa")
                self.actualizar()
           
    def crear_tuberia(self):
        altura_tuberia = random.randint(50, 350)
        espacio = self.espacio_tuberias
       
        tuberia_superior = self.canvas.create_rectangle(
            400, 0,
            400 + self.tuberia_ancho, altura_tuberia,
            fill="#228B22", outline="#006400", width=2
        )
        tuberia_inferior = self.canvas.create_rectangle(
            400, altura_tuberia + espacio,
            400 + self.tuberia_ancho, 560,
            fill="#228B22", outline="#006400", width=2
        )
        self.tuberias.append({
            "superior": tuberia_superior,
            "inferior": tuberia_inferior,
            "x": 400,
            "altura": altura_tuberia,
            "pasada": False
        })
       
    def actualizar(self):
        if not self.juego_activo or self.pausa:
            return
           
        self.velocidad += self.gravedad
        self.pajaro_y += self.velocidad
       
        self.canvas.coords(self.pajaro,
                          self.pajaro_x - 15, self.pajaro_y - 15,
                          self.pajaro_x + 15, self.pajaro_y + 15)
        self.canvas.coords(self.ojo,
                          self.pajaro_x + 2, self.pajaro_y - 10,
                          self.pajaro_x + 8, self.pajaro_y - 4)
        self.canvas.coords(self.pico,
                          self.pajaro_x + 10, self.pajaro_y - 2,
                          self.pajaro_x + 20, self.pajaro_y + 3,
                          self.pajaro_x + 10, self.pajaro_y + 8)
       
        for nube in self.nubes:
            self.canvas.move(nube, -1, 0)
            if self.canvas.coords(nube)[0] < -60:
                self.canvas.move(nube, 460, 0)
       
        self.frame_count += 1
        if self.frame_count % self.tuberia_frecuencia == 0:
            self.crear_tuberia()
            self.frame_count = 0
       
        tuberias_a_eliminar = []
        for tuberia in self.tuberias:
            tuberia["x"] -= self.tuberia_velocidad
            self.canvas.coords(tuberia["superior"],
                              tuberia["x"], 0,
                              tuberia["x"] + self.tuberia_ancho, tuberia["altura"])
            self.canvas.coords(tuberia["inferior"],
                              tuberia["x"], tuberia["altura"] + self.espacio_tuberias,
                              tuberia["x"] + self.tuberia_ancho, 560)
           
            if self.verificar_colision(tuberia):
                self.fin_juego()
                return
           
            if not tuberia["pasada"] and tuberia["x"] + self.tuberia_ancho < self.pajaro_x:
                tuberia["pasada"] = True
                self.puntuacion += 1
                self.label_puntuacion.config(text=f"Puntuación: {self.puntuacion}")
                if self.puntuacion % 5 == 0:
                    self.dificultad += 1
                    self.tuberia_velocidad = 5 + self.dificultad * 0.5
                    self.tuberia_frecuencia = max(60, 100 - self.dificultad * 10)
                play_sound(1200, 30)
           
            if tuberia["x"] + self.tuberia_ancho < 0:
                tuberias_a_eliminar.append(tuberia)
       
        for tuberia in tuberias_a_eliminar:
            self.canvas.delete(tuberia["superior"])
            self.canvas.delete(tuberia["inferior"])
            self.tuberias.remove(tuberia)
       
        if self.pajaro_y > 560 or self.pajaro_y < 0:
            self.fin_juego()
            return
       
        self.ventana.after(20, self.actualizar)
       
    def verificar_colision(self, tuberia):
        if (self.pajaro_x + 15 > tuberia["x"] and
            self.pajaro_x - 15 < tuberia["x"] + self.tuberia_ancho and
            self.pajaro_y - 15 < tuberia["altura"]):
            return True
        if (self.pajaro_x + 15 > tuberia["x"] and
            self.pajaro_x - 15 < tuberia["x"] + self.tuberia_ancho and
            self.pajaro_y + 15 > tuberia["altura"] + self.espacio_tuberias):
            return True
        return False
       
    def fin_juego(self):
        self.juego_activo = False
        self.resultado = self.puntuacion * self.recompensa_por_punto
        play_sound(300, 300)
       
        self.canvas.create_rectangle(100, 250, 300, 350, fill="white", outline="black")
        self.canvas.create_text(200, 280,
                               text="¡Juego Terminado!",
                               font=("Segoe UI", 16, "bold"),
                               fill="black")
        self.canvas.create_text(200, 310,
                               text=f"Puntuación: {self.puntuacion}",
                               font=("Segoe UI", 12),
                               fill="black")
        self.canvas.create_text(200, 330,
                               text=f"Recompensa: ${self.resultado}",
                               font=("Segoe UI", 12, "bold"),
                               fill="#10b981")
       
        tk.Button(self.ventana, text="Cerrar",
                 font=("Segoe UI", 10, "bold"),
                 bg="#ef4444", fg="white", bd=0,
                 command=self.ventana.destroy).place(x=175, y=360)


class BlockBlastGame:
    """Minijuego Block Blast (recompensa reducida a 50 por línea)"""
    def __init__(self, parent, color_fondo, color_texto):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🎮 Block Blast")
        self.ventana.geometry("400x600")
        self.ventana.configure(bg="#1a1a2e")
        self.ventana.resizable(False, False)
       
        self.canvas = tk.Canvas(self.ventana, width=400, height=500, bg="#16213e", highlightthickness=0)
        self.canvas.pack()
       
        self.tablero = [[0 for _ in range(8)] for _ in range(8)]
        self.tamano_celda = 50
        self.puntuacion = 0
        self.combo = 1
        self.bloques_disponibles = []
        self.recompensa_por_linea = 50  # Reducido de 100
       
        self.label_puntuacion = tk.Label(self.ventana, text="Puntuación: 0",
                                        font=("Segoe UI", 16, "bold"),
                                        bg="#1a1a2e", fg="white")
        self.label_puntuacion.pack(pady=5)
        self.label_combo = tk.Label(self.ventana, text="",
                                   font=("Segoe UI", 10),
                                   bg="#1a1a2e", fg="#f59e0b")
        self.label_combo.pack()
       
        self.crear_bloques_disponibles()
        self.dibujar_tablero()
        self.canvas.bind("<Button-1>", self.click_tablero)
        self.resultado = 0
       
    def crear_bloques_disponibles(self):
        self.bloques_disponibles = []
        formas = [
            [(0, 0)],
            [(0, 0), (1, 0)],
            [(0, 0), (0, 1)],
            [(0, 0), (1, 0), (0, 1)],
            [(0, 0), (1, 0), (1, 1)],
            [(0, 0), (1, 0), (2, 0)],
            [(0, 0), (0, 1), (0, 2)],
            [(0, 0), (1, 0), (0, 1), (1, 1)],
            [(0, 0), (1, 0), (2, 0), (1, 1)],
            [(0, 0), (1, 0), (1, 1), (2, 1)],
            [(0, 0), (1, 0), (2, 0), (0, 1)],
            [(0, 0), (1, 0), (2, 0), (2, 1)]
        ]
        for _ in range(3):
            forma = random.choice(formas)
            color = random.choice(["#ef4444", "#10b981", "#38bdf8", "#f59e0b", "#8b5cf6"])
            self.bloques_disponibles.append({"forma": forma, "color": color})
           
    def dibujar_tablero(self):
        self.canvas.delete("all")
        for i in range(8):
            for j in range(8):
                x1 = j * self.tamano_celda
                y1 = i * self.tamano_celda
                x2 = x1 + self.tamano_celda
                y2 = y1 + self.tamano_celda
                color = "#1e3a5f" if self.tablero[i][j] == 0 else self.tablero[i][j]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#2a4a6f")
        for idx, bloque in enumerate(self.bloques_disponibles):
            x_offset = 20 + idx * 130
            y_offset = 520
            for dx, dy in bloque["forma"]:
                x1 = x_offset + dx * 40
                y1 = y_offset + dy * 40
                x2 = x1 + 40
                y2 = y1 + 40
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bloque["color"],
                                           outline="white", width=2)
               
    def click_tablero(self, event):
        if not self.bloques_disponibles:
            return
        col = event.x // self.tamano_celda
        fila = event.y // self.tamano_celda
        if fila >= 8 or col >= 8:
            return
        bloque = self.bloques_disponibles[0]
        if self.colocar_bloque(bloque, fila, col):
            self.bloques_disponibles.pop(0)
            lineas = self.verificar_lineas()
            if lineas > 0:
                self.combo += 1
                self.puntuacion += lineas * self.recompensa_por_linea * self.combo
                self.label_combo.config(text=f"Combo x{self.combo}")
            else:
                self.combo = 1
                self.label_combo.config(text="")
            self.crear_bloques_disponibles()
            self.dibujar_tablero()
            self.label_puntuacion.config(text=f"Puntuación: {self.puntuacion}")
            if not self.puede_colocar():
                self.fin_juego()
               
    def colocar_bloque(self, bloque, fila, col):
        for dx, dy in bloque["forma"]:
            nueva_fila = fila + dy
            nueva_col = col + dx
            if nueva_fila >= 8 or nueva_col >= 8 or nueva_fila < 0 or nueva_col < 0:
                return False
            if self.tablero[nueva_fila][nueva_col] != 0:
                return False
        for dx, dy in bloque["forma"]:
            nueva_fila = fila + dy
            nueva_col = col + dx
            self.tablero[nueva_fila][nueva_col] = bloque["color"]
        return True
       
    def verificar_lineas(self):
        lineas_eliminadas = 0
        filas_completas = [i for i in range(8) if all(self.tablero[i][j] != 0 for j in range(8))]
        columnas_completas = [j for j in range(8) if all(self.tablero[i][j] != 0 for i in range(8))]
        for fila in filas_completas:
            for j in range(8):
                self.tablero[fila][j] = 0
            lineas_eliminadas += 1
        for columna in columnas_completas:
            for i in range(8):
                self.tablero[i][columna] = 0
            lineas_eliminadas += 1
        return lineas_eliminadas
           
    def puede_colocar(self):
        for bloque in self.bloques_disponibles:
            for i in range(8):
                for j in range(8):
                    if self.colocar_bloque_check(bloque, i, j):
                        return True
        return False
       
    def colocar_bloque_check(self, bloque, fila, col):
        for dx, dy in bloque["forma"]:
            nueva_fila = fila + dy
            nueva_col = col + dx
            if nueva_fila >= 8 or nueva_col >= 8 or nueva_fila < 0 or nueva_col < 0:
                return False
            if self.tablero[nueva_fila][nueva_col] != 0:
                return False
        return True
       
    def fin_juego(self):
        self.resultado = self.puntuacion
        self.canvas.create_rectangle(50, 200, 350, 300, fill="white", outline="black")
        self.canvas.create_text(200, 230,
                               text="¡Juego Terminado!",
                               font=("Segoe UI", 16, "bold"),
                               fill="black")
        self.canvas.create_text(200, 260,
                               text=f"Puntuación: {self.puntuacion}",
                               font=("Segoe UI", 12),
                               fill="black")
        self.canvas.create_text(200, 280,
                               text=f"Recompensa: ${self.resultado}",
                               font=("Segoe UI", 12, "bold"),
                               fill="#10b981")
        tk.Button(self.ventana, text="Cerrar",
                 font=("Segoe UI", 10, "bold"),
                 bg="#ef4444", fg="white", bd=0,
                 command=self.ventana.destroy).place(x=175, y=310)


class TetrisGame:
    """Tetris (recompensas reducidas)"""
    def __init__(self, parent, color_fondo, color_texto):
        self.ventana = tk.Toplevel(parent)
        self.ventana.title("🎮 Tetris")
        self.ventana.geometry("400x600")
        self.ventana.configure(bg="#1a1a2e")
        self.ventana.resizable(False, False)
       
        self.canvas = tk.Canvas(self.ventana, width=300, height=500, bg="#16213e", highlightthickness=0)
        self.canvas.pack(side="left", padx=10)
       
        info_frame = tk.Frame(self.ventana, bg="#1a1a2e", width=80)
        info_frame.pack(side="right", fill="y", padx=10)
        info_frame.pack_propagate(False)
       
        tk.Label(info_frame, text="Puntuación:", font=("Segoe UI", 10, "bold"),
                bg="#1a1a2e", fg="white").pack(pady=5)
        self.label_puntuacion = tk.Label(info_frame, text="0",
                                        font=("Segoe UI", 14, "bold"),
                                        bg="#1a1a2e", fg="#10b981")
        self.label_puntuacion.pack(pady=5)
       
        tk.Label(info_frame, text="Nivel:", font=("Segoe UI", 10, "bold"),
                bg="#1a1a2e", fg="white").pack(pady=5)
        self.label_nivel = tk.Label(info_frame, text="1",
                                   font=("Segoe UI", 14, "bold"),
                                   bg="#1a1a2e", fg="#38bdf8")
        self.label_nivel.pack(pady=5)
       
        # Vista previa y hold
        tk.Label(info_frame, text="Siguiente:", font=("Segoe UI", 10, "bold"),
                bg="#1a1a2e", fg="white").pack(pady=5)
        self.preview_canvas = tk.Canvas(info_frame, width=80, height=80, bg="#16213e", highlightthickness=0)
        self.preview_canvas.pack()
       
        tk.Label(info_frame, text="Hold (C):", font=("Segoe UI", 10, "bold"),
                bg="#1a1a2e", fg="white").pack(pady=5)
        self.hold_canvas = tk.Canvas(info_frame, width=80, height=80, bg="#16213e", highlightthickness=0)
        self.hold_canvas.pack()
       
        self.tablero = [[0 for _ in range(10)] for _ in range(20)]
        self.tamano_celda = 25
        self.pieza_actual = None
        self.siguiente_pieza = None
        self.pieza_hold = None
        self.puede_hold = True
        self.pieza_x = 0
        self.pieza_y = 0
        self.puntuacion = 0
        self.nivel = 1
        self.velocidad = 500
        self.juego_activo = True
        self.pausa = False
        self.recompensa_multiplier = 0.5  # Reducido: ahora cada punto vale 0.5, antes 1
       
        self.piezas = [
            {"forma": [(0, 0), (1, 0), (0, 1), (1, 1)], "color": "#f59e0b"},
            {"forma": [(0, 0), (1, 0), (2, 0), (3, 0)], "color": "#38bdf8"},
            {"forma": [(0, 0), (1, 0), (1, 1), (2, 1)], "color": "#10b981"},
            {"forma": [(1, 0), (2, 0), (0, 1), (1, 1)], "color": "#ef4444"},
            {"forma": [(0, 0), (0, 1), (0, 2), (1, 2)], "color": "#8b5cf6"},
            {"forma": [(1, 0), (1, 1), (1, 2), (0, 2)], "color": "#f59e0b"},
            {"forma": [(0, 0), (1, 0), (2, 0), (1, 1)], "color": "#ec4899"}
        ]
       
        self.ventana.bind("<Left>", lambda e: self.mover(-1))
        self.ventana.bind("<Right>", lambda e: self.mover(1))
        self.ventana.bind("<Down>", lambda e: self.mover_abajo())
        self.ventana.bind("<Up>", lambda e: self.rotar())
        self.ventana.bind("<space>", lambda e: self.soltar())
        self.ventana.bind("<c>", lambda e: self.hold())
        self.ventana.bind("<C>", lambda e: self.hold())
        self.ventana.bind("<p>", lambda e: self.toggle_pausa())
        self.ventana.bind("<P>", lambda e: self.toggle_pausa())
       
        self.resultado = 0
        self.crear_pieza()
        self.actualizar()
       
    def crear_pieza(self):
        if self.siguiente_pieza is None:
            self.pieza_actual = random.choice(self.piezas)
            self.siguiente_pieza = random.choice(self.piezas)
        else:
            self.pieza_actual = self.siguiente_pieza
            self.siguiente_pieza = random.choice(self.piezas)
        self.pieza_x = 3
        self.pieza_y = 0
        self.puede_hold = True
        if self.colision(self.pieza_actual["forma"], self.pieza_x, self.pieza_y):
            self.fin_juego()
        self.actualizar_preview()
           
    def colision(self, forma, x, y):
        for dx, dy in forma:
            nueva_x = x + dx
            nueva_y = y + dy
            if nueva_x < 0 or nueva_x >= 10 or nueva_y >= 20:
                return True
            if nueva_y >= 0 and self.tablero[nueva_y][nueva_x] != 0:
                return True
        return False
       
    def mover(self, direccion):
        if not self.juego_activo or self.pausa:
            return
        nueva_x = self.pieza_x + direccion
        if not self.colision(self.pieza_actual["forma"], nueva_x, self.pieza_y):
            self.pieza_x = nueva_x
            self.dibujar()
           
    def mover_abajo(self):
        if not self.juego_activo or self.pausa:
            return
        if not self.colision(self.pieza_actual["forma"], self.pieza_x, self.pieza_y + 1):
            self.pieza_y += 1
            self.dibujar()
        else:
            self.fijar_pieza()
           
    def rotar(self):
        if not self.juego_activo or self.pausa:
            return
        nueva_forma = [(-dy, dx) for dx, dy in self.pieza_actual["forma"]]
        if not self.colision(nueva_forma, self.pieza_x, self.pieza_y):
            self.pieza_actual["forma"] = nueva_forma
            self.dibujar()
           
    def soltar(self):
        if not self.juego_activo or self.pausa:
            return
        while not self.colision(self.pieza_actual["forma"], self.pieza_x, self.pieza_y + 1):
            self.pieza_y += 1
        self.fijar_pieza()
       
    def hold(self):
        if not self.juego_activo or self.pausa or not self.puede_hold:
            return
        if self.pieza_hold is None:
            self.pieza_hold = self.pieza_actual
            self.crear_pieza()
        else:
            temp = self.pieza_actual
            self.pieza_actual = self.pieza_hold
            self.pieza_hold = temp
            self.pieza_x = 3
            self.pieza_y = 0
            self.puede_hold = False
        self.actualizar_hold()
        self.dibujar()
       
    def toggle_pausa(self):
        if self.juego_activo:
            self.pausa = not self.pausa
            if self.pausa:
                self.canvas.create_text(150, 250, text="PAUSA", font=("Segoe UI", 24, "bold"), fill="red", tags="pausa")
            else:
                self.canvas.delete("pausa")
                self.actualizar()
               
    def fijar_pieza(self):
        for dx, dy in self.pieza_actual["forma"]:
            nueva_x = self.pieza_x + dx
            nueva_y = self.pieza_y + dy
            if nueva_y >= 0:
                self.tablero[nueva_y][nueva_x] = self.pieza_actual["color"]
        lineas = self.verificar_lineas()
        if lineas > 0:
            puntos = [0, 100, 300, 500, 800]
            self.puntuacion += int(puntos[min(lineas, 4)] * self.recompensa_multiplier)
            self.label_puntuacion.config(text=str(self.puntuacion))
            self.nivel = self.puntuacion // 1000 + 1
            self.label_nivel.config(text=str(self.nivel))
            self.velocidad = max(100, 500 - (self.nivel - 1) * 50)
        self.crear_pieza()
        self.dibujar()
       
    def verificar_lineas(self):
        lineas_eliminadas = 0
        i = 19
        while i >= 0:
            if all(self.tablero[i][j] != 0 for j in range(10)):
                for j in range(10):
                    self.tablero[i][j] = 0
                for k in range(i, 0, -1):
                    for j in range(10):
                        self.tablero[k][j] = self.tablero[k-1][j]
                lineas_eliminadas += 1
            else:
                i -= 1
        return lineas_eliminadas
           
    def dibujar(self):
        self.canvas.delete("all")
        for i in range(20):
            for j in range(10):
                x1 = j * self.tamano_celda
                y1 = i * self.tamano_celda
                x2 = x1 + self.tamano_celda
                y2 = y1 + self.tamano_celda
                color = "#1e3a5f" if self.tablero[i][j] == 0 else self.tablero[i][j]
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#2a4a6f")
        if self.pieza_actual:
            for dx, dy in self.pieza_actual["forma"]:
                x = self.pieza_x + dx
                y = self.pieza_y + dy
                if y >= 0:
                    x1 = x * self.tamano_celda
                    y1 = y * self.tamano_celda
                    x2 = x1 + self.tamano_celda
                    y2 = y1 + self.tamano_celda
                    self.canvas.create_rectangle(x1, y1, x2, y2,
                                               fill=self.pieza_actual["color"],
                                               outline="white", width=2)
                                               
    def actualizar_preview(self):
        self.preview_canvas.delete("all")
        if self.siguiente_pieza:
            min_x = min(dx for dx, _ in self.siguiente_pieza["forma"])
            min_y = min(dy for _, dy in self.siguiente_pieza["forma"])
            for dx, dy in self.siguiente_pieza["forma"]:
                x = (dx - min_x) * 20 + 10
                y = (dy - min_y) * 20 + 10
                self.preview_canvas.create_rectangle(x, y, x+20, y+20, fill=self.siguiente_pieza["color"], outline="white")
               
    def actualizar_hold(self):
        self.hold_canvas.delete("all")
        if self.pieza_hold:
            min_x = min(dx for dx, _ in self.pieza_hold["forma"])
            min_y = min(dy for _, dy in self.pieza_hold["forma"])
            for dx, dy in self.pieza_hold["forma"]:
                x = (dx - min_x) * 20 + 10
                y = (dy - min_y) * 20 + 10
                self.hold_canvas.create_rectangle(x, y, x+20, y+20, fill=self.pieza_hold["color"], outline="white")
                                               
    def actualizar(self):
        if not self.juego_activo or self.pausa:
            return
        self.mover_abajo()
        self.ventana.after(self.velocidad, self.actualizar)
       
    def fin_juego(self):
        self.juego_activo = False
        self.resultado = self.puntuacion  # Ya está multiplicado por el factor
        self.canvas.create_rectangle(25, 200, 275, 300, fill="white", outline="black")
        self.canvas.create_text(150, 230,
                               text="¡Juego Terminado!",
                               font=("Segoe UI", 16, "bold"),
                               fill="black")
        self.canvas.create_text(150, 260,
                               text=f"Puntuación: {self.puntuacion}",
                               font=("Segoe UI", 12),
                               fill="black")
        self.canvas.create_text(150, 280,
                               text=f"Recompensa: ${self.resultado}",
                               font=("Segoe UI", 12, "bold"),
                               fill="#10b981")
        tk.Button(self.ventana, text="Cerrar",
                 font=("Segoe UI", 10, "bold"),
                 bg="#ef4444", fg="white", bd=0,
                 command=self.ventana.destroy).place(x=125, y=310)


# ============ CLASE PRINCIPAL CON INFLACIÓN Y MERCADO ============
class AuraBancoPremium:
    def __init__(self, root):
        self.root = root
        self.root.title("AURA | Banca Corporativa Premium")
        self.root.geometry("600x700")
        self.root.configure(bg="#0a0e17")
        self.root.resizable(False, False)
       
        self.colores = {
            "bg_principal": "#0a0e17",
            "bg_secundario": "#131a26",
            "bg_terciario": "#1a2536",
            "bg_card": "#1e2a3a",
            "texto_principal": "#e2e8f0",
            "texto_secundario": "#94a3b8",
            "texto_tenue": "#64748b",
            "acento_principal": "#38bdf8",
            "acento_secundario": "#818cf8",
            "exito": "#10b981",
            "error": "#ef4444",
            "advertencia": "#f59e0b",
            "info": "#06b6d4",
            "borde": "#2a3b4d",
            "sombra": "#00000040"
        }
       
        self.configurar_estilos()
        self.datos = cargar_datos()
        self.usuario_actual = None
        self.intentos_fallidos = {}
        self.verificar_expiracion_cuentas()
        self.centrar_ventana()
        self.pantalla_inicio()
        self.logros = self.datos.get("logros", {})
       
    def cargar_logros(self):
        return self.datos.get("logros", {})
           
    def guardar_logros(self):
        self.datos["logros"] = self.logros
        guardar_datos(self.datos)
       
    def otorgar_logro(self, usuario, logro):
        if usuario not in self.logros:
            self.logros[usuario] = []
        if logro not in self.logros[usuario]:
            self.logros[usuario].append(logro)
            self.guardar_logros()
            messagebox.showinfo("¡Logro desbloqueado!", f"Has obtenido el logro: {logro}")
       
    def configurar_estilos(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       bg=self.colores["bg_card"],
                       fg=self.colores["texto_principal"],
                       fieldbg=self.colores["bg_card"],
                       rowheight=30,
                       borderwidth=0,
                       font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                       bg=self.colores["bg_terciario"],
                       fg=self.colores["acento_principal"],
                       font=("Segoe UI", 10, "bold"),
                       borderwidth=0)
        style.map("Treeview",
                 background=[("selected", self.colores["acento_principal"])],
                 foreground=[("selected", "#ffffff")])

    def centrar_ventana(self):
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def verificar_expiracion_cuentas(self):
        ahora = datetime.now()
        usuarios_a_eliminar = []
        for usuario, datos in self.datos["usuarios"].items():
            if "ultimo_acceso" in datos:
                try:
                    ultimo_acceso = datetime.strptime(datos["ultimo_acceso"], "%Y-%m-%d %H:%M:%S")
                    diferencia = ahora - ultimo_acceso
                    if diferencia > timedelta(hours=24):
                        usuarios_a_eliminar.append(usuario)
                except ValueError:
                    usuarios_a_eliminar.append(usuario)
        for usuario in usuarios_a_eliminar:
            del self.datos["usuarios"][usuario]
        if usuarios_a_eliminar:
            guardar_datos(self.datos)
            messagebox.showwarning("Cuentas Eliminadas",
                                 f"Se eliminaron {len(usuarios_a_eliminar)} cuenta(s) por inactividad.")

    def limpiar_pantalla(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def crear_boton_premium(self, parent, texto, comando, color, width=300, height=45, icono=""):
        btn = tk.Button(parent,
                       text=f"{icono} {texto}" if icono else texto,
                       font=("Segoe UI", 10, "bold"),
                       bg=color,
                       fg="white",
                       bd=0,
                       height=2,
                       width=width,
                       cursor="hand2",
                       command=comando,
                       activebackground=self.ajustar_color(color, -20),
                       activeforeground="white",
                       relief="flat",
                       pady=8)
        return btn

    def ajustar_color(self, color_hex, ajuste):
        color_hex = color_hex.lstrip('#')
        r, g, b = tuple(int(color_hex[i:i+2], 16) for i in (0, 2, 4))
        r = max(0, min(255, r + ajuste))
        g = max(0, min(255, g + ajuste))
        b = max(0, min(255, b + ajuste))
        return f'#{r:02x}{g:02x}{b:02x}'

    def pantalla_inicio(self):
        self.limpiar_pantalla()
        self.root.geometry("600x700")
        main_frame = tk.Frame(self.root, bg=self.colores["bg_principal"])
        main_frame.pack(fill="both", expand=True)
        logo_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        logo_frame.pack(pady=60)
        logo_canvas = tk.Canvas(logo_frame, width=100, height=100, bg=self.colores["bg_principal"], highlightthickness=0)
        logo_canvas.pack()
        logo_canvas.create_oval(5, 5, 95, 95, fill=self.colores["bg_terciario"], outline=self.colores["acento_principal"], width=3)
        logo_canvas.create_text(50, 50, text="A", font=("Segoe UI", 40, "bold"), fill=self.colores["acento_principal"])
        tk.Label(logo_frame, text="AURA", font=("Segoe UI", 32, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(pady=10)
        tk.Label(logo_frame, text="BANCA CORPORATIVA PREMIUM", font=("Segoe UI", 11, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(pady=5)
        linea_canvas = tk.Canvas(logo_frame, width=300, height=2, bg=self.colores["bg_principal"], highlightthickness=0)
        linea_canvas.pack(pady=10)
        linea_canvas.create_line(0, 0, 100, 0, fill=self.colores["acento_principal"], width=2)
        linea_canvas.create_line(100, 0, 200, 0, fill=self.colores["bg_terciario"], width=2)
        linea_canvas.create_line(200, 0, 300, 0, fill=self.colores["acento_secundario"], width=2)
        info_frame = tk.Frame(main_frame, bg=self.colores["bg_secundario"], highlightbackground=self.colores["borde"], highlightthickness=1)
        info_frame.pack(pady=20, padx=40, fill="x")
        tk.Label(info_frame, text="⚠️ Seguridad Premium", font=("Segoe UI", 9, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["advertencia"]).pack(pady=5)
        tk.Label(info_frame, text="Las cuentas inactivas por 24 horas\nserán eliminadas automáticamente", font=("Segoe UI", 8), bg=self.colores["bg_secundario"], fg=self.colores["texto_secundario"]).pack(pady=5)
        botones_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        botones_frame.pack(pady=30)
        btn_login = self.crear_boton_premium(botones_frame, "Acceder a mi Banca", self.pantalla_login, self.colores["acento_principal"], icono="🔐")
        btn_login.pack(pady=10)
        btn_registro = self.crear_boton_premium(botones_frame, "Abrir Cuenta Corporativa", self.pantalla_registro, self.colores["exito"], icono="💼")
        btn_registro.pack(pady=10)
        tk.Label(main_frame, text="© 2024 AURA Bank - Todos los derechos reservados", font=("Segoe UI", 8), bg=self.colores["bg_principal"], fg=self.colores["texto_tenue"]).pack(side="bottom", pady=10)

    def pantalla_login(self):
        self.limpiar_pantalla()
        self.root.geometry("600x700")
        main_frame = tk.Frame(self.root, bg=self.colores["bg_principal"])
        main_frame.pack(fill="both", expand=True)
        header_frame = tk.Frame(main_frame, bg=self.colores["bg_secundario"])
        header_frame.pack(fill="x", pady=(0, 30))
        tk.Label(header_frame, text="🔐 Acceso Seguro", font=("Segoe UI", 20, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["texto_principal"]).pack(pady=20)
        form_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        form_frame.pack(pady=30, padx=50, fill="both")
        tk.Label(form_frame, text="ID de Usuario", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(anchor="w", pady=(10, 5))
        ent_usuario = tk.Entry(form_frame, font=("Segoe UI", 12), bg=self.colores["bg_card"], fg=self.colores["texto_principal"], bd=0, insertbackground=self.colores["texto_principal"], relief="flat")
        ent_usuario.pack(fill="x", ipady=12, pady=(0, 15))
        tk.Label(form_frame, text="Contraseña", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(anchor="w", pady=(10, 5))
        ent_clave = tk.Entry(form_frame, font=("Segoe UI", 12), bg=self.colores["bg_card"], fg=self.colores["texto_principal"], bd=0, show="•", insertbackground=self.colores["texto_principal"], relief="flat")
        ent_clave.pack(fill="x", ipady=12, pady=(0, 20))
        def verificar_credenciales():
            user = ent_usuario.get().strip()
            clave = ent_clave.get().strip()
            if not user or not clave:
                messagebox.showwarning("Atención", "Por favor complete todos los campos.")
                return
            if user in self.intentos_fallidos:
                if self.intentos_fallidos[user]["intentos"] >= 3:
                    tiempo_restante = datetime.now() - self.intentos_fallidos[user]["ultimo_intento"]
                    if tiempo_restante < timedelta(minutes=5):
                        messagebox.showerror("Cuenta Bloqueada", f"Demasiados intentos fallidos.\nIntente nuevamente en {5 - tiempo_restante.seconds // 60} minutos.")
                        return
                    else:
                        del self.intentos_fallidos[user]
            clave_hash = hash_password(clave)
            if user in self.datos["usuarios"] and self.datos["usuarios"][user]["clave"] == clave_hash:
                self.usuario_actual = user
                self.registrar_acceso(user)
                self.pantalla_dashboard()
            else:
                if user not in self.intentos_fallidos:
                    self.intentos_fallidos[user] = {"intentos": 0, "ultimo_intento": datetime.now()}
                self.intentos_fallidos[user]["intentos"] += 1
                self.intentos_fallidos[user]["ultimo_intento"] = datetime.now()
                intentos_restantes = 3 - self.intentos_fallidos[user]["intentos"]
                if intentos_restantes > 0:
                    messagebox.showerror("Acceso Denegado", f"Credenciales incorrectas.\n\nIntentos restantes: {intentos_restantes}")
                else:
                    messagebox.showerror("Cuenta Bloqueada", "Ha excedido el número máximo de intentos.\nSu cuenta ha sido bloqueada por 5 minutos.")
        btn_login = self.crear_boton_premium(form_frame, "Ingresar", verificar_credenciales, self.colores["acento_principal"])
        btn_login.pack(pady=20)
        btn_regresar = self.crear_boton_premium(form_frame, "Regresar", self.pantalla_inicio, self.colores["bg_terciario"])
        btn_regresar.pack(pady=5)

    def pantalla_registro(self):
        self.limpiar_pantalla()
        self.root.geometry("600x700")
        main_frame = tk.Frame(self.root, bg=self.colores["bg_principal"])
        main_frame.pack(fill="both", expand=True)
        header_frame = tk.Frame(main_frame, bg=self.colores["bg_secundario"])
        header_frame.pack(fill="x", pady=(0, 20))
        tk.Label(header_frame, text="💼 Registro Corporativo", font=("Segoe UI", 20, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["texto_principal"]).pack(pady=20)
        form_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        form_frame.pack(pady=20, padx=50, fill="both")
        tk.Label(form_frame, text="Nombre de Usuario", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(anchor="w", pady=(10, 5))
        ent_usuario = tk.Entry(form_frame, font=("Segoe UI", 12), bg=self.colores["bg_card"], fg=self.colores["texto_principal"], bd=0, insertbackground=self.colores["texto_principal"], relief="flat")
        ent_usuario.pack(fill="x", ipady=12, pady=(0, 10))
        tk.Label(form_frame, text="Contraseña", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(anchor="w", pady=(10, 5))
        ent_clave = tk.Entry(form_frame, font=("Segoe UI", 12), bg=self.colores["bg_card"], fg=self.colores["texto_principal"], bd=0, show="•", insertbackground=self.colores["texto_principal"], relief="flat")
        ent_clave.pack(fill="x", ipady=12, pady=(0, 10))
        tk.Label(form_frame, text="Confirmar Contraseña", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(anchor="w", pady=(10, 5))
        ent_confirmar = tk.Entry(form_frame, font=("Segoe UI", 12), bg=self.colores["bg_card"], fg=self.colores["texto_principal"], bd=0, show="•", insertbackground=self.colores["texto_principal"], relief="flat")
        ent_confirmar.pack(fill="x", ipady=12, pady=(0, 15))
        def registrar_cuenta():
            user = ent_usuario.get().strip()
            clave = ent_clave.get().strip()
            confirmar = ent_confirmar.get().strip()
            if not user or not clave or not confirmar:
                messagebox.showwarning("Atención", "Todos los campos son obligatorios.")
                return
            if len(user) < 3:
                messagebox.showwarning("Atención", "El nombre de usuario debe tener al menos 3 caracteres.")
                return
            if not re.match("^[a-zA-Z0-9_]+$", user):
                messagebox.showwarning("Atención", "El nombre de usuario solo puede contener letras, números y guiones bajos.")
                return
            if len(clave) < 6:
                messagebox.showwarning("Atención", "La contraseña debe tener al menos 6 caracteres.")
                return
            if clave != confirmar:
                messagebox.showerror("Error", "Las contraseñas no coinciden.")
                return
            if user in self.datos["usuarios"]:
                messagebox.showerror("Error", "Este ID ya se encuentra asignado.")
                return
            fecha_actual = datetime.now()
            self.datos["usuarios"][user] = {
                "clave": hash_password(clave),
                "cuentas": {
                    "corriente": 100.00,
                    "ahorros": 50.00,
                    "credito_limite": 1000.00,
                    "credito_deuda": 0.00
                },
                "historial": [
                    {"fecha": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"), "tipo": "Apertura", "monto": 100.00, "detalles": "Bono de Cuenta Corriente"},
                    {"fecha": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"), "tipo": "Apertura", "monto": 50.00, "detalles": "Bono de Cuenta de Ahorros"}
                ],
                "ultimo_acceso": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"),
                "fecha_creacion": fecha_actual.strftime("%Y-%m-%d %H:%M:%S"),
                "mejoras": {
                    "interes": 0.15,
                    "comision_retiro": 0.02,
                    "limite_credito": 1000.00,
                    "recompensa_bonus": 0.0
                }
            }
            if guardar_datos(self.datos):
                messagebox.showinfo("¡Felicidades!", "¡Tu cuenta corporativa ha sido creada exitosamente!\n\nBono de bienvenida:\n• Cuenta Corriente: $100.00\n• Cuenta de Ahorros: $50.00\n• Límite de Crédito: $1,000.00\n\n🎮 Gana más corporativos jugando:\n• Flappy Bird\n• Block Blast\n• Tetris\n\n⚠️ Recuerda iniciar sesión cada 24 horas.")
                self.pantalla_inicio()
            else:
                messagebox.showerror("Error", "No se pudo guardar la información.")
        btn_registro = self.crear_boton_premium(form_frame, "Activar Cuenta", registrar_cuenta, self.colores["exito"])
        btn_registro.pack(pady=15)
        btn_cancelar = self.crear_boton_premium(form_frame, "Cancelar", self.pantalla_inicio, self.colores["bg_terciario"])
        btn_cancelar.pack(pady=5)

    def registrar_acceso(self, usuario):
        self.datos["usuarios"][usuario]["ultimo_acceso"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        guardar_datos(self.datos)

    def pantalla_dashboard(self):
        self.limpiar_pantalla()
        self.root.geometry("600x700")
        if not self.usuario_actual:
            self.pantalla_login()
            return
        self.datos = cargar_datos()
        user_data = self.datos["usuarios"][self.usuario_actual]
        cuentas = user_data["cuentas"]
        main_frame = tk.Frame(self.root, bg=self.colores["bg_principal"])
        main_frame.pack(fill="both", expand=True)
        header_frame = tk.Frame(main_frame, bg=self.colores["bg_secundario"])
        header_frame.pack(fill="x", pady=(0, 20))
        info_usuario = tk.Frame(header_frame, bg=self.colores["bg_secundario"])
        info_usuario.pack(side="left", padx=20, pady=15)
        tk.Label(info_usuario, text=f"👤 {self.usuario_actual}", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_secundario"], fg=self.colores["texto_principal"]).pack(anchor="w")
        if "ultimo_acceso" in user_data:
            tk.Label(info_usuario, text=f"Último acceso: {user_data['ultimo_acceso']}", font=("Segoe UI", 8), bg=self.colores["bg_secundario"], fg=self.colores["texto_tenue"]).pack(anchor="w")
        # Mostrar inflación global
        inflacion = self.datos.get("inflacion", 1.0)
        tk.Label(info_usuario, text=f"Índice de valor: {inflacion:.3f}", font=("Segoe UI", 8), bg=self.colores["bg_secundario"], fg=self.colores["advertencia"]).pack(anchor="w")
        tk.Button(header_frame, text="Cerrar Sesión", font=("Segoe UI", 9, "bold"), bg=self.colores["error"], fg="white", bd=0, cursor="hand2", padx=15, pady=8, command=self.cerrar_sesion).pack(side="right", padx=20, pady=15)
        resumen_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        resumen_frame.pack(fill="x", padx=20, pady=10)
        tk.Label(resumen_frame, text="💳 Resumen de Cuentas", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(anchor="w", pady=10)
        grid_frame = tk.Frame(resumen_frame, bg=self.colores["bg_principal"])
        grid_frame.pack(fill="x", pady=5)
        cuentas_info = [
            ("Cuenta Corriente", cuentas["corriente"], "💵", self.colores["exito"]),
            ("Cuenta de Ahorros", cuentas["ahorros"], "🏦", self.colores["info"]),
            ("Crédito Disponible", cuentas["credito_limite"] - cuentas["credito_deuda"], "💳", self.colores["advertencia"]),
            ("Deuda de Crédito", cuentas["credito_deuda"], "📊", self.colores["error"])
        ]
        for i, (nombre, valor, icono, color) in enumerate(cuentas_info):
            fila = i // 2
            columna = i % 2
            card = tk.Frame(grid_frame, bg=self.colores["bg_card"], highlightbackground=self.colores["borde"], highlightthickness=1)
            card.grid(row=fila, column=columna, padx=5, pady=5, sticky="nsew")
            tk.Label(card, text=f"{icono} {nombre}", font=("Segoe UI", 8), bg=self.colores["bg_card"], fg=self.colores["texto_secundario"]).pack(anchor="w", padx=10, pady=(10, 5))
            tk.Label(card, text=f"${valor:,.2f}", font=("Segoe UI", 12, "bold"), bg=self.colores["bg_card"], fg=color).pack(anchor="w", padx=10, pady=(0, 10))
        grid_frame.grid_columnconfigure(0, weight=1)
        grid_frame.grid_columnconfigure(1, weight=1)
        operaciones_frame = tk.Frame(main_frame, bg=self.colores["bg_principal"])
        operaciones_frame.pack(fill="x", padx=20, pady=20)
        tk.Label(operaciones_frame, text="⚡ Operaciones Rápidas", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(anchor="w", pady=10)
        ops_grid = tk.Frame(operaciones_frame, bg=self.colores["bg_principal"])
        ops_grid.pack(fill="x", pady=5)
        botones = [
            ("Minijuegos", self.op_minijuegos, self.colores["exito"], "🎮"),
            ("Transferir", self.op_transferencia, self.colores["acento_principal"], "💸"),
            ("Retirar", self.op_retiro, "#f97316", "🏧"),
            ("Invertir", self.op_inversion, "#8b5cf6", "📈"),
            ("Usar Tarjeta", self.op_usar_tarjeta, "#f59e0b", "💳"),
            ("Pagar Tarjeta", self.op_pagar_tarjeta, "#06b6d4", "💰"),
            ("Historial", self.op_historial, self.colores["bg_terciario"], "📜"),
            ("Mercado", self.abrir_mercado, "#ec4899", "🛒"),
            ("Logros", self.ver_logros, "#ec4899", "🏆")
        ]
        for i, (texto, comando, color, icono) in enumerate(botones):
            fila = i // 3
            columna = i % 3
            btn = tk.Button(ops_grid, text=f"{icono}\n{texto}", font=("Segoe UI", 9, "bold"), bg=color, fg="white", bd=0, cursor="hand2", command=comando, activebackground=self.ajustar_color(color, -20), activeforeground="white", relief="flat", height=2)
            btn.grid(row=fila, column=columna, padx=3, pady=3, sticky="nsew")
        for i in range(3):
            ops_grid.grid_columnconfigure(i, weight=1)

    def op_retiro(self):
        monto = simpledialog.askfloat("Retiro", "¿Cuánto deseas retirar? (Comisión actual: 2%)")
        if not monto or monto <= 0:
            return
        self.datos = cargar_datos()
        cuentas = self.datos["usuarios"][self.usuario_actual]["cuentas"]
        mejoras = self.datos["usuarios"][self.usuario_actual].get("mejoras", {})
        comision = monto * mejoras.get("comision_retiro", 0.02)
        total = monto + comision
        if total > cuentas["corriente"]:
            messagebox.showerror("Error", "Fondos insuficientes (incluye comisión).")
            return
        cuentas["corriente"] -= total
        self.datos["usuarios"][self.usuario_actual]["historial"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "Retiro",
            "monto": monto,
            "detalles": f"Retiro en efectivo (comisión: ${comision:.2f})"
        })
        guardar_datos(self.datos)
        messagebox.showinfo("Retiro exitoso", f"Retiraste ${monto:.2f}. Comisión: ${comision:.2f}. Total debitado: ${total:.2f}")
        self.pantalla_dashboard()

    def op_inversion(self):
        monto = simpledialog.askfloat("Inversiones", "Cantidad a invertir (interés actual: 15%):")
        if not monto or monto <= 0:
            return
        self.datos = cargar_datos()
        saldo_corr = self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"]
        if monto > saldo_corr:
            messagebox.showerror("Error", "Fondos insuficientes.")
            return
        mejoras = self.datos["usuarios"][self.usuario_actual].get("mejoras", {})
        interes = monto * mejoras.get("interes", 0.15)
        total = monto + interes
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"] -= monto
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["ahorros"] += total
        self.datos["usuarios"][self.usuario_actual]["historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tipo": "Plazo Fijo", "monto": monto, "detalles": f"Rendimiento neto: +${interes:,.2f}"})
        guardar_datos(self.datos)
        self.otorgar_logro(self.usuario_actual, "Inversionista")
        messagebox.showinfo("Inversión Exitosa", f"Total a recibir: ${total:,.2f}")
        self.pantalla_dashboard()

    def op_usar_tarjeta(self):
        tienda = simpledialog.askstring("Pasarela Crédito", "¿En qué tienda compras?")
        if not tienda:
            return
        monto = simpledialog.askfloat("Margen", "Monto del consumo:")
        if not monto or monto <= 0:
            return
        self.datos = cargar_datos()
        cuentas = self.datos["usuarios"][self.usuario_actual]["cuentas"]
        disponible = cuentas["credito_limite"] - cuentas["credito_deuda"]
        if monto > disponible:
            messagebox.showerror("Cancelada", "Excediste tu límite de crédito.")
            return
        cuentas["credito_deuda"] += monto
        self.datos["usuarios"][self.usuario_actual]["historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tipo": "Consumo Tarjeta", "monto": monto, "detalles": f"Compra en {tienda}"})
        guardar_datos(self.datos)
        messagebox.showinfo("Compra Exitosa", f"Compra en {tienda} por ${monto:,.2f}")
        self.pantalla_dashboard()

    def op_pagar_tarjeta(self):
        self.datos = cargar_datos()
        deuda = self.datos["usuarios"][self.usuario_actual]["cuentas"]["credito_deuda"]
        if deuda <= 0:
            messagebox.showinfo("Al día", "No registras deudas.")
            return
        monto = simpledialog.askfloat("Abonar", f"Deuda actual: ${deuda:,.2f}. ¿Cuánto deseas pagar?")
        if not monto or monto <= 0:
            return
        saldo_corr = self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"]
        if monto > saldo_corr:
            messagebox.showerror("Error", "Dinero insuficiente.")
            return
        if monto > deuda:
            messagebox.showwarning("Error", "No puedes pagar más de lo que debes.")
            return
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"] -= monto
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["credito_deuda"] -= monto
        self.datos["usuarios"][self.usuario_actual]["historial"].append({"fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "tipo": "Pago Tarjeta", "monto": monto, "detalles": "Amortización de saldo deudor"})
        guardar_datos(self.datos)
        messagebox.showinfo("Pago Exitoso", f"Deuda restante: ${deuda - monto:,.2f}")
        self.pantalla_dashboard()

    def op_transferencia(self):
        destinatario = simpledialog.askstring("Transferencia", "Introduce el nombre del usuario destino:")
        if not destinatario:
            return
        destinatario = destinatario.strip()
        self.datos = cargar_datos()
        if destinatario not in self.datos["usuarios"]:
            messagebox.showerror("Error", "El usuario destino no existe.")
            return
        if destinatario == self.usuario_actual:
            messagebox.showwarning("Atención", "No puedes transferir fondos a ti mismo.")
            return
        monto = simpledialog.askfloat("Monto", f"¿Cuánto enviarás a {destinatario}?\nSaldo disponible: ${self.datos['usuarios'][self.usuario_actual]['cuentas']['corriente']:,.2f}")
        if not monto or monto <= 0:
            return
        saldo_origen = self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"]
        if monto > saldo_origen:
            messagebox.showerror("Rechazado", "Saldo insuficiente.")
            return
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"] -= monto
        self.datos["usuarios"][destinatario]["cuentas"]["corriente"] += monto
        fecha_act = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.datos["usuarios"][self.usuario_actual]["historial"].append({"fecha": fecha_act, "tipo": "Transferencia Enviada", "monto": monto, "detalles": f"Fondos a {destinatario}"})
        self.datos["usuarios"][destinatario]["historial"].append({"fecha": fecha_act, "tipo": "Transferencia Recibida", "monto": monto, "detalles": f"Fondos de {self.usuario_actual}"})
        guardar_datos(self.datos)
        self.otorgar_logro(self.usuario_actual, "Primera transferencia")
        messagebox.showinfo("Éxito", f"Transferencia completada por ${monto:,.2f}")
        self.pantalla_dashboard()

    def op_minijuegos(self):
        ventana_minijuegos = tk.Toplevel(self.root)
        ventana_minijuegos.title("🎮 Minijuegos")
        ventana_minijuegos.geometry("400x400")
        ventana_minijuegos.configure(bg=self.colores["bg_principal"])
        ventana_minijuegos.resizable(False, False)
        frame = tk.Frame(ventana_minijuegos, bg=self.colores["bg_principal"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame, text="🎮 Gana Corporativos", font=("Segoe UI", 16, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(pady=10)
        tk.Label(frame, text="Elige un minijuego (recompensas ajustadas por inflación)", font=("Segoe UI", 10), bg=self.colores["bg_principal"], fg=self.colores["texto_secundario"]).pack(pady=10)
        btn_flappy = self.crear_boton_premium(frame, "Flappy Bird", self.jugar_flappy_bird, "#38bdf8", icono="🐦")
        btn_flappy.pack(pady=10)
        btn_block = self.crear_boton_premium(frame, "Block Blast", self.jugar_block_blast, "#f59e0b", icono="🧱")
        btn_block.pack(pady=10)
        btn_tetris = self.crear_boton_premium(frame, "Tetris", self.jugar_tetris, "#8b5cf6", icono="🎯")
        btn_tetris.pack(pady=10)
        tk.Button(ventana_minijuegos, text="Cerrar", font=("Segoe UI", 10), bg=self.colores["bg_terciario"], fg="white", bd=0, cursor="hand2", command=ventana_minijuegos.destroy).pack(pady=10)

    def jugar_flappy_bird(self):
        juego = FlappyBirdGame(self.root, self.colores["bg_principal"], self.colores["texto_principal"])
        self.root.wait_window(juego.ventana)
        if juego.resultado > 0:
            # Aplicar inflación y bonus de mejoras
            bonus = self.datos["usuarios"][self.usuario_actual].get("mejoras", {}).get("recompensa_bonus", 0.0)
            recompensa_final = int(juego.resultado * (1 + bonus) * self.datos.get("inflacion", 1.0))
            self.agregar_recompensa(recompensa_final, "Flappy Bird")
            self.otorgar_logro(self.usuario_actual, "Primer vuelo")

    def jugar_block_blast(self):
        juego = BlockBlastGame(self.root, self.colores["bg_principal"], self.colores["texto_principal"])
        self.root.wait_window(juego.ventana)
        if juego.resultado > 0:
            bonus = self.datos["usuarios"][self.usuario_actual].get("mejoras", {}).get("recompensa_bonus", 0.0)
            recompensa_final = int(juego.resultado * (1 + bonus) * self.datos.get("inflacion", 1.0))
            self.agregar_recompensa(recompensa_final, "Block Blast")
            self.otorgar_logro(self.usuario_actual, "Constructor")

    def jugar_tetris(self):
        juego = TetrisGame(self.root, self.colores["bg_principal"], self.colores["texto_principal"])
        self.root.wait_window(juego.ventana)
        if juego.resultado > 0:
            bonus = self.datos["usuarios"][self.usuario_actual].get("mejoras", {}).get("recompensa_bonus", 0.0)
            recompensa_final = int(juego.resultado * (1 + bonus) * self.datos.get("inflacion", 1.0))
            self.agregar_recompensa(recompensa_final, "Tetris")
            self.otorgar_logro(self.usuario_actual, "Maestro del Tetris")

    def agregar_recompensa(self, monto, juego):
        self.datos = cargar_datos()
        self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"] += monto
        self.datos["usuarios"][self.usuario_actual]["historial"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "Minijuego",
            "monto": monto,
            "detalles": f"Recompensa por {juego}"
        })
        # Aumentar inflación un 0.5% por cada recompensa
        self.datos["inflacion"] = self.datos.get("inflacion", 1.0) * 0.995
        guardar_datos(self.datos)
        messagebox.showinfo("Recompensa", f"¡Has ganado ${monto} en {juego}!\nÍndice de valor actualizado.")
        self.pantalla_dashboard()

    def abrir_mercado(self):
        ventana_mercado = tk.Toplevel(self.root)
        ventana_mercado.title("🛒 Mercado de Mejoras")
        ventana_mercado.geometry("400x500")
        ventana_mercado.configure(bg=self.colores["bg_principal"])
        ventana_mercado.resizable(False, False)
        frame = tk.Frame(ventana_mercado, bg=self.colores["bg_principal"])
        frame.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame, text="🛒 Mejoras Disponibles", font=("Segoe UI", 16, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(pady=10)
        # Mostrar saldo
        saldo = self.datos["usuarios"][self.usuario_actual]["cuentas"]["corriente"]
        tk.Label(frame, text=f"Saldo disponible: ${saldo:,.2f}", font=("Segoe UI", 10), bg=self.colores["bg_principal"], fg=self.colores["exito"]).pack(pady=5)
        mejoras = [
            ("Aumentar interés (+5%)", 200, "interes", 0.05),
            ("Reducir comisión retiro (-1%)", 150, "comision_retiro", -0.01),
            ("Aumentar límite crédito (+$500)", 300, "limite_credito", 500),
            ("Aumentar recompensa minijuegos (+10%)", 250, "recompensa_bonus", 0.10)
        ]
        for nombre, costo, clave, valor in mejoras:
            btn = tk.Button(frame, text=f"{nombre} - ${costo}", font=("Segoe UI", 10), bg=self.colores["bg_terciario"], fg="white", bd=0, cursor="hand2", command=lambda c=costo, k=clave, v=valor, n=nombre: self.comprar_mejora(c, k, v, n))
            btn.pack(fill="x", pady=5)
        tk.Button(ventana_mercado, text="Cerrar", font=("Segoe UI", 10), bg=self.colores["bg_terciario"], fg="white", bd=0, cursor="hand2", command=ventana_mercado.destroy).pack(pady=10)

    def comprar_mejora(self, costo, clave, valor, nombre):
        self.datos = cargar_datos()
        usuario = self.usuario_actual
        saldo = self.datos["usuarios"][usuario]["cuentas"]["corriente"]
        if saldo < costo:
            messagebox.showerror("Fondos insuficientes", "No tienes suficientes corporativos.")
            return
        self.datos["usuarios"][usuario]["cuentas"]["corriente"] -= costo
        mejoras = self.datos["usuarios"][usuario].get("mejoras", {})
        if clave in mejoras:
            mejoras[clave] += valor
        else:
            mejoras[clave] = valor
        self.datos["usuarios"][usuario]["mejoras"] = mejoras
        self.datos["usuarios"][usuario]["historial"].append({
            "fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "tipo": "Compra Mejora",
            "monto": costo,
            "detalles": nombre
        })
        guardar_datos(self.datos)
        self.otorgar_logro(usuario, "Comprador")
        messagebox.showinfo("Mejora adquirida", f"Has comprado: {nombre}")
        self.pantalla_dashboard()

    def ver_logros(self):
        logros_usuario = self.logros.get(self.usuario_actual, [])
        if not logros_usuario:
            messagebox.showinfo("Logros", "Aún no tienes logros. ¡Juega y realiza operaciones para desbloquearlos!")
            return
        texto = "🏆 Tus logros:\n\n" + "\n".join(logros_usuario)
        messagebox.showinfo("Logros", texto)

    def op_historial(self):
        self.datos = cargar_datos()
        historial = self.datos["usuarios"][self.usuario_actual]["historial"]
        if not historial:
            messagebox.showinfo("Historial", "No hay operaciones registradas.")
            return
        historial_window = tk.Toplevel(self.root)
        historial_window.title(f"Historial de {self.usuario_actual}")
        historial_window.geometry("700x500")
        historial_window.configure(bg=self.colores["bg_principal"])
        historial_window.resizable(False, False)
        frame_historial = tk.Frame(historial_window, bg=self.colores["bg_principal"])
        frame_historial.pack(fill="both", expand=True, padx=20, pady=20)
        tk.Label(frame_historial, text=f"📜 Historial de Operaciones - {self.usuario_actual}", font=("Segoe UI", 14, "bold"), bg=self.colores["bg_principal"], fg=self.colores["texto_principal"]).pack(pady=10)
        columns = ("fecha", "tipo", "monto", "detalles")
        tree = ttk.Treeview(frame_historial, columns=columns, show="headings", height=15)
        tree.heading("fecha", text="Fecha")
        tree.heading("tipo", text="Tipo")
        tree.heading("monto", text="Monto")
        tree.heading("detalles", text="Detalles")
        tree.column("fecha", width=150)
        tree.column("tipo", width=150)
        tree.column("monto", width=100)
        tree.column("detalles", width=250)
        scrollbar = ttk.Scrollbar(frame_historial, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        for operacion in reversed(historial):
            tree.insert("", "end", values=(operacion["fecha"], operacion["tipo"], f"${operacion['monto']:,.2f}", operacion["detalles"]))
        tk.Button(historial_window, text="Cerrar", font=("Segoe UI", 10, "bold"), bg=self.colores["bg_terciario"], fg="white", bd=0, cursor="hand2", padx=20, pady=8, command=historial_window.destroy).pack(pady=10)

    def cerrar_sesion(self):
        if messagebox.askyesno("Cerrar Sesión", "¿Está seguro que desea cerrar la sesión?"):
            self.usuario_actual = None
            self.pantalla_inicio()

if __name__ == "__main__":
    root = tk.Tk()
    app = AuraBancoPremium(root)
    root.mainloop()
