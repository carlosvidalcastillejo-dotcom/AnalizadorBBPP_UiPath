import json
from pathlib import Path

# Cargar BBPP_Master.json
bbpp_path = Path(r"c:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\config\bbpp\BBPP_Master.json")
with open(bbpp_path, 'r', encoding='utf-8') as f:
    bbpp_data = json.load(f)

# Excepciones del REFramework por regla
reframework_exceptions = {
    'NOMENCLATURA_001': [
        "Config",
        "TransactionItem",
        "TransactionData",
        "TransactionNumber",
        "RetryNumber",
        "SystemException",
        "BusinessException",
        "QueueRetry",
        "ConsecutiveSystemExceptions"
    ],
    'NOMENCLATURA_002': [
        "Config",
        "TransactionItem",
        "TransactionData",
        "TransactionNumber",
        "RetryNumber",
        "SystemException",
        "BusinessException",
        "QueueRetry",
        "ConsecutiveSystemExceptions",
        "in_Config",
        "io_TransactionItem",
        "in_TransactionData",
        "out_TransactionData",
        "io_dt_TransactionData",
        "in_TransactionNumber",
        "in_OrchestratorQueueName",
        "in_OrchestratorQueueFolder",
        "io_TransactionNumber",
        "io_RetryNumber",
        "io_SystemException",
        "io_BusinessException",
        "io_QueueRetry",
        "io_ConsecutiveSystemExceptions"
    ],
    'NOMENCLATURA_003': [
        "in_Config",
        "io_TransactionItem",
        "in_TransactionData",
        "out_TransactionData",
        "io_dt_TransactionData",
        "in_TransactionNumber",
        "in_OrchestratorQueueName",
        "in_OrchestratorQueueFolder",
        "io_TransactionNumber",
        "io_RetryNumber",
        "io_SystemException",
        "io_BusinessException",
        "io_QueueRetry",
        "io_ConsecutiveSystemExceptions"
    ],
    'NOMENCLATURA_005': [
        "Config",
        "TransactionItem",
        "TransactionData",
        "TransactionNumber",
        "RetryNumber",
        "SystemException",
        "BusinessException",
        "QueueRetry",
        "ConsecutiveSystemExceptions"
    ],
    'NOMENCLATURA_004': [  # Argumentos con descripción
        "in_Config",
        "io_TransactionItem",
        "in_TransactionData",
        "out_TransactionData",
        "in_OrchestratorQueueName",
        "in_OrchestratorQueueFolder"
    ]
}

# Actualizar reglas con excepciones
updated_count = 0
for rule in bbpp_data['rules']:
    rule_id = rule['id']
    
    if rule_id in reframework_exceptions:
        # Asegurar que tiene parameters
        if 'parameters' not in rule:
            rule['parameters'] = {}
        
        # Agregar excepciones
        rule['parameters']['exceptions'] = reframework_exceptions[rule_id]
        updated_count += 1
        print(f"✅ {rule_id}: {len(reframework_exceptions[rule_id])} excepciones agregadas")

# Actualizar metadata
bbpp_data['metadata']['version'] = "2.3.0"
bbpp_data['metadata']['last_updated'] = "2025-11-29"
bbpp_data['metadata']['changelog'] = "v2.3.0: Sistema de excepciones para reglas de nomenclatura (REFramework)"

# Guardar
with open(bbpp_path, 'w', encoding='utf-8') as f:
    json.dump(bbpp_data, f, indent=2, ensure_ascii=False)

print(f"\n✅ BBPP_Master.json actualizado correctamente")
print(f"✅ {updated_count} reglas actualizadas con excepciones")
print(f"✅ Versión: {bbpp_data['metadata']['version']}")
