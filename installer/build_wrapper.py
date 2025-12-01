# -*- coding: utf-8 -*-
"""Wrapper para ejecutar build_installer.py con encoding correcto"""
import sys
import os

# Configurar encoding UTF-8
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# Ejecutar build_installer
import build_installer
build_installer.main()
