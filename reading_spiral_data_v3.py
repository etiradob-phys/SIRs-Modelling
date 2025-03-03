# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 03 / 03 / 2025
# --------------------------------------------------------------------------------------------------------------------------------------

import tkinter as tk
import pandas as pd
import re
from tkinter import filedialog

# Ocultar la ventana de Tkinter
root = tk.Tk()
root.withdraw()

# Seleccionar archivo
filename = filedialog.askopenfilename()  
print(f"Archivo seleccionado: {filename}")

# Función para extraer fechas y valores específicos
def extraer_renglones_y_fechas(archivo, renglones_objetivo):
    with open(archivo, 'r') as file:
        lines = file.readlines()

    resultados = []
    frame_lines = []
    fecha_actual = None
    dentro_de_frame = False

    # Expresión regular para extraer la distancia a la Tierra en AU
    distancia_regex = re.compile(r"Distance to Earth \[AU\]:\s*([0-9\.]+)")

    for line in lines:
        # Detecta el inicio de un nuevo frame y extrae la fecha
        if line.startswith("Frame"):
            if frame_lines:  # Guardar el frame anterior antes de procesar el nuevo
                valores = [fecha_actual]
                for renglon in renglones_objetivo:
                    if renglon < len(frame_lines):
                        match = distancia_regex.search(frame_lines[renglon])
                        valores.append(match.group(1) if match else None)
                    else:
                        valores.append(None)
                resultados.append(valores)

            # Reiniciar frame
            fecha_actual = line.split("Date")[1].split("UT:")[0].strip()
            frame_lines = []
            dentro_de_frame = True  # Indicar que estamos dentro de un frame
            continue

        if dentro_de_frame:
            frame_lines.append(line.strip())

    # Procesar el último frame después de salir del bucle
    if frame_lines:
        valores = [fecha_actual]
        for renglon in renglones_objetivo:
            if renglon < len(frame_lines):
                match = distancia_regex.search(frame_lines[renglon])
                valores.append(match.group(1) if match else None)
            else:
                valores.append(None)
        resultados.append(valores)

    # Crear el DataFrame con múltiples columnas
    columnas = ["Date"] + [f"Distance_Row_{r}" for r in renglones_objetivo]
    df = pd.DataFrame(resultados, columns=columnas)
    return df

# Configuración
renglones_a_extraer = [15, 20, 25, 30, 35, 40, 45]  # Renglones de interés

# Ejecutar función
df = extraer_renglones_y_fechas(filename, renglones_a_extraer)

df["Date"] = pd.to_datetime(df["Date"])

# Mostrar el DataFrame
print(df)
