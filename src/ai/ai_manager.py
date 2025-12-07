import json
import os
from pathlib import Path
from typing import Dict, Optional, List, Tuple
import base64

# Intentar importar bibliotecas de IA (opcionales)
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

try:
    import anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

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
        Probar conexión con el proveedor configurado (REAL)

        Returns:
            (Exito, Mensaje)
        """
        if not self.config.get('enabled'):
            return False, "IA desactivada"

        provider = self.config.get('provider')
        api_key = self.get_api_key()

        if not api_key and provider != 'local':
            return False, "API Key no configurada"

        try:
            if provider == 'openai':
                return self._test_openai(api_key)
            elif provider == 'gemini':
                return self._test_gemini(api_key)
            elif provider == 'claude':
                return self._test_claude(api_key)
            elif provider == 'local':
                return self._test_local()
            else:
                return False, "Proveedor desconocido"
        except Exception as e:
            return False, f"Error al probar conexión: {str(e)}"

    def _test_openai(self, api_key: str) -> Tuple[bool, str]:
        """Probar conexión con OpenAI"""
        if not OPENAI_AVAILABLE:
            return False, "Biblioteca 'openai' no instalada. Ejecuta: pip install openai"

        try:
            client = openai.OpenAI(api_key=api_key)
            # Hacer una solicitud mínima para verificar la key
            response = client.models.list()
            return True, "✓ Conexión exitosa con OpenAI"
        except openai.AuthenticationError:
            return False, "✗ API Key inválida"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def _test_gemini(self, api_key: str) -> Tuple[bool, str]:
        """Probar conexión con Google Gemini"""
        if not GEMINI_AVAILABLE:
            return False, "Biblioteca 'google-generativeai' no instalada. Ejecuta: pip install google-generativeai"

        try:
            genai.configure(api_key=api_key)
            # Listar modelos para verificar la key
            models = genai.list_models()
            return True, "✓ Conexión exitosa con Google Gemini"
        except Exception as e:
            if "API key not valid" in str(e):
                return False, "✗ API Key inválida"
            return False, f"✗ Error: {str(e)}"

    def _test_claude(self, api_key: str) -> Tuple[bool, str]:
        """Probar conexión con Anthropic Claude"""
        if not ANTHROPIC_AVAILABLE:
            return False, "Biblioteca 'anthropic' no instalada. Ejecuta: pip install anthropic"

        try:
            client = anthropic.Anthropic(api_key=api_key)
            # Hacer una solicitud mínima
            response = client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=10,
                messages=[{"role": "user", "content": "test"}]
            )
            return True, "✓ Conexión exitosa con Anthropic Claude"
        except anthropic.AuthenticationError:
            return False, "✗ API Key inválida"
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def _test_local(self) -> Tuple[bool, str]:
        """Probar conexión con modelo local (Ollama/LM Studio)"""
        if not REQUESTS_AVAILABLE:
            return False, "Biblioteca 'requests' no instalada. Ejecuta: pip install requests"

        try:
            # Intentar conectar con Ollama (puerto por defecto: 11434)
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            if response.status_code == 200:
                models = response.json().get('models', [])
                if models:
                    return True, f"✓ Conexión exitosa con Ollama ({len(models)} modelos disponibles)"
                return True, "✓ Ollama conectado (sin modelos instalados)"
            return False, "✗ Ollama no responde correctamente"
        except requests.exceptions.ConnectionError:
            # Intentar LM Studio (puerto por defecto: 1234)
            try:
                response = requests.get("http://localhost:1234/v1/models", timeout=2)
                if response.status_code == 200:
                    return True, "✓ Conexión exitosa con LM Studio"
                return False, "✗ LM Studio no responde correctamente"
            except:
                return False, "✗ No se detectó Ollama ni LM Studio. Asegúrate de que uno esté ejecutándose."
        except Exception as e:
            return False, f"✗ Error: {str(e)}"

    def analyze_code(self, xaml_content: str, findings: List[Dict], context: Dict = None) -> Dict:
        """
        Analizar código XAML con IA y generar sugerencias

        Args:
            xaml_content: Contenido del archivo XAML
            findings: Lista de findings encontrados por el analizador estático
            context: Contexto adicional (nombre archivo, tipo proyecto, etc.)

        Returns:
            Dict con sugerencias de IA, tokens usados, costo estimado
        """
        if not self.config.get('enabled'):
            return {'error': 'IA desactivada', 'suggestions': []}

        provider = self.config.get('provider')

        try:
            if provider == 'openai':
                return self._analyze_openai(xaml_content, findings, context)
            elif provider == 'gemini':
                return self._analyze_gemini(xaml_content, findings, context)
            elif provider == 'claude':
                return self._analyze_claude(xaml_content, findings, context)
            elif provider == 'local':
                return self._analyze_local(xaml_content, findings, context)
            else:
                return {'error': 'Proveedor desconocido', 'suggestions': []}
        except Exception as e:
            return {'error': f'Error en análisis: {str(e)}', 'suggestions': []}

    def _build_prompt(self, xaml_content: str, findings: List[Dict], context: Dict = None) -> str:
        """Construir prompt para el análisis de IA"""
        prompt = f"""Eres un experto en UiPath y análisis de código de automatización RPA.

