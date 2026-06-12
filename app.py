import os
import sys
import json
import threading
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
from pathlib import Path

# Imports pour les graphiques
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

# Import de notre moteur logique
from core.organizer import FileOrganizer

# ================= COULEURS & THÈME =================
COLORS = {
    "bg": "#1e1e2e", "fg": "#cdd6f4", "accent": "#89b4fa",
    "success": "#a6e3a1", "danger": "#f38ba8", "warning": "#f9e2af",
    "surface": "#313244", "text_muted": "#a6adc8"
}

class SmartOrganizerPro:
    def __init__(self, root):
        self.root = root
        self.root.title("Smart File Organizer Pro v2.0")
        self.root.geometry("1000x700")
        self.root.configure(bg=COLORS["bg"])
        self.root.minsize(800, 600)

        # Initialisation du moteur
        self.organizer = FileOrganizer("config/settings.json")
        self.organizer.load_custom_rules()
        self.organizer.load_exclusions()

        self.watch_folder = tk.StringVar(value=str(Path.home() / "Downloads"))
        self.is_watching = False
        self.observer = None

        self.setup_ui()
        self.update_dashboard()

    # ================= INTERFACE GRAPHIQUE =================
    def setup_ui(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TFrame', background=COLORS["bg"])
        style.configure('TLabel', background=COLORS["bg"], foreground=COLORS["fg"], font=('Segoe UI', 10))
        style.configure('Title.TLabel', font=('Segoe UI', 24, 'bold'), foreground=COLORS["accent"])
        style.configure('TButton', font=('Segoe UI', 10, 'bold'), padding=8)
        style.configure('TNotebook', background=COLORS["bg"], borderwidth=0)
        style.configure('TNotebook.Tab', background=COLORS["surface"], foreground=COLORS["fg"], padding=[20, 10], font=('Segoe UI', 10, 'bold'))
        style.map('TNotebook.Tab', background=[('selected', COLORS["accent"])], foreground=[('selected', '#1e1e2e')])

        # Header
        header = ttk.Frame(self.root)
        header.pack(fill='x', padx=20, pady=15)
        ttk.Label(header, text="📂 Smart File Organizer Pro", style='Title.TLabel').pack(side='left')
        
        self.status_var = tk.StringVar(value="🟡 En attente...")
        ttk.Label(header, textvariable=self.status_var, foreground=COLORS["warning"]).pack(side='right')

        # Notebook (Onglets)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=20, pady=10)

        self.create_organizer_tab()
        self.create_dashboard_tab()
        self.create_rules_tab()
        self.create_exclusions_tab()

    def create_organizer_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="  🖥️ Organisateur  ")

        # Sélection dossier
        folder_frame = ttk.Frame(frame)
        folder_frame.pack(fill='x', pady=10)
        ttk.Label(folder_frame, text="Dossier à surveiller :").pack(side='left')
        ttk.Entry(folder_frame, textvariable=self.watch_folder, width=60).pack(side='left', padx=10)
        ttk.Button(folder_frame, text="📁 Parcourir", command=self.browse_folder).pack(side='left')

        # Boutons
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill='x', pady=10)
        self.toggle_btn = ttk.Button(btn_frame, text="▶️ Démarrer la surveillance", command=self.toggle_watch)
        self.toggle_btn.pack(side='left', expand=True, fill='x', padx=(0, 5))
        ttk.Button(btn_frame, text="🧹 Trier l'existant", command=self.clean_existing).pack(side='left', expand=True, fill='x', padx=5)
        ttk.Button(btn_frame, text="↩️ Annuler dernier tri", command=self.undo_last).pack(side='left', expand=True, fill='x')

        # Journal
        log_frame = ttk.Frame(frame)
        log_frame.pack(fill='both', expand=True, pady=10)
        ttk.Label(log_frame, text="📜 Journal d'activité :", font=('Segoe UI', 10, 'bold')).pack(anchor='w')
        
        self.log_text = tk.Text(log_frame, bg='#11111b', fg=COLORS["text_muted"], font=('Consolas', 9), state='disabled', wrap='word')
        self.log_text.pack(fill='both', expand=True, pady=5)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')

    def create_dashboard_tab(self):
        self.dash_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.dash_frame, text="  📊 Tableau de bord  ")
        
        # Stats cards
        stats_frame = ttk.Frame(self.dash_frame)
        stats_frame.pack(fill='x', pady=10)
        
        self.stat_files = tk.StringVar(value="Fichiers triés : 0")
        self.stat_size = tk.StringVar(value="Espace libéré : 0 Mo")
        
        ttk.Label(stats_frame, textvariable=self.stat_files, font=('Segoe UI', 14, 'bold'), foreground=COLORS["success"]).pack(side='left', expand=True)
        ttk.Label(stats_frame, textvariable=self.stat_size, font=('Segoe UI', 14, 'bold'), foreground=COLORS["accent"]).pack(side='right', expand=True)

        # Graphique
        self.fig = Figure(figsize=(6, 4), dpi=100, facecolor=COLORS["bg"])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(COLORS["bg"])
        self.ax.tick_params(colors=COLORS["text_muted"])
        self.ax.title.set_color(COLORS["fg"])
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.dash_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)

    def create_rules_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="  ⚙️ Règles  ")
        
        # Titre et description
        ttk.Label(frame, text="Créez des règles personnalisées", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Exemple: Si le nom contient 'facture' → déplacer dans /Finance/", 
                 foreground=COLORS["text_muted"]).pack(pady=5)
        
        # Formulaire d'ajout
        form_frame = ttk.LabelFrame(frame, text="Ajouter une règle", padding=10)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Mot-clé dans le nom :").grid(row=0, column=0, sticky='w', pady=5)
        self.rule_keyword = ttk.Entry(form_frame, width=30)
        self.rule_keyword.grid(row=0, column=1, padx=10, pady=5)
        
        ttk.Label(form_frame, text="Catégorie de destination :").grid(row=1, column=0, sticky='w', pady=5)
        self.rule_category = ttk.Entry(form_frame, width=30)
        self.rule_category.grid(row=1, column=1, padx=10, pady=5)
        ttk.Label(form_frame, text="(ex: Finance, Personnel, Travail)", 
                 foreground=COLORS["text_muted"]).grid(row=1, column=2, padx=5)
        
        ttk.Button(form_frame, text="➕ Ajouter la règle", command=self.add_rule).grid(row=2, column=0, columnspan=3, pady=10)
        
        # Liste des règles
        list_frame = ttk.LabelFrame(frame, text="Règles existantes", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.rules_tree = ttk.Treeview(list_frame, columns=("Keyword", "Category"), show='headings', height=8)
        self.rules_tree.heading("Keyword", text="Mot-clé")
        self.rules_tree.heading("Category", text="Catégorie")
        self.rules_tree.column("Keyword", width=300)
        self.rules_tree.column("Category", width=200)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.rules_tree.yview)
        self.rules_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rules_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Bouton supprimer
        ttk.Button(frame, text="🗑️ Supprimer la règle sélectionnée", 
                  command=self.delete_rule).pack(pady=5)
        
        self.refresh_rules_list()

    def create_exclusions_tab(self):
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="  🚫 Exclusions  ")
        
        # Titre et description
        ttk.Label(frame, text="Fichiers et dossiers à ignorer", font=('Segoe UI', 12, 'bold')).pack(pady=10)
        ttk.Label(frame, text="Les fichiers contenant ces mots ne seront jamais déplacés", 
                 foreground=COLORS["text_muted"]).pack(pady=5)
        
        # Formulaire d'ajout
        form_frame = ttk.LabelFrame(frame, text="Ajouter une exclusion", padding=10)
        form_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(form_frame, text="Mot ou extension à exclure :").grid(row=0, column=0, sticky='w', pady=5)
        self.exclusion_entry = ttk.Entry(form_frame, width=40)
        self.exclusion_entry.grid(row=0, column=1, padx=10, pady=5)
        ttk.Label(form_frame, text="(ex: .tmp, confidential, draft)", 
                 foreground=COLORS["text_muted"]).grid(row=0, column=2, padx=5)
        
        ttk.Button(form_frame, text="➕ Ajouter l'exclusion", 
                  command=self.add_exclusion).grid(row=1, column=0, columnspan=3, pady=10)
        
        # Liste des exclusions
        list_frame = ttk.LabelFrame(frame, text="Exclusions actives", padding=10)
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        self.exclusions_listbox = tk.Listbox(list_frame, bg='#11111b', fg=COLORS["fg"], 
                                             font=('Segoe UI', 10), selectbackground=COLORS["accent"])
        self.exclusions_listbox.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.exclusions_listbox.yview)
        self.exclusions_listbox.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side='right', fill='y')
        
        # Bouton supprimer
        ttk.Button(frame, text="🗑️ Supprimer l'exclusion sélectionnée", 
                  command=self.delete_exclusion).pack(pady=5)
        
        self.refresh_exclusions_list()

    # ================= RÈGLES PERSONNALISÉES =================
    def add_rule(self):
        keyword = self.rule_keyword.get().strip()
        category = self.rule_category.get().strip()
        
        if not keyword or not category:
            messagebox.showwarning("Erreur", "Veuillez remplir tous les champs")
            return
        
        # Ajouter la règle
        self.organizer.custom_rules.append({
            "type": "name_contains",
            "value": keyword,
            "category": category
        })
        
        # Sauvegarder
        self.save_custom_rules()
        
        # Refresh UI
        self.refresh_rules_list()
        self.rule_keyword.delete(0, tk.END)
        self.rule_category.delete(0, tk.END)
        self.log(f"✅ Règle ajoutée: '{keyword}' → /{category}/")
    
    def delete_rule(self):
        selection = self.rules_tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez une règle à supprimer")
            return
        
        item = self.rules_tree.item(selection[0])
        keyword = item['values'][0]
        
        # Supprimer la règle
        self.organizer.custom_rules = [r for r in self.organizer.custom_rules 
                                       if r.get('value') != keyword]
        self.save_custom_rules()
        self.refresh_rules_list()
        self.log(f"🗑️ Règle supprimée: '{keyword}'")
    
    def refresh_rules_list(self):
        # Vider la liste
        for item in self.rules_tree.get_children():
            self.rules_tree.delete(item)
        
        # Remplir avec les règles
        for rule in self.organizer.custom_rules:
            if rule.get('type') == 'name_contains':
                self.rules_tree.insert("", "end", values=(rule['value'], rule['category']))
    
    def save_custom_rules(self):
        with open("custom_rules.json", 'w', encoding='utf-8') as f:
            json.dump(self.organizer.custom_rules, f, indent=2, ensure_ascii=False)

    # ================= EXCLUSIONS =================
    def add_exclusion(self):
        exclusion = self.exclusion_entry.get().strip()
        
        if not exclusion:
            messagebox.showwarning("Erreur", "Veuillez entrer un motif d'exclusion")
            return
        
        if exclusion not in self.organizer.exclusions:
            self.organizer.exclusions.append(exclusion)
            self.save_exclusions()
            self.refresh_exclusions_list()
            self.exclusion_entry.delete(0, tk.END)
            self.log(f"🚫 Exclusion ajoutée: '{exclusion}'")
        else:
            messagebox.showinfo("Info", "Cette exclusion existe déjà")
    
    def delete_exclusion(self):
        selection = self.exclusions_listbox.curselection()
        if not selection:
            messagebox.showwarning("Attention", "Sélectionnez une exclusion à supprimer")
            return
        
        exclusion = self.exclusions_listbox.get(selection[0])
        self.organizer.exclusions.remove(exclusion)
        self.save_exclusions()
        self.refresh_exclusions_list()
        self.log(f"✅ Exclusion supprimée: '{exclusion}'")
    
    def refresh_exclusions_list(self):
        self.exclusions_listbox.delete(0, tk.END)
        for exclusion in self.organizer.exclusions:
            self.exclusions_listbox.insert(tk.END, exclusion)
    
    def save_exclusions(self):
        with open("exclusions.json", 'w', encoding='utf-8') as f:
            json.dump(self.organizer.exclusions, f, indent=2, ensure_ascii=False)

    # ================= LOGIQUE MÉTIER =================
    def browse_folder(self):
        folder = filedialog.askdirectory()
        if folder: 
            self.watch_folder.set(folder)

    def toggle_watch(self):
        if not self.is_watching:
            self.start_watching()
        else:
            self.stop_watching()

    def start_watching(self):
        from watchdog.observers import Observer
        from watchdog.events import FileSystemEventHandler
        
        class Handler(FileSystemEventHandler):
            def __init__(self, app): 
                self.app = app
            def on_created(self, event):
                if not event.is_directory:
                    self.app.process_file_async(event.src_path)

        self.is_watching = True
        self.toggle_btn.config(text="⏹️ Arrêter")
        self.status_var.set("🟢 Surveillance active...")
        self.log("Surveillance démarrée.")

        self.observer = Observer()
        self.observer.schedule(Handler(self), self.watch_folder.get(), recursive=False)
        self.observer.start()

    def stop_watching(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        self.is_watching = False
        self.toggle_btn.config(text="▶️ Démarrer")
        self.status_var.set("🟡 En attente...")
        self.log("Surveillance arrêtée.")

    def process_file_async(self, filepath):
        threading.Thread(target=self.process_file, args=(filepath,), daemon=True).start()

    def process_file(self, filepath):
        time.sleep(1) # Laisse le temps au fichier de se verrouiller/déverrouiller
        record, error = self.organizer.move_file(filepath, self.watch_folder.get())
        if record:
            self.root.after(0, lambda: self.log(f"✅ {record['filename']} -> /{record['category']}/"))
            self.root.after(0, self.update_dashboard)
        elif error and error not in ["Excluded", "Locked"]:
            self.root.after(0, lambda: self.log(f"❌ Erreur: {error}"))

    def clean_existing(self):
        threading.Thread(target=self._clean_thread, daemon=True).start()

    def _clean_thread(self):
        self.log("🧹 Nettoyage en cours...")
        moved, errors = self.organizer.clean_existing(self.watch_folder.get())
        self.root.after(0, lambda: self.log(f"🎉 {len(moved)} fichiers triés."))
        self.root.after(0, self.update_dashboard)

    def undo_last(self):
        success, msg = self.organizer.undo_last_move()
        if success:
            self.log("↩️ Dernier tri annulé.")
            self.update_dashboard()
        else:
            messagebox.showwarning("Undo", "Aucun tri à annuler.")

    def update_dashboard(self):
        stats = self.organizer.get_statistics()
        self.stat_files.set(f"Fichiers triés : {stats['total_files']}")
        self.stat_size.set(f"Espace organisé : {stats['total_size_mb']} Mo")
        
        # Mise à jour du graphique
        self.ax.clear()
        categories = {}
        for r in self.organizer.history:
            cat = r['category']
            categories[cat] = categories.get(cat, 0) + 1
        
        if categories:
            colors = [COLORS["accent"], COLORS["success"], COLORS["warning"], COLORS["danger"], "#cba6f7", "#fab387"]
            self.ax.pie(categories.values(), labels=categories.keys(), autopct='%1.1f%%', 
                        colors=colors[:len(categories)], textprops={'color': COLORS["fg"]})
            self.ax.set_title("Répartition par catégorie", color=COLORS["fg"])
        else:
            self.ax.text(0.5, 0.5, "Aucune donnée", ha='center', va='center', color=COLORS["text_muted"])
        
        self.fig.tight_layout()
        self.canvas.draw()

    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        def _update():
            self.log_text.config(state='normal')
            self.log_text.insert('end', f"[{timestamp}] {message}\n")
            self.log_text.see('end')
            self.log_text.config(state='disabled')
        self.root.after(0, _update)

    def on_closing(self):
        if messagebox.askokcancel("Quitter", "Voulez-vous vraiment quitter ?"):
            self.stop_watching()
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SmartOrganizerPro(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()