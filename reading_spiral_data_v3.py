# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 03 / 03 / 2025
# --------------------------------------------------------------------------------------------------------------------------------------

import tkinter as tk
import pandas as pd
import re

from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # Ocultar la ventana de Tkinter

filename = filedialog.askopenfilename()  # Abre un cuadro de diálogo para seleccionar el archivo

print(f"Archivo seleccionado: {filename}")

# --------------------------------------------------------------------------------------------------------------------------------------

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
    # Detecta el inicio de un frame y extrae la fecha
    if line.startswith("Frame"):
      fecha_actual = line.split("Date")[1].split("UT:")[0].strip()

      if frame_lines:
          valores = [fecha_actual]
          for renglon in renglones_objetivo:
              if renglon < len(frame_lines):
                  match = distancia_regex.search(frame_lines[renglon])
                  valores.append(match.group(1) if match else None)
              else:
                  valores.append(None)
          resultados.append(valores)

          frame_lines = []
      
      dentro_de_frame = True
  
    if dentro_de_frame:
        frame_lines.append(line.strip())

    # Procesar el último frame
    if frame_lines:
        valores = [fecha_actual]
        for renglon in renglones_objetivo:
            if renglon < len(frame_lines):
                match = distancia_regex.search(frame_lines[renglon])
                valores.append(match.group(1) if match else None)
            else:
                valores.append(None)
        resultados.append(valores)

    # Crear el DataFrame con múltiples columnas para los diferentes renglones
    columnas = ["Date"] + [f"Distance_Row_{r}" for r in renglones_objetivo]
    df = pd.DataFrame(resultados, columns=columnas)
    return df

# Configuración
nombre_archivo = list(filename.keys())[0]  # Obtiene el nombre del archivo subido
renglones_a_extraer = [16,21,26,31,36,41,46]  # Lista de renglones que queremos extraer
