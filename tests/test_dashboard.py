"""
Script para abrir el Dashboard de Métricas y verificar las nuevas columnas
"""

import sys
import tkinter as tk
from pathlib import Path

# Añadir path para imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ui.metrics_dashboard import MetricsDashboard

def main():
    """Abrir Dashboard de Métricas"""
    print("=" * 60)
    print("DASHBOARD DE MÉTRICAS - PRUEBA DE NUEVAS COLUMNAS")
    print("=" * 60)
    print("\n✅ Abriendo Dashboard de Métricas...")
    print("   Verifica que las columnas aparezcan en este orden:")
    print("   1. Fecha")
    print("   2. Proyecto")
    print("   3. Conjunto BBPP  ← NUEVA")
    print("   4. Versión        ← ACTUALIZADA")
    print("   5. Score")
    print("   6. Errors")
    print("   7. Warnings")
    print("   8. Info")
    print("\n" + "=" * 60)
    
    # Crear ventana principal
    root = tk.Tk()
    root.title("Dashboard de Métricas - Prueba")
    root.geometry("1200x700")
    
    # Crear dashboard
    dashboard = MetricsDashboard(root)
    dashboard.pack(fill=tk.BOTH, expand=True)
    
    # Iniciar aplicación
    root.mainloop()

if __name__ == "__main__":
    main()