Analiza el siguiente código XAML de UiPath y los findings detectados por el analizador estático.
Genera sugerencias concretas y accionables para mejorar la calidad del código.

**Contexto:**
- Archivo: {context.get('filename', 'Unknown') if context else 'Unknown'}
- Tipo de Proyecto: {context.get('project_type', 'Unknown') if context else 'Unknown'}

**Findings detectados ({len(findings)}):**
"""
        for i, finding in enumerate(findings[:10], 1):  # Limitar a 10 findings para no saturar
            prompt += f"\n{i}. [{finding.get('severity', 'info').upper()}] {finding.get('rule_name', '')}: {finding.get('message', '')}"

        if len(findings) > 10:
            prompt += f"\n... y {len(findings) - 10} findings más"

        prompt += f"""

**Código XAML (primeros 2000 caracteres):**
```xml
{xaml_content[:2000]}
```

**Por favor, proporciona:**
1. **Análisis General:** Evaluación de la calidad del código
2. **Sugerencias de Mejora:** 3-5 sugerencias concretas y priorizadas
3. **Patrones Detectados:** Buenos o malos patrones identificados
4. **Recomendaciones:** Best practices aplicables

Formato de respuesta: JSON con estructura:
{{
  "analysis": "texto del análisis",
  "suggestions": [
    {{"priority": "high/medium/low", "title": "...", "description": "...", "benefit": "..."}},
  ],
  "patterns": {{"good": [...], "bad": [...]}},
  "recommendations": [...]
}}
"""
        return prompt

    def _analyze_openai(self, xaml_content: str, findings: List[Dict], context: Dict) -> Dict:
        """Análisis con OpenAI"""
        if not OPENAI_AVAILABLE:
            return {'error': 'Biblioteca openai no disponible', 'suggestions': []}

        try:
            client = openai.OpenAI(api_key=self.get_api_key())
            model = self.config.get('model', 'gpt-3.5-turbo')

            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "Eres un experto en UiPath y análisis de código RPA."},
                    {"role": "user", "content": self._build_prompt(xaml_content, findings, context)}
                ],
                temperature=self.config.get('temperature', 0.7),
                response_format={"type": "json_object"}
            )

            result_text = response.choices[0].message.content
            result_json = json.loads(result_text)

            return {
                'success': True,
                'analysis': result_json.get('analysis', ''),
                'suggestions': result_json.get('suggestions', []),
                'patterns': result_json.get('patterns', {}),
                'recommendations': result_json.get('recommendations', []),
                'tokens_used': response.usage.total_tokens,
                'cost_usd': self._estimate_cost_openai(model, response.usage.total_tokens),
                'model': model
            }
        except Exception as e:
            return {'error': f'Error OpenAI: {str(e)}', 'suggestions': []}

    def _analyze_gemini(self, xaml_content: str, findings: List[Dict], context: Dict) -> Dict:
        """Análisis con Google Gemini"""
        if not GEMINI_AVAILABLE:
            return {'error': 'Biblioteca google-generativeai no disponible', 'suggestions': []}

        try:
            genai.configure(api_key=self.get_api_key())
            model_name = self.config.get('model', 'gemini-1.5-flash')
            model = genai.GenerativeModel(model_name)

            response = model.generate_content(
                self._build_prompt(xaml_content, findings, context),
                generation_config=genai.types.GenerationConfig(
                    temperature=self.config.get('temperature', 0.7),
                )
            )

            result_json = json.loads(response.text)

            return {
                'success': True,
                'analysis': result_json.get('analysis', ''),
                'suggestions': result_json.get('suggestions', []),
                'patterns': result_json.get('patterns', {}),
                'recommendations': result_json.get('recommendations', []),
                'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                'cost_usd': 0.0,  # Gemini tiene pricing diferente
                'model': model_name
            }
        except Exception as e:
            return {'error': f'Error Gemini: {str(e)}', 'suggestions': []}

    def _analyze_claude(self, xaml_content: str, findings: List[Dict], context: Dict) -> Dict:
        """Análisis con Anthropic Claude"""
        if not ANTHROPIC_AVAILABLE:
            return {'error': 'Biblioteca anthropic no disponible', 'suggestions': []}

        try:
            client = anthropic.Anthropic(api_key=self.get_api_key())
            model = self.config.get('model', 'claude-3-5-sonnet-20240620')

            response = client.messages.create(
                model=model,
                max_tokens=4096,
                temperature=self.config.get('temperature', 0.7),
                messages=[
                    {"role": "user", "content": self._build_prompt(xaml_content, findings, context)}
                ]
            )

            result_json = json.loads(response.content[0].text)

            return {
                'success': True,
                'analysis': result_json.get('analysis', ''),
                'suggestions': result_json.get('suggestions', []),
                'patterns': result_json.get('patterns', {}),
                'recommendations': result_json.get('recommendations', []),
                'tokens_used': response.usage.input_tokens + response.usage.output_tokens,
                'cost_usd': self._estimate_cost_claude(model, response.usage.input_tokens, response.usage.output_tokens),
                'model': model
            }
        except Exception as e:
            return {'error': f'Error Claude: {str(e)}', 'suggestions': []}

    def _analyze_local(self, xaml_content: str, findings: List[Dict], context: Dict) -> Dict:
        """Análisis con modelo local (Ollama/LM Studio)"""
        if not REQUESTS_AVAILABLE:
            return {'error': 'Biblioteca requests no disponible', 'suggestions': []}

        try:
            model = self.config.get('model', 'llama3')
            prompt = self._build_prompt(xaml_content, findings, context)

            # Intentar Ollama primero
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": model, "prompt": prompt, "stream": False},
                    timeout=60
                )
                if response.status_code == 200:
                    result_json = json.loads(response.json()['response'])
                    return {
                        'success': True,
                        'analysis': result_json.get('analysis', ''),
                        'suggestions': result_json.get('suggestions', []),
                        'patterns': result_json.get('patterns', {}),
                        'recommendations': result_json.get('recommendations', []),
                        'tokens_used': 0,
                        'cost_usd': 0.0,
                        'model': f'{model} (Ollama)'
                    }
            except:
                pass

            # Intentar LM Studio
            response = requests.post(
                "http://localhost:1234/v1/chat/completions",
                json={
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": self.config.get('temperature', 0.7)
                },
                timeout=60
            )

            if response.status_code == 200:
                result_text = response.json()['choices'][0]['message']['content']
                result_json = json.loads(result_text)
                return {
                    'success': True,
                    'analysis': result_json.get('analysis', ''),
                    'suggestions': result_json.get('suggestions', []),
                    'patterns': result_json.get('patterns', {}),
                    'recommendations': result_json.get('recommendations', []),
                    'tokens_used': 0,
                    'cost_usd': 0.0,
                    'model': f'{model} (LM Studio)'
                }

            return {'error': 'No se pudo conectar con modelo local', 'suggestions': []}
        except Exception as e:
            return {'error': f'Error modelo local: {str(e)}', 'suggestions': []}

    def _estimate_cost_openai(self, model: str, tokens: int) -> float:
        """Estimar costo de OpenAI"""
        # Precios aproximados (USD por 1K tokens) - actualizar según pricing oficial
        pricing = {
            'gpt-4o': 0.005,  # Precio promedio input+output
            'gpt-4-turbo': 0.01,
            'gpt-3.5-turbo': 0.0015
        }
        rate = pricing.get(model, 0.002)
        return (tokens / 1000) * rate

    def _estimate_cost_claude(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Estimar costo de Claude"""
        # Precios aproximados (USD por 1M tokens)
        pricing = {
            'claude-3-5-sonnet-20240620': {'input': 3.0, 'output': 15.0},
            'claude-3-opus-20240229': {'input': 15.0, 'output': 75.0},
            'claude-3-haiku-20240307': {'input': 0.25, 'output': 1.25}
        }
        rates = pricing.get(model, {'input': 3.0, 'output': 15.0})
        return (input_tokens / 1_000_000 * rates['input']) + (output_tokens / 1_000_000 * rates['output'])


# Singleton
_ai_manager = None

def get_ai_manager() -> AIManager:
    global _ai_manager
    if _ai_manager is None:
        _ai_manager = AIManager()
    return _ai_manager
