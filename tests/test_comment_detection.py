"""
Script de prueba para detección de código comentado
Incluye detección de CommentOut
"""

import sys
from pathlib import Path

# Agregar src al path
sys.path.insert(0, str(Path(__file__).parent))

from src.xaml_parser import XamlParser

def test_comment_detection():
    """Test de detección de comentarios y CommentOut"""
    print("\n" + "="*60)
    print("TEST DE DETECCIÓN DE CÓDIGO COMENTADO")
    print("="*60)
    
    # Crear un XAML de prueba con CommentOut
    test_xaml = '''<?xml version="1.0" encoding="utf-8"?>
<Activity xmlns="http://schemas.microsoft.com/netfx/2009/xaml/activities" 
          xmlns:ui="http://schemas.uipath.com/workflow/activities"
          xmlns:x="http://schemas.microsoft.com/winfx/2006/xaml">
  <Sequence DisplayName="Main Sequence">
    <ui:LogMessage DisplayName="Log 1" Message="test" />
    <ui:CommentOut DisplayName="Comment Out">
      <ui:CommentOut.Body>
        <Sequence DisplayName="Ignored">
          <ui:LogMessage DisplayName="Log comentado 1" Message="comentado" />
          <ui:LogMessage DisplayName="Log comentado 2" Message="más texto" />
          <ui:LogMessage DisplayName="Log comentado 3" Message="aún más" />
        </Sequence>
      </ui:CommentOut.Body>
    </ui:CommentOut>
    <ui:LogMessage DisplayName="Log 2" Message="normal" />
  </Sequence>
</Activity>'''
    
    # Guardar XAML temporal
    test_file = Path("/tmp/test_commentout.xaml")
    test_file.write_text(test_xaml, encoding='utf-8')
    
    # Parsear
    parser = XamlParser(test_file)
    result = parser.parse()
    
    # Verificar si hubo error
    if 'error' in result:
        print(f"\n❌ ERROR DE PARSING:")
        print(f"   {result.get('error', 'Error desconocido')}")
        test_file.unlink()
        return False
    
    # DEBUG: Ver todos los elementos del árbol
    print(f"\n🔍 DEBUG - Elementos en el árbol XML:")
    if parser.root is not None:
        for elem in parser.root.iter():
            tag = elem.tag
            if '}' in tag:
                tag = tag.split('}')[1]
            if elem.get('DisplayName'):
                print(f"   - {tag}: {elem.get('DisplayName')}")
    
    # Mostrar resultados
    commented = result.get('commented_code', {})
    
    print(f"\n📊 RESULTADOS:")
    print(f"   Total comentarios: {commented.get('total_comments', 0)}")
    print(f"   Comentarios XML: {commented.get('xml_comments', 0)}")
    print(f"   CommentOut activities: {commented.get('comment_out_activities', 0)}")
    print(f"   Líneas comentadas (total): {commented.get('commented_lines', 0)}")
    print(f"   Líneas XML comentadas: {commented.get('xml_commented_lines', 0)}")
    print(f"   Líneas CommentOut: {commented.get('comment_out_lines', 0)}")
    
    print(f"\n📋 DETALLES DE COMMENTOUT:")
    for i, co in enumerate(commented.get('comment_out_details', []), 1):
        print(f"   {i}. {co['display_name']}")
        print(f"      └─ Actividades dentro: {co['activities_inside']}")
    
    # Calcular porcentaje
    total_lines = result.get('total_lines', 0)
    commented_lines = commented.get('commented_lines', 0)
    
    if total_lines > 0:
        percent = (commented_lines / total_lines) * 100
        print(f"\n📈 PORCENTAJE:")
        print(f"   Total líneas: {total_lines}")
        print(f"   Líneas comentadas: {commented_lines}")
        print(f"   Porcentaje: {percent:.2f}%")
        
        if percent > 5:
            print(f"   ⚠️ SUPERA EL UMBRAL de 5%")
        else:
            print(f"   ✅ Dentro del umbral de 5%")
    
    # Limpiar
    test_file.unlink()
    
    return commented.get('comment_out_activities', 0) > 0


if __name__ == "__main__":
    success = test_comment_detection()
    
    print("\n" + "="*60)
    if success:
        print("✅ TEST PASADO: CommentOut detectado correctamente")
    else:
        print("❌ TEST FALLADO: No se detectó CommentOut")
    print("="*60 + "\n")
    
    sys.exit(0 if success else 1)
