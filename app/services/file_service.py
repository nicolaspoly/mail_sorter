import os
import shutil

BASE_DIR = "organized"

import os
import shutil

def move_file(filepath, category):
    if not os.path.exists(filepath):
        print(f"❌ File not found: {filepath}")
        return None

    # ✅ dossier de destination
    new_dir = os.path.join("sorted", category)

    # ✅ crée le dossier s'il n'existe pas
    os.makedirs(new_dir, exist_ok=True)

    # ✅ chemin final du fichier
    new_path = os.path.join(new_dir, os.path.basename(filepath))

    shutil.move(filepath, new_path)

    print(f"✅ Moved {filepath} → {new_path}")

    return new_path
