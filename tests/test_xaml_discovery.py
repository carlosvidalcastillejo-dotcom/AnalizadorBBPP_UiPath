from pathlib import Path

project_path = Path(r"C:\Users\Imrik\Documents\Proyectos Git\AnalizadorBBPP_UiPath\dummy_project")

print(f"Project path: {project_path}")
print(f"Exists: {project_path.exists()}")
print(f"Is dir: {project_path.is_dir()}")

print("\nBuscando archivos XAML:")
xaml_files = list(project_path.rglob('*.xaml'))
print(f"Encontrados: {len(xaml_files)}")

for xaml in xaml_files:
    print(f"  - {xaml}")
    print(f"    Relative: {xaml.relative_to(project_path)}")
    print(f"    .local in path: {'.local' in str(xaml)}")
    print(f"    .git in path: {'.git' in str(xaml)}")
