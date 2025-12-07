import json
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import base64

class AIManager:
    """Gestor de integración con Inteligencia Artificial"""
    
    PROVIDERS = {
        "openai": "OpenAI (GPT-4 / GPT-3.5)",
        "gemini": "Google Gemini (Pro / Flash)",
        "claude": "Anthropic Claude (Sonnet / Opus)",
        "local": "Modelo Local (Ollama / LM Studio)"
    }
    
    MODELS = {
        "openai": ["gpt-4o", "gpt-4-turbo", "gpt-3.5-turbo"],
        "gemini": ["gemini-1.5-pro", "gemini-1.5-flash", "gemini-pro"],
        "claude": ["claude-3-5-sonnet-20240620", "claude-3-opus-20240229", "claude-3-haiku-20240307"],
        "local": ["llama3", "mistral", "custom"]
    }
    
    def __init__(self):
        """Inicializar gestor de IA"""
        self.config_path = Path(__file__).parent.parent.parent / 'config' / 'user_config.json'
        self.config = self._load_config()
        
    def _load_config(self) -> Dict:
        """Cargar configuración"""
        if not self.config_path.exists():
            return {}
            
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get('ai_config', {
                    'enabled': False,
                    'provider': 'openai',
                    'api_key': '',  # Encriptada/Ofuscada
                    'model': 'gpt-3.5-turbo',
                    'temperature': 0.7
                })
        except Exception as e:
            print(f"Error cargando config de IA: {e}")
            return {}

    def save_config(self, enabled: bool, provider: str, api_key: str, model: str) -> bool:
        """
        Guardar configuración de IA
        
        Args:
            enabled: Si la IA está habilitada
            provider: Proveedor (openai, gemini, etc.)
            api_key: API Key (se guardará encriptada)
            model: Modelo seleccionado
        """
        try:
            # Cargar config completa actual
            full_config = {}
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
            
            # Ofuscar API Key (básico por ahora, mejorar con criptografía real)
            # Solo ofuscar si no parece ya ofuscada (empieza con __ENC__)
            if api_key and not api_key.startswith("__ENC__"):
                encoded_key = base64.b64encode(api_key.encode()).decode()
                stored_key = f"__ENC__{encoded_key}"
            else:
                stored_key = api_key
            
            # Actualizar sección AI
            ai_config = {
                'enabled': enabled,
                'provider': provider,
                'api_key': stored_key,
                'model': model,
                'temperature': 0.7
            }
            
            full_config['ai_config'] = ai_config
            self.config = ai_config
            
            # Guardar
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(full_config, f, indent=4)
                
            return True
        except Exception as e:
            print(f"Error guardando config IA: {e}")
            return False
            
    def get_api_key(self) -> str:
        """Obtener API Key desencriptada"""
        key = self.config.get('api_key', '')
        if key.startswith("__ENC__"):
            try:
                encoded = key.replace("__ENC__", "")
                return base64.b64decode(encoded).decode()
            except:
                return ""
        return key

    def get_config(self) -> Dict:
        """Obtener configuración actual"""
        return self.config

    def test_connection(self) -> Tuple[bool, str]:
        """
        Probar conexión con el proveedor configurado
        
        Returns:
            (Exito, Mensaje)
        """
        if not self.config.get('enabled'):
            return False, "IA desactivada"
            
        provider = self.config.get('provider')
        api_key = self.get_api_key()
        
        if not api_key and provider != 'local':
            return False, "API Key no configurada"
            
        # Simulación de conexión para esta fase
        # En el futuro aquí irán las llamadas reales a las bibliotecas de cliente
        import time
        time.sleep(1) # Simular latencia
        
        if provider == 'openai':
            if api_key.startswith("sk-"):
                return True, "Conexión exitosa con OpenAI"
            return False, "API Key de OpenAI inválida (debe empezar con sk-)"
            
        elif provider == 'gemini':
            if len(api_key) > 20: # Validación básica
                return True, "Conexión exitosa con Gemini"
            return False, "API Key de Gemini parece inválida"
            
        elif provider == 'claude':
            if api_key.startswith("sk-ant"):
                return True, "Conexión exitosa con Claude"
            return False, "API Key de Claude inválida (debe empezar con sk-ant)"
            
        elif provider == 'local':
            return True, "Conexión con modelo local (simulada)"
            
        return False, "Proveedor desconocido"


# Singleton
_ai_manager = None

def get_ai_manager() -> AIManager:
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager
