# 📂 Smart File Organizer Pro

**Le tri automatique, intelligent et en temps réel de vos fichiers.**

Smart File Organizer Pro est une application de bureau (Windows/Mac/Linux) conçue pour mettre fin au chaos du dossier "Téléchargements". Grâce à une surveillance en temps réel et un système de règles personnalisables, vos fichiers se rangent tout seuls dès qu'ils arrivent sur votre ordinateur.

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20|%20Mac%20|%20Linux-lightgrey)

---

## ✨ Fonctionnalités Principales

- 🚀 **Surveillance Temps Réel** : Détecte et trie les nouveaux fichiers instantanément.
- 🧠 **Règles Personnalisées** : Créez vos propres règles sur vos futurs fichiers (ex: tout fichier contenant "facture" va dans `/Finance`).
- 🚫 **Exclusions Intelligentes** : Protégez vos fichiers sensibles ou temporaires (.tmp, brouillons).
- 📊 **Dashboard Analytique** : Visualisez vos habitudes de fichiers avec des graphiques en temps réel.
- ↩️ **Système "Undo"** : Annulez le dernier tri en un clic en cas d'erreur.
- 📁 **Dossier "_À_Trier"** : Les fichiers sans mot-clé évident sont isolés pour un tri manuel rapide.
- 🌙 **Interface Moderne** : Design sombre (Dark Mode) ergonomique et fluide.

---

## 📥 Installation

### Option 1 : Utiliser l'exécutable (Recommandé pour Windows)
1. Téléchargez le fichier **`Release.zip`** dans la section [Releases](https://github.com/CrypticHacker-droid/SmartFileOrganizer-Pro/releases) de ce dépôt.
2. Décompressez le ZIP.
3. Lancez `SmartFileOrganizer.exe`.
> ⚠️ *Note de sécurité Windows : Si un écran bleu "Windows a protégé votre ordinateur" apparaît, cliquez sur "Informations complémentaires" puis "Exécuter quand même". C'est normal car l'application n'est pas signée par une entreprise certifiée.*

### Option 2 : Lancer depuis le Code Source (Python)
Si vous avez Python 3.10+ installé :
```bash
git clone https://github.com/CrypticHacker-droid/SmartFileOrganizer-Pro.git
cd SmartFileOrganizer-Pro
pip install -r requirements.txt
python app.py

🎯 Comment l'utiliser ?
Choisir le dossier : Dans l'onglet Organisateur, sélectionnez le dossier à surveiller (ex: C:\Users\Vous\Downloads).
Créer des règles : Allez dans l'onglet Règles. Ajoutez un mot-clé (ex: CV) et une catégorie de destination (ex: Personnel).
Ajouter des exclusions : Dans l'onglet Exclusions, ajoutez les extensions ou mots à ignorer (ex: .tmp, confidential).
Activer la surveillance : Cliquez sur ▶️ Démarrer la surveillance. C'est tout !
🛣️ Feuille de route (Roadmap)
Portage sur Android/iOS (via Flet/Flutter)
Analyse du contenu des PDF/DOCX pour un tri sémantique
Système de suggestions automatiques basé sur l'historique
Support multi-langues (EN/FR/ES)
🤝 Contribution
Les Pull Requests sont les bienvenues ! N'hésitez pas à ouvrir une Issue si vous trouvez un bug ou si vous avez une idée d'amélioration.
📄 Licence
Ce projet est sous licence MIT. Voir le fichier LICENSE pour plus de détails.


