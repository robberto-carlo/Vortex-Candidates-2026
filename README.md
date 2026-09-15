# Vortex-Candidates-2026

<p align="center">

<img src="https://img.shields.io/badge/Device-Raspberry%20Pi-red?style=for-the-badge">

<img src="https://img.shields.io/badge/Language-Python-blue?style=for-the-badge">

<img src="https://img.shields.io/badge/Vision%20System-OpenCV-green?style=for-the-badge">

</p>

---

## Overview

Este repositorio contiene el desarrollo realizado por el equipo **Vortex** para la competencia **Candidates 2026**, correspondiente a los retos **Pista A (MAZE)** y **Pista B (Niveles)**.

El proyecto utiliza una **Raspberry Pi y una cámara** para desarrollar un sistema de visión por computadora capaz de capturar y procesar imágenes, detectar colores y obtener información de los elementos presentes en la imagen.

El sistema está siendo desarrollado utilizando **Python y OpenCV**, junto con herramientas de calibración y pruebas para facilitar su implementación durante la competencia.

---

## Setup

Para preparar la Raspberry Pi y ejecutar el proyecto, primero es necesario clonar el repositorio.

### Clone Repository

Desde la Raspberry Pi, ejecutar:

```bash
git clone https://github.com/robberto-carlo/Vortex-Candidates-2026.git
```

Entrar al repositorio:

```bash
cd Vortex-Candidates-2026
```

### Setup Script

El proyecto incluye un script `setup.sh` dentro de la carpeta `raspberry/`, encargado de instalar las dependencias necesarias para ejecutar el sistema.

Entrar a la carpeta `raspberry`:

```bash
cd raspberry
```

Ejecutar el script:

```bash
./setup.sh
```

Al finalizar, el script verifica las versiones instaladas de Python, OpenCV, NumPy y PySerial.

---

## Week 2

Durante la segunda semana se desarrolló la base del sistema de visión.

### Completed

* Configuración inicial del proyecto.

* Pruebas de captura y procesamiento de imágenes con OpenCV.

* Desarrollo de las funciones básicas para el manejo de la cámara.

* Desarrollo de funciones para la detección de colores.

* Detección mediante HSV y threshold en escala de grises.

* Desarrollo de funciones para la detección de objetos y obtención de sus coordenadas.

* Creación de tests para comprobar las funciones de la cámara.

* Desarrollo de herramientas de calibración para ROI y HSV.

---

## Color Detection

Se implementaron diferentes métodos para detectar información de color en las imágenes.

### HSV

La detección mediante HSV permite definir rangos de color y generar una máscara a partir de ellos.

### Threshold

También se implementó detección mediante threshold sobre imágenes en escala de grises, permitiendo separar regiones de la imagen según sus valores de intensidad.

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

### Software

* Raspberry Pi OS.
* Python.
* OpenCV.
* NumPy.
* PySerial.
* Git.

---

## Team

<p align="center">

<strong>Vortex</strong><br> <em>Candidates 2026</em>

</p>
