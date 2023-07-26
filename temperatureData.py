# Developed by jos_0W

# Bookstore imports
import mysql.connector
import threading
from datetime import datetime, timedelta
import serial
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import seaborn as sns

# Setting parameters to access the mysql database
config = {
    'host' : 'localhost',
    'user' : '**************',
    'password' : '*************',
    'database' : 'temperaturas',
}

# Creation of a temperature database
def createDatabase():
    conection = mysql.connector.connect(
        host="localhost",
        user="**************",
        password="*************",
    )

    try:
        cursor = conection.cursor()
        cursor.execute("CREATE DATABASE temperaturas")
        cursor.execute("CREATE TABLE temperaturas.medidas (tempid INT AUTO_INCREMENT PRIMARY KEY, fecha VARCHAR(50), temperatura FLOAT)")
        print("Base de datos creada con exito")
    except:
        print("La base de datos ya existe")
    conection.close()

# Writing records to the database
def insert_record(fecha, TEMP):
    conection = mysql.connector.connect(**config)
    cursor = conection.cursor()
    cursor.execute ("INSERT INTO medidas (fecha, temperatura) VALUES (%s, %s)",(fecha,TEMP))
    conection.commit()
    w = str(fecha)
    h =str(w)[0:17]
    conection.close()

# Serial communication to COM port for data acquisition
def readData():
    hour = datetime.now()
    hour_string= str(hour).format('YYYY-MM-DD-HH-MM')
    list_values = []
    arduino = serial.Serial(port='COM9', baudrate=9600)
    arduino_data = arduino.readline().decode().strip()
    
    list_values.append(round(float(arduino_data),3))
    temperature = list_values[0]

    arduino_data = 0
    list_values.clear()
    arduino.close()
    
    thread = threading.Thread(insert_record(hour_string,temperature))
    thread.start()

# Data visualization
def buildGraph():
    # Sql queries
    conection = mysql.connector.connect(**config)
    cursor = conection.cursor()
    cursor.execute("SELECT tempid, temperatura FROM medidas LIMIT 100")
    datos = cursor.fetchall()
    cursor.execute("SELECT avg(temperatura) FROM medidas")
    averige = cursor.fetchall()
    cursor.execute("SELECT tempid, temperatura FROM medidas ORDER BY temperatura DESC LIMIT 1")
    maximun_value = cursor.fetchall()
    cursor.execute("SELECT tempid, temperatura FROM medidas ORDER BY temperatura ASC LIMIT 1")
    minimum_value = cursor.fetchall()

    plt.clf()
    x_maximun = [item[0] for item in maximun_value]
    y_maximun = [item[1] for item in maximun_value]
    
    x_minimun = [item[0] for item in minimum_value]
    y_minimun = [item[1] for item in minimum_value]
    
    measurements = [item[0] for item in datos]
    temperatures = [item[1] for item in datos]

    # Temperatures in relation to weather
    plt.subplot(2,2,1)
    plt.plot(measurements, temperatures, label='Temperatura', color='purple')
    plt.scatter(x_maximun, y_maximun, color='red', marker='o', label=f'Máximo: {y_maximun} °C')
    plt.scatter(x_minimun, y_minimun, color='green', marker='d', label=f'Minimo: {y_minimun} °C')
    plt.axhline(y=averige, color='b', ls='--', label=f'Promedio: {averige} °C')
    plt.ylabel('Temperatura (°C)')
    plt.xlabel('Cantidad de observaciones')
    plt.legend()
    plt.title('Grafica de Temperatura con relacion al tiempo')
    
    # Temperature frequency
    plt.subplot(2,2,2)
    plt.hist(temperatures, bins=20, label='Datos', color='b')
    plt.xlabel('Temperatura (°C)')
    plt.ylabel('Frecuencia')
    plt.legend()
    plt.title('Histograma de Temperatura')

    #
    plt.subplot(2,2,3)
    plt.plot(measurements, temperatures, ls='--', marker='o', mec="purple", label='temperature', color='lightblue')

    #
    plt.subplot(2,2,4)
    df = {'x':measurements, 'temperature':temperatures}
    sns.scatterplot(data=df, x='x', y='temperature', hue='temperature')
    plt.scatter(x_minimun, y_minimun, color='green', marker='d', label=f'Minimo: {y_minimun} °C')
    plt.scatter(x_maximun, y_maximun, color='red', marker='o', label=f'Máximo: {y_maximun} °C')
    plt.ylabel('Temperatura (°C)')
    plt.xlabel('Cantidad de observaciones')
    plt.legend()
    plt.title('Analisis de temperaturas (Altas y Bajas)')

    plt.draw()

def main():
    createDatabase()
    plt.ion()
    try:
        while True:
            readData()
            buildGraph()
            plt.pause(3)
    except:
        plt.ioff()
        plt.show()

if __name__ == "__main__":
    main()