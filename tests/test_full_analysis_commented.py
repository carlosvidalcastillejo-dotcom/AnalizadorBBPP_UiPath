"""
Test completo: Análisis con código comentado
Verifica que se detecta Y se penaliza
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.xaml_parser import XamlParser
from src.analyzer import BBPPAnalyzer

def test_full_analysis():
    """Test de análisis completo con CommentOut"""
    print("\n" + "="*60)
    print("TEST COMPLETO: ANÁLISIS CON CÓDIGO COMENTADO")
    print("="*60)
    
    # Crear XAML con código comentado (>5%)
    test_xaml = '''<?xml version="1.0" encoding="utf-8"?>
<Activity xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:ui="http://schemas.uipath.com/workflow/activities"
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Sequence DisplayName="Main Sequence">
    <ui:LogMessage DisplayName="Log Message 1" Message="test 1" />
    <ui:LogMessage DisplayName="Log Message 2" Message="test 2" />
    
    <ui:CommentOut DisplayName="Comment Out">
      <ui:CommentOut.Body>
        <Sequence DisplayName="Ignored Activities">
          <ui:LogMessage DisplayName="Log comentado 1" Message="comentado" />
          <ui:LogMessage DisplayName="Log comentado 2" Message="más texto" />
          <ui:LogMessage DisplayName="Log comentado 3" Message="aún más" />
        </Sequence>
      </ui:CommentOut.Body>
    </ui:CommentOut>
    
    <ui:LogMessage DisplayName="Log Message 3" Message="test 3" />
  </Sequence>
</Activity>'''
    
    # Guardar archivo temporal
    test_file = Path("/tmp/test_analysis.xaml")
    test_file.write_text(test_xaml)
    
    # 1. PARSEAR
    print("\n📋 PASO 1: Parseando archivo...")
    parser = XamlParser(test_file)
    parsed_data = parser.parse()
    
    if 'error' in parsed_data:
        print(f"❌ Error de parsing: {parsed_data['error']}")
        test_file.unlink()
        return False
    
    # Mostrar info de parsing
    commented = parsed_data.get('commented_code', {})
    print(f"   ✅ Archivo parseado")
    print(f"   - Total líneas: {parsed_data.get('total_lines', 0)}")
    print(f"   - Líneas comentadas: {commented.get('commented_lines', 0)}")
    print(f"   - CommentOut activities: {commented.get('comment_out_activities', 0)}")
    
    # Calcular porcentaje
    total_lines = parsed_data.get('total_lines', 0)
    commented_lines = commented.get('commented_lines', 0)
    if total_lines > 0:
        percent = (commented_lines / total_lines) * 100
        print(f"   - Porcentaje: {percent:.2f}%")
    
    # 2. ANALIZAR
    print("\n🔍 PASO 2: Analizando con reglas BBPP...")
    analyzer = BBPPAnalyzer()
    findings = analyzer.analyze(parsed_data)
    
    print(f"   ✅ Análisis completado")
    print(f"   - Total findings: {len(findings)}")
    
    # 3. BUSCAR FINDING DE CÓDIGO COMENTADO
    print("\n🎯 PASO 3: Buscando finding de código comentado...")
    commented_finding = None
    for finding in findings:
        if 'comentado' in finding.rule_name.lower():
            commented_finding = finding
            break
    
    if commented_finding:
        print(f"   ✅ Finding encontrado:")
        print(f"      - Regla: {commented_finding.rule_name}")
        print(f"      - Severidad: {commented_finding.severity}")
        print(f"      - Categoría: {commented_finding.category}")
        print(f"      - Descripción: {commented_finding.description}")
        print(f"      - Detalles:")
        for key, value in commented_finding.details.items():
            print(f"         · {key}: {value}")
    else:
        print(f"   ❌ NO se encontró finding de código comentado")
        print(f"\n   Findings encontrados:")
        for f in findings:
            print(f"      - {f.rule_name} ({f.severity})")
        test_file.unlink()
        return False
    
    # 4. VERIFICAR PENALIZACIÓN EN SCORE
    print("\n💯 PASO 4: Verificando impacto en score...")
    
    # Calcular score
    score = analyzer.calculate_score(findings)
    print(f"   Score final: {score}/100")
    
    # Verificar que es menor a 100 (hay penalización)
    if score < 100:
        penalty = 100 - score
        print(f"   ✅ Penalización aplicada: -{penalty} puntos")
    else:
        print(f"   ❌ NO hay penalización (score = 100)")
        test_file.unlink()
        return False
    
    # Limpiar
    test_file.unlink()
    
    return True


if __name__ == "__main__":
    print("\n" + "="*60)
    print("INICIANDO TEST COMPLETO")
    print("="*60)
    
    success = test_full_analysis()
    
    print("\n" + "="*60)
    if success:
        print("✅ TEST PASADO")
        print("   - Código comentado detectado")
        print("   - Finding generado")
        print("   - Penalización aplicada al score")
    else:
        print("❌ TEST FALLADO")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
