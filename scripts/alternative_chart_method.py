"""
Método alternativo para el gráfico de severidades usando BarChart
que tiene mejor compatibilidad con OnlyOffice
"""

def _add_severity_chart_alternative(self, ws, stats, start_row, start_col):
    """Añadir gráfico de severidades usando gráfico de barras (mejor compatibilidad)"""
    # Datos para el gráfico
    data_start_row = start_row
    ws.cell(row=data_start_row, column=start_col, value="Severidad")
    ws.cell(row=data_start_row, column=start_col + 1, value="Cantidad")
    
    # Colores de fondo para las celdas de datos (esto sí funciona en OnlyOffice)
    error_fill = PatternFill(start_color=self.COLOR_ERROR, end_color=self.COLOR_ERROR, fill_type="solid")
    warning_fill = PatternFill(start_color="FFC107", end_color="FFC107", fill_type="solid")
    info_fill = PatternFill(start_color=self.COLOR_INFO, end_color=self.COLOR_INFO, fill_type="solid")
    
    data_rows = [
        ("Errores", stats.get('errors', 0), error_fill),
        ("Warnings", stats.get('warnings', 0), warning_fill),
        ("Info", stats.get('infos', 0), info_fill),
    ]
    
    for i, (label, value, fill) in enumerate(data_rows, 1):
        ws.cell(row=data_start_row + i, column=start_col, value=label)
        ws.cell(row=data_start_row + i, column=start_col + 1, value=value)
        # Aplicar color de fondo a la celda de cantidad
        ws.cell(row=data_start_row + i, column=start_col + 1).fill = fill
        ws.cell(row=data_start_row + i, column=start_col + 1).font = Font(bold=True, color="FFFFFF")
    
    # Crear gráfico de barras horizontal (mejor para mostrar colores)
    chart = BarChart()
    chart.type = "bar"  # Barras horizontales
    chart.title = "Distribución por Severidad"
    chart.style = 10
    
    data = Reference(ws, min_col=start_col + 1, min_row=data_start_row, 
                    max_row=data_start_row + len(data_rows))
    cats = Reference(ws, min_col=start_col, min_row=data_start_row + 1, 
                    max_row=data_start_row + len(data_rows))
    
    chart.add_data(data, titles_from_data=True)
    chart.set_categories(cats)
    
    # Configurar el gráfico
    chart.legend = None  # Sin leyenda para gráfico de barras
    chart.y_axis.title = "Cantidad"
    chart.x_axis.title = "Severidad"
    
    # Posición del gráfico
    ws.add_chart(chart, f"{get_column_letter(start_col + 3)}{start_row}")
