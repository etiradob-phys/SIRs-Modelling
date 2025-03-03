# Author: E. Tirado-Bueno (etirado@inaoe.mx)
# Last Update: 03 / 03 / 2025
# --------------------------------------------------------------------------------------------------------------------------------------

import tkinter as tk
from tkinter import filedialog

root = tk.Tk()
root.withdraw()  # Ocultar la ventana de Tkinter

filename = filedialog.askopenfilename()  # Abre un cuadro de diálogo para seleccionar el archivo

print(f"Archivo seleccionado: {filename}")

# --------------------------------------------------------------------------------------------------------------------------------------
