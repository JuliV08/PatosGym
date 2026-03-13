import os
import zipfile

def create_zip(zip_filename, source_dir):
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Excludes
        exclude_dirs = {'.git', 'venv', 'staticfiles', '__pycache__', '.idea', '.vscode'}
        
        for root, dirs, files in os.walk(source_dir):
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                if file.endswith('.pyc') or file == zip_filename:
                    continue
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, source_dir)
                zipf.write(file_path, arcname)

create_zip('patosgym_deploy.zip', '.')
print("Created patosgym_deploy.zip")
