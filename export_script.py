import os

root_dirs = [
    r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio\apps\api",
    r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio\apps\web\src",
    r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio\apps\web\package.json",
    r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio\apps\web\next.config.ts"
]
output_file = r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio\codigo_completo.txt"

ignore_dirs = [".git", "__pycache__", "node_modules", ".next", "public"]
ignore_extensions = [".pyc", ".png", ".jpg", ".jpeg", ".ico", ".svg", ".xlsx", ".zip", ".json"] # Keep package.json manually

def write_file_to_output(path, out):
    try:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
            
        relative_path = os.path.relpath(path, r"c:\Users\jcarl\OneDrive\Mierda\ahp_portfolio")
        out.write(f"\n\n{'='*80}\n")
        out.write(f"File: {relative_path}\n")
        out.write(f"{'='*80}\n\n")
        
        # Determine language for markdown
        ext = os.path.splitext(path)[1][1:]
        if ext == 'ts' or ext == 'tsx': ext = 'typescript'
        elif ext == 'js' or ext == 'jsx': ext = 'javascript'
        elif ext == 'py': ext = 'python'
        elif ext == 'json': ext = 'json'
        
        out.write(f"```{ext}\n")
        out.write(content)
        if not content.endswith('\n'):
            out.write('\n')
        out.write("```\n")
        
    except Exception as e:
        print(f"Error reading {path}: {e}")

with open(output_file, "w", encoding="utf-8") as out:
    out.write("# Código de la Aplicación (AHP Portfolio)\n\n")
    out.write("A continuación se presenta el código completo de la aplicación (Frontend en Next.js y Backend en Python FastAPI).\n")
    for path in root_dirs:
        if os.path.isfile(path):
            write_file_to_output(path, out)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = [d for d in dirs if d not in ignore_dirs]
                for file in files:
                    if not any(file.endswith(ext) for ext in ignore_extensions):
                        filepath = os.path.join(root, file)
                        write_file_to_output(filepath, out)
        else:
            print(f"No existe: {path}")

print(f"Exportación completada. Código combinado guardado en: {output_file}")
