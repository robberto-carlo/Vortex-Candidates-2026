#!/bin/bash

set -e

echo "    Vortex-Candidates-2026 - SETUP"
echo ""

echo "[1/5] Actualizando paquetes..."
sudo apt update

echo "[2/5] Instalando Git..."
sudo apt install -y \
    git

echo "[3/5] Instalando Python..."
sudo apt install -y \
    python3 \
    python3-pip \
    python3-dev

echo "[4/5] Instalando OpenCV..."
sudo apt install -y \
    python3-opencv \
    libopencv-dev

echo "[5/5] Instalando librerías de Python..."
sudo apt install -y \
    python3-numpy \
    python3-serial

echo ""
echo "=========================================="
echo "       INSTALACIÓN COMPLETADA"
echo "=========================================="
echo ""

echo "Git:"
git --version

echo ""
echo "Python:"
python3 --version

echo ""
echo "OpenCV:"
python3 -c "import cv2; print(cv2.__version__)"

echo ""
echo "NumPy:"
python3 -c "import numpy; print(numpy.__version__)"

echo ""
echo "PySerial:"
python3 -c "import serial; print(serial.__version__)"

echo ""
echo "Vortex-Candidates-2026 está listo."