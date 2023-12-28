import sys
import numpy as np
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QVBoxLayout, QHBoxLayout, QPushButton
from PyQt5.QtCore import QTimer
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import serial
import threading

# Variables globales
datos = [0] * 2048  # Inicializa el array con 100 elementos con valor 0
datos_cambio = [0] * 2048 # Se inicializa en 0
contador_datos = 0
escala = 20
ventana = [0] * escala
inicio_ventana = 0

lock = threading.Lock()

# Configura el puerto secountrial
ser = serial.Serial('/dev/ttyUSB0', baudrate=460800, timeout=1)  # Reemplaza '/dev/ttyUSB0' con tu puerto USB a UART

def leer_datos_uart():
    global datos, contador_datos,datos_cambio

    while True:
        # Lee datos desde el puerto UART
        data = ser.read(1)  # Lee un byte de datos
        print(data) 
        valor = ord(data) if data else 0  # Convierte el byte en un valor numérico
        valor = valor * (3.3/256)
        # Actualiza el array de datos
        #datos.insert(0, valor)  # Agrega el valor al principio del array
        #datos.pop()  # Elimina el valor más antiguo del array
        with lock:
            datos[contador_datos] = data
            #print(datos[contador_datos])
            contador_datos += 1
            if(contador_datos == 2047):
                contador_datos = 0
                datos_cambio = datos.copy()

def actualizar_grafico():
    global escala,datos_cambio,datos,inicio_ventana
    # Borra el gráfico anterior y plotea los nuevos datos
    #ax.clear()
    #x = range(contador_datos - escala, contador_datos)  # Los últimos 100 puntos en el tiempo
    #with lock:
    #   ax.plot(y)

    with lock:
        if(datos_cambio[2047] != 0):
            y = datos_cambio[inicio_ventana:inicio_ventana + escala]
        else:
            y = datos[inicio_ventana:inicio_ventana + escala]

    ax.plot(y)
    ax.set_ylim(0, 4) 
    ax.set_xlabel('Tiempo')
    ax.set_ylabel('Valor')
    canvas.draw()

def reducir_escala():
    print("reducir escala")
    global escala
    if (escala + 5 < 2048):
        escala = escala + 5

    return 

def aumentar_escala():
    global escala
    if(escala - 5)>0:
        escala = escala - 5

    return

def aumentar_ventana():
    global inicio_ventana
    if(inicio_ventana + escala + 10 < 2047):
        inicio_ventana += 10
    return

def reducir_ventana():
    global inicio_ventana
    if(inicio_ventana - 10 > 0):
        inicio_ventana -= 10
    return


app = QApplication(sys.argv)

window = QMainWindow()
window.setGeometry(100, 100, 800, 400)
window.setWindowTitle("Aplicación con Matplotlib y UART")

central_widget = QWidget(window)
window.setCentralWidget(central_widget)
layout = QVBoxLayout(central_widget)

# Configura el área de dibujo de Matplotlib
fig = Figure()
canvas = FigureCanvas(fig)
layout.addWidget(canvas)
ax = fig.add_subplot(111)

canvas.setFixedSize(800, 400) 

#Button Escala
button_layout = QHBoxLayout()
layout.addLayout(button_layout)

aumentar_escala_button = QPushButton("Aumentar Escala")
reducir_escala_button = QPushButton("Reducir Escala")

aumentar_escala_button.clicked.connect(aumentar_escala)
reducir_escala_button.clicked.connect(reducir_escala)

button_layout.addWidget(aumentar_escala_button)
button_layout.addWidget(reducir_escala_button)

#Button ventana
button_layout_ventana = QHBoxLayout()
layout.addLayout(button_layout_ventana)

aumentar_ventana_button = QPushButton("Aumentar Ventana")
reducir_ventana_button = QPushButton("Reducir Ventana")

aumentar_ventana_button.clicked.connect(aumentar_ventana)
reducir_ventana_button.clicked.connect(reducir_ventana)

button_layout_ventana.addWidget(aumentar_ventana_button)
button_layout_ventana.addWidget(reducir_ventana_button)

# Inicia un hilo para leer datos UART
uart_thread = threading.Thread(target=leer_datos_uart)
uart_thread.daemon = True  # El hilo se detendrá cuando la aplicación principal se cierre
uart_thread.start()

# Crea un temporizador para actualizar el gráfico cada 1 segundo
timer = QTimer()
timer.timeout.connect(actualizar_grafico)
timer.start(1000)  # 1000 milisegundos = 1 segundo

window.show()

sys.exit(app.exec_())
