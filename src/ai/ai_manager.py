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

    def save_config(self, enabled: bool = None, provider: str = None, api_key: str = None, model: str = None, **kwargs) -> bool:
        """
        Guardar configuración de IA de forma parcial o total.
        
        Args:
            enabled: Habilitar/deshabilitar (opcional)
            provider: Proveedor (openai, gemini, etc) (opcional)
            api_key: API Key (se guardará encriptada) (opcional)
            model: Modelo seleccionado (opcional)
            **kwargs: Otros parámetros
        """
        try:
            # Cargar config completa actual
            full_config = {}
            if self.config_path.exists():
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    full_config = json.load(f)
            
            # Valores actuales en memoria
            current = self.config
            
            # Determinar valores finales
            final_enabled = enabled if enabled is not None else current.get('enabled', False)
            final_provider = provider if provider is not None else current.get('provider', 'gemini')
            final_model = model if model is not None else current.get('model', 'gemini-1.5-flash')
            
            # Lógica API Key
            if api_key is not None:
                if api_key and not api_key.startswith("__ENC__"):
                    encoded_key = base64.b64encode(api_key.encode()).decode()
                    stored_key = f"__ENC__{encoded_key}"
                else:
                    stored_key = api_key
            else:
                stored_key = current.get('api_key', '')
            
            # Construir objeto config actualizado preservando campos extra
            ai_config = current.copy()
            ai_config.update({
                'enabled': final_enabled,
                'provider': final_provider,
                'api_key': stored_key,
                'model': final_model,
            })
            
            # Actualizar campos extra de kwargs
            for k, v in kwargs.items():
                ai_config[k] = v
                
            # Asegurar default prompt si se perdiera (defensivo)
            if 'ai_prompts' not in ai_config:
                ai_config['ai_prompts'] = {'Default': self._get_default_prompt_text()}

            # Asegurar que siempre exista active_prompt
            if 'active_prompt' not in ai_config:
                ai_config['active_prompt'] = 'Default'

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

    def test_connection(self) -> Tuple[bool, str, List[str]]:
        """
        Probar conexión con el proveedor configurado (REAL)

        Returns:
            (Exito, Mensaje, ListaModelosDisponibles)
        """
        if not self.config.get('enabled'):
            return False, "IA desactivada", []

        provider = self.config.get('provider')
        api_key = self.get_api_key()

        if not api_key and provider != 'local':
            return False, "API Key no configurada", []

        try:
            result = (False, "Proveedor desconocido")
            
            if provider == 'openai':
                result = self._test_openai(api_key)
            elif provider == 'gemini':
                result = self._test_gemini(api_key)
            elif provider == 'claude':
                result = self._test_claude(api_key)
            elif provider == 'local':
                result = self._test_local()
            else:
                result = (False, "Proveedor desconocido")
                
            # Normalizar retorno a 3 elementos
            if len(result) == 2:
                return result[0], result[1], []
            return result
        except Exception as e:
            return False, f"Error al probar conexión: {str(e)}", []

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

    def _test_gemini(self, api_key: str) -> Tuple[bool, str, List[str]]:
        """Probar conexión con Google Gemini y listar modelos compatibles"""
        if not GEMINI_AVAILABLE:
            return False, "Biblioteca 'google-generativeai' no instalada.", []

        try:
            genai.configure(api_key=api_key)
            
            # 1. Listar modelos reales disponibles para esta API Key
            available_models = []
            try:
                for m in genai.list_models():
                    if 'generateContent' in m.supported_generation_methods:
                        # Almacenar nombre completo (models/...) y corto
                        available_models.append(m.name.replace('models/', ''))
            except Exception as e:
                return False, f"✗ API Key inválida o error de conexión ({str(e)})", []
            
            if not available_models:
                return False, "✗ Conectado, pero no se encontraron modelos generativos disponibles.", []

            # 2. Verificar modelo seleccionado
            target = self.config.get('model', '').replace('models/', '')
            
            match_found = False
            for av in available_models:
                if av == target:
                    match_found = True
                    break
            
            models_str = ", ".join(available_models[:4])
            
            if match_found:
                return True, f"✓ Conexión exitosa. Modelo '{target}' validado.", available_models
            else:
                return True, f"⚠ Conectado. Modelo actual '{target}' no listado.", available_models

        except Exception as e:
            return False, f"✗ Error Gemini: {str(e)}", []

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

    def get_prompt_template(self) -> str:
        """
        Obtener el contenido del prompt activo para el análisis.
        Mantiene compatibilidad con llamadas anteriores.
        """
        active_name = self.config.get('active_prompt', 'Default')
        prompts = self.get_all_prompts()
        
        # Si el activo no existe, usar Default
        if active_name not in prompts:
            active_name = 'Default'
            
        return prompts.get(active_name, self._get_default_prompt_text())

    def _get_default_prompt_text(self) -> str:
        """Texto del prompt por defecto"""
        return """Eres un experto auditor de UiPath.
Analiza el siguiente código XAML y los hallazgos. Sé conciso y directo (estilo bullet-points).

**Objetivo:**
1. Crear un 'analysis' (Resumen ejecutivo muy breve: estado general, riesgo principal y calidad). Máximo 4 líneas.
2. Listar 'suggestions' concretas para arreglar los errores críticos detectados.

**Contexto:**
- Archivo: {filename}
- Tipo de Proyecto: {project_type}

**Hallazgos detectados ({findings_count}):**
{findings_list}

**Código XAML (fragmento):**
```xml
{xaml_content}
```

**Instrucciones:**
1. Analiza la gravedad de los hallazgos.
2. Proporciona una solución específica para cada hallazgo crítico.
3. Sugiere mejoras de rendimiento o legibilidad si aplica.
4. Identifica posibles riesgos de mantenimiento.

**Formato JSON estricto:**
{
  "analysis": "Resumen ejecutivo corto y directo...",
  "suggestions": [
    {"priority": "Alta", "title": "Acción Corta", "description": "Instrucción precisa de corrección.", "benefit": "Beneficio claro"}
  ]
}
"""

    def get_all_prompts(self) -> Dict[str, str]:
        """Obtener diccionario de todos los prompts disponibles"""
        # Estructura en config: 'ai_prompts': {'Nombre': 'Contenido'}
        prompts = self.config.get('ai_prompts', {})

        # Versión actualizada del prompt por defecto
        default_latest = self._get_default_prompt_text()

        # Asegurar que existe al menos el Default
        if 'Default' not in prompts:
            prompts['Default'] = default_latest
        else:
            # Si el Default guardado es versión antigua (tiene duplicación o formato viejo), actualizarlo
            current_default = prompts['Default']
            # Detectar versión antigua por la duplicación de "Contexto:" o por tener "score_adjustment"
            if 'score_adjustment' in current_default or current_default.count('**Contexto:**') > 1:
                # Guardar versión antigua como backup
                prompts['Default (Versión Antigua)'] = current_default
                # Actualizar a la nueva versión
                prompts['Default'] = default_latest
                # Guardar cambios
                self.save_config(**self.config)

        # Migración: Si existe 'prompt_template' antiguo, guardarlo como 'Legacy Custom'
        if 'prompt_template' in self.config:
            if self.config['prompt_template'] != prompts['Default']:
                prompts['Custom (Migrado)'] = self.config['prompt_template']
            # Limpiar clave antigua
            del self.config['prompt_template']
            self.save_config(**self.config)

        return prompts

    def save_prompt(self, name: str, content: str) -> bool:
        """Guardar o actualizar un prompt"""
        try:
            if 'ai_prompts' not in self.config:
                self.config['ai_prompts'] = {}
            
            self.config['ai_prompts'][name] = content
            
            # Si es el primero o único, marcarlo como activo
            if len(self.config['ai_prompts']) == 1:
                self.config['active_prompt'] = name
                
            return self.save_config(**self.config)
        except Exception as e:
            print(f"Error al guardar prompt: {e}")
            return False

    def delete_prompt(self, name: str) -> bool:
        """Eliminar un prompt (no permite eliminar Default si es el único)"""
        if name == 'Default':
            return False # Proteger Default
            
        try:
            if 'ai_prompts' in self.config and name in self.config['ai_prompts']:
                del self.config['ai_prompts'][name]
                
                # Si borramos el activo, resetear a Default
                if self.config.get('active_prompt') == name:
                    self.config['active_prompt'] = 'Default'
                    
                return self.save_config(**self.config)
            return False
        except Exception as e:
            print(f"Error al eliminar prompt: {e}")
            return False

    def set_active_prompt(self, name: str) -> bool:
        """Establecer el prompt activo"""
        prompts = self.get_all_prompts()
        if name not in prompts:
            return False
            
        self.config['active_prompt'] = name
        return self.save_config(**self.config)

    def get_active_prompt_name(self) -> str:
        """Obtener nombre del prompt activo actual"""
        return self.config.get('active_prompt', 'Default')

    def _build_prompt(self, xaml_content: str, findings: List[Dict], context: Dict = None) -> str:
        """Construir prompt dinámico usando el template"""
        # Preparar lista de findings formateada
        findings_txt = ""
        for i, finding in enumerate(findings[:10], 1):
            findings_txt += f"\n{i}. [{finding.get('severity', 'info').upper()}] {finding.get('rule_name', '')}: {finding.get('message', '')}"
        
        if len(findings) > 10:
            findings_txt += f"\n... y {len(findings) - 10} findings más"

        # Obtener template
        template = self.get_prompt_template()
        
        # Reemplazar variables (usando format o replace para ser más robusto ante llaves json)
        # Nota: El template tiene {{ }} para el JSON format, así que usamos replace manual para evitar conflictos
        # o usamos format() con cuidado. Para seguridad, haremos replaces manuales de nuestros placeholders.
        
        prompt = template.replace("{filename}", context.get('filename', 'Unknown') if context else 'Unknown')
        prompt = prompt.replace("{project_type}", context.get('project_type', 'Unknown') if context else 'Unknown')
        prompt = prompt.replace("{findings_count}", str(len(findings)))
        prompt = prompt.replace("{findings_list}", findings_txt)
        prompt = prompt.replace("{xaml_content}", xaml_content[:2000])
        
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
            
            # Preferir gemini-pro si el configurado falla o no existe, más seguro para todos
            target_model = self.config.get('model', 'gemini-pro')
            if not target_model: target_model = 'gemini-pro'

            prompt_text = self._build_prompt(xaml_content, findings, context)
            
            def call_gemini(m_name):
                model = genai.GenerativeModel(m_name)
                # Configurar para que responda en JSON si es posible (nuevas versiones)
                # O confiar en el prompt. Gemini Pro 1.0 no soporta response_mime_type nativo siempre.
                return model.generate_content(
                    prompt_text,
                    generation_config=genai.types.GenerationConfig(
                        temperature=self.config.get('temperature', 0.7),
                    )
                )

            try:
                response = call_gemini(target_model)
            except Exception as e:
                # Si falla (404 o cualquier otro), intentar autorecuperación inteligente
                print(f"Modelo {target_model} falló ({str(e)}). Buscando alternativa válida...")
                
                # Buscar dinámicamente un modelo que SÍ exista
                valid_model = None
                try:
                    for m in genai.list_models():
                        if 'generateContent' in m.supported_generation_methods:
                            valid_model = m.name
                            # Preferir modelos 'gemini' sobre otros (como 'paLM')
                            if 'gemini' in valid_model.lower():
                                break
                except:
                    pass
                
                if valid_model and valid_model != target_model:
                     print(f"Intentando con modelo alternativa detectado: {valid_model}")
                     response = call_gemini(valid_model)
                     target_model = f"{valid_model} (Auto-Recovered)"
                else:
                    # Si no encontramos alternativa o falla también, relanzar error original
                    raise e

            # Limpiar respuesta (quitar bloques markdown si existen)
            text_resp = response.text
            clean_text = text_resp.replace('```json', '').replace('```', '').strip()
            
            try:
                result_json = json.loads(clean_text)
            except json.JSONDecodeError:
                # Si falla, intentar devolver texto plano en 'analysis'
                # O si es porque hay texto antes del JSON, intentar extraerlo con regex
                import re
                json_match = re.search(r'(\{.*\})', clean_text, re.DOTALL)
                if json_match:
                    result_json = json.loads(json_match.group(1))
                else:
                    return {
                        'success': True,
                        'analysis': text_resp, # Devolver todo como texto si no hay JSON
                        'suggestions': [],
                        'model': target_model
                    }

            return {
                'success': True,
                'analysis': result_json.get('analysis', ''),
                'suggestions': result_json.get('suggestions', []),
                'patterns': result_json.get('patterns', {}),
                'recommendations': result_json.get('recommendations', []),
                'tokens_used': response.usage_metadata.total_token_count if hasattr(response, 'usage_metadata') else 0,
                'cost_usd': 0.0,
                'model': target_model
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
