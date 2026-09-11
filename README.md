# Vortex-Candidates-2026

<p align="center">

<img src="https://img.shields.io/badge/Device-Raspberry%20Pi-red?style=for-the-badge">
<img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge">
<img src="https://img.shields.io/badge/Vision%20System-OpenCV-green?style=for-the-badge">

</p>

---

## Week 2

Durante la primera semana se desarrolló la base del sistema de visión.

### Completed

* Configuración inicial del proyecto.
* Preparación del entorno de desarrollo.
* Pruebas de captura y procesamiento de imágenes con OpenCV.
* Desarrollo de las funciones básicas para el manejo de la cámara.
* Desarrollo de funciones para la detección de colores.
* Implementación de detección mediante HSV y threshold.
* Desarrollo de funciones para la detección de objetos y obtención de sus coordenadas.
* Creación de tests para comprobar las funciones de la cámara.
* Desarrollo de herramientas de calibración para ROI y HSV.

### Next Steps

* Crear el entorno en la Raspberry Pi para utilizar el código.
* Probar las funciones de la cámara en la Raspberry Pi.
* Crear una herramienta para calibrar los valores de threshold mediante trackbars.
* Implementar la comunicación entre la Raspberry Pi y Arduino.
* Implementar la lectura de sensores de distancia mediante Arduino.

---

## Overview

Este repositorio contiene el desarrollo realizado por el equipo **Vortex** para la competencia **Candidates 2026**, correspondiente a los retos **Pista A (MAZE)** y **Pista B (Niveles)**.

El proyecto utiliza una **Raspberry Pi y una cámara** para desarrollar un sistema de visión por computadora capaz de capturar y procesar imágenes, detectar colores, y obtener información de los elementos presentes en la imagen.

El sistema está siendo desarrollado utilizando **Python y OpenCV**, junto con herramientas de calibración y pruebas para facilitar su implementación durante la competencia.

---

## Color Detection

Se implementaron diferentes métodos para detectar información de color en las imágenes.

### HSV

La detección mediante HSV permite definir rangos de color y generar una máscara a partir de ellos.

### Threshold

También se implementó detección mediante threshold para separar regiones de la imagen según sus valores de intensidad.

---

## Calibration

El proyecto incluye herramientas para calibrar los parámetros utilizados por el sistema de visión.

### ROI Calibration

Permite seleccionar una **Region of Interest (ROI)** directamente sobre la imagen de la cámara.

### HSV Calibration

Permite ajustar los valores:

* H Min / H Max.
* S Min / S Max.
* V Min / V Max.

mediante trackbars mientras se observa la cámara y la máscara en tiempo real.

---

## Tests

Se desarrollaron diferentes tests para comprobar el funcionamiento de las funciones de visión.

Actualmente se han realizado pruebas para:

* Cámara.
* Detección de colores.
* Threshold.
* Detección de objetos.
* Detección del color dominante.

---

## Requirements

### Hardware

* Raspberry Pi.
* Cámara.
* Arduino.


### Software

* Raspberry Pi OS.
* Python.
* OpenCV.
* NumPy.
* Git.

---

## Team

<p align="center">

<strong>Vortex</strong><br> <em>Candidates 2026</em>

</p>
