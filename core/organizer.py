import os
import shutil
import json
from datetime import datetime
from pathlib import Path

class FileOrganizer:
    def __init__(self, config_path="config/settings.json"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        self.categories = self.config.get("default_categories", {})
        self.custom_rules = []
        self.exclusions = []
        self.history = []
        self.stats = {
            "files_moved": 0,
            "bytes_moved": 0,
            "start_date": datetime.now().isoformat()
        }
        
    def load_custom_rules(self, rules_file="custom_rules.json"):
        if os.path.exists(rules_file):
            with open(rules_file, 'r', encoding='utf-8') as f:
                self.custom_rules = json.load(f)
    
    def load_exclusions(self, exclusions_file="exclusions.json"):
        if os.path.exists(exclusions_file):
            with open(exclusions_file, 'r', encoding='utf-8') as f:
                self.exclusions = json.load(f)
    
    def save_stats(self, stats_file="stats.json"):
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, indent=2)
    
    def get_category(self, filename, filepath=""):
        # Vérifier les règles personnalisées d'abord
        for rule in self.custom_rules:
            if rule["type"] == "name_contains" and rule["value"].lower() in filename.lower():
                return rule["category"]
            elif rule["type"] == "extension" and filename.lower().endswith(rule["value"].lower()):
                return rule["category"]
        
        # Catégories par défaut
        ext = os.path.splitext(filename)[1].lower()
        for category, extensions in self.categories.items():
            if ext in extensions:
                return category
        
        # MODIFICATION ICI : Le dossier "À Trier" pour les fichiers sans mot-clé
        return "_À_Trier"
    
    def is_excluded(self, filename, filepath=""):
        for exclusion in self.exclusions:
            if exclusion in filename or exclusion in filepath:
                return True
        return False
    
    def move_file(self, src_path, watch_folder):
        if not os.path.isfile(src_path):
            return None, "Not a file"
        
        filename = os.path.basename(src_path)
        
        # Vérifier exclusions
        if self.is_excluded(filename, src_path):
            return None, "Excluded"
        
        # Vérifier fichiers verrouillés
        try:
            with open(src_path, 'rb') as f:
                pass
        except PermissionError:
            return None, "Locked"
        
        # Déterminer catégorie
        category = self.get_category(filename, src_path)
        dest_folder = os.path.join(watch_folder, category)
        os.makedirs(dest_folder, exist_ok=True)
        
        # Gestion conflits
        dest_path = os.path.join(dest_folder, filename)
        if os.path.exists(dest_path):
            name, ext = os.path.splitext(filename)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            new_filename = f"{name}_{timestamp}{ext}"
            dest_path = os.path.join(dest_folder, new_filename)
        
        # Déplacer
        try:
            file_size = os.path.getsize(src_path)
            shutil.move(src_path, dest_path)
            
            # Enregistrer dans l'historique
            record = {
                "timestamp": datetime.now().isoformat(),
                "original_path": src_path,
                "new_path": dest_path,
                "filename": os.path.basename(dest_path),
                "category": category,
                "size": file_size,
                "can_undo": True
            }
            self.history.append(record)
            
            # Mettre à jour stats
            self.stats["files_moved"] += 1
            self.stats["bytes_moved"] += file_size
            
            return record, None
        except Exception as e:
            return None, str(e)
    
    def undo_last_move(self):
        if not self.history:
            return False, "No history"
        
        # Trouver le dernier move avec can_undo=True
        for record in reversed(self.history):
            if record.get("can_undo", False):
                try:
                    if os.path.exists(record["new_path"]):
                        shutil.move(record["new_path"], record["original_path"])
                        record["can_undo"] = False
                        self.stats["files_moved"] -= 1
                        self.stats["bytes_moved"] -= record.get("size", 0)
                        return True, None
                except Exception as e:
                    return False, str(e)
        
        return False, "No undoable moves"
    
    def clean_existing(self, folder, recursive=False):
        moved_files = []
        errors = []
        
        if recursive:
            for root, dirs, files in os.walk(folder):
                # Skip les sous-dossiers de catégories
                if any(root.endswith(cat) for cat in self.categories.keys()):
                    continue
                for filename in files:
                    filepath = os.path.join(root, filename)
                    record, error = self.move_file(filepath, folder)
                    if record:
                        moved_files.append(record)
                    elif error and error not in ["Excluded", "Locked"]:
                        errors.append((filename, error))
        else:
            for filename in os.listdir(folder):
                filepath = os.path.join(folder, filename)
                if os.path.isfile(filepath):
                    record, error = self.move_file(filepath, folder)
                    if record:
                        moved_files.append(record)
                    elif error and error not in ["Excluded", "Locked"]:
                        errors.append((filename, error))
        
        return moved_files, errors
    
    def get_statistics(self):
        return {
            "total_files": self.stats["files_moved"],
            "total_size_mb": round(self.stats["bytes_moved"] / (1024 * 1024), 2),
            "categories_count": len(set(r["category"] for r in self.history)),
            "start_date": self.stats["start_date"]
        }