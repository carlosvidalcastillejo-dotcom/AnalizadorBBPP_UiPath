"""
Script para extraer reglas del Excel BBPP.xlsx y generar BBPP_Master.json
"""
import openpyxl
import json
from pathlib import Path

# Leer Excel
wb = openpyxl.load_workbook('BBPP.xlsx')
ws = wb.active

# Extraer reglas
excel_rules = []
for i, row in enumerate(ws.iter_rows(min_row=2, values_only=True), 1):
    if not row[0]:  # Skip empty rows
        continue
    
    name = row[0]
    desc = row[1] if row[1] else ""
    severity = row[2] if row[2] else "Warning"
    penalty = row[3] if row[3] else 0
    
    # Convertir penalización a número si es string
    if isinstance(penalty, str):
        # Extraer número de strings como "-1% cada 5 incumplimientos"
        import re
        match = re.search(r'(\d+)', penalty)
        penalty = int(match.group(1)) if match else 2
    elif isinstance(penalty, (int, float)):
        penalty = abs(int(penalty * 100)) if penalty < 1 else int(penalty)
    
    # Generar ID único
    rule_id = f"EXCEL_{i:03d}"
    
    excel_rules.append({
        "id": rule_id,
        "name": name,
        "description": desc[:200] if len(desc) > 200 else desc,  # Limitar descripción
        "category": "general",
        "severity": severity.lower() if severity.lower() in ['error', 'warning', 'info'] else 'warning',
        "penalty": penalty,
        "enabled": True,
        "sets": ["NTTData"],  # Por defecto en NTTData
        "implementation_status": "pending",
        "source": "excel"
    })

print(f"✅ Extraídas {len(excel_rules)} reglas del Excel")
print(json.dumps(excel_rules[:3], indent=2, ensure_ascii=False))

# Guardar temporalmente
with open('excel_rules_temp.json', 'w', encoding='utf-8') as f:
    json.dump(excel_rules, f, indent=2, ensure_ascii=False)
