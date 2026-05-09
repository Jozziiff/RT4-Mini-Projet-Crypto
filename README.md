<div align="center">

# SecureShare

### Partage de fichiers sécurisé par URLs signées

*Un projet académique sur la cryptographie appliquée au web*

---

![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white)
![HMAC](https://img.shields.io/badge/Crypto-HMAC--SHA256-FF6B35?style=for-the-badge&logo=letsencrypt&logoColor=white)
![License](https://img.shields.io/badge/Licence-MIT-22C55E?style=for-the-badge)
![Status](https://img.shields.io/badge/Statut-Académique-8B5CF6?style=for-the-badge)

</div>

---

## Vue d'ensemble

**SecureShare** est un système minimaliste de partage de fichiers dont l'accès est contrôlé par des **URLs signées cryptographiquement**. Au lieu d'exposer directement les chemins des fichiers stockés, le serveur génère des URLs à durée limitée dont l'intégrité est garantie par une signature **HMAC-SHA256**.

> Toute tentative de modification de l'URL (nom du fichier, date d'expiration) invalide immédiatement la signature et bloque l'accès.

Ce projet illustre, de manière pédagogique, comment les primitives cryptographiques s'appliquent à un problème concret du web — sans JWT, sans base de données, sans infrastructure cloud.

---

## Fonctionnalités

| Fonctionnalité | Description |
|---|---|
| **Upload de fichier** | Dépôt de fichiers via un formulaire web simple |
| **Validation serveur** | Nettoyage du nom, extensions autorisées, rejet des doublons |
| **Génération d'URL signée** | URL contenant le nom, l'expiration et la signature HMAC |
| **Vérification cryptographique** | Rejet automatique de toute URL modifiée ou expirée |
| **Téléchargement sécurisé** | Accès accordé uniquement si la signature est valide |

---

## Architecture du projet

```
SecureShare/
│
├── app.py                  # Point d'entrée — initialisation Flask + création de /storage
├── config.py               # Clé secrète et durée d'expiration
│
├── routes/
│   ├── upload.py           # POST /upload — réception et stockage du fichier
│   └── download.py         # GET /download — vérification et envoi du fichier
│
├── services/
│   ├── crypto_service.py   # Génération et vérification de la signature HMAC
│   ├── file_service.py     # Nettoyage du nom + écriture dans /storage
│   └── url_service.py      # Construction et parsing des URLs signées
│
├── templates/
│   ├── index.html          # Formulaire d'upload
│   └── success.html        # Affichage de l'URL générée
│
├── static/
│   └── style.css           # Feuille de style minimaliste
│
└── storage/                # Fichiers uploadés (créé automatiquement au démarrage)
```

Chaque couche a une responsabilité unique et bien définie. Les routes gèrent le HTTP. Les services encapsulent la logique. Les templates gèrent la présentation.

---

## Logique cryptographique

La sécurité du système repose entièrement sur le secret de `SECRET_KEY` et les propriétés de **HMAC-SHA256**.

### Génération de la signature

```
données    =  "nom_fichier:timestamp_expiration"
signature  =  HMAC(SECRET_KEY, données, SHA-256)
```

### URL signée générée

```
/download?filename=rapport.pdf&expires=1712345678&signature=a3f9c2...
```

### Vérification côté serveur

```
1. Recalculer la signature attendue à partir de filename + expires
2. Comparer avec la signature reçue (comparaison en temps constant)
3. Vérifier que expires > temps actuel
```

### Propriétés de sécurité garanties

| Propriété | Mécanisme |
|---|---|
| **Intégrité** | Toute modification de `filename` ou `expires` change le HMAC |
| **Authenticité** | Seul le serveur détenant `SECRET_KEY` peut produire une signature valide |
| **Expiration** | `expires` est inclus dans les données signées — il ne peut pas être étendu |
| **Anti-timing attack** | Comparaison via `hmac.compare_digest()` pour éviter les attaques temporelles |

> C'est le même mécanisme conceptuel utilisé en production par AWS S3 (pre-signed URLs) ou Google Cloud Storage — simplifié ici à des fins pédagogiques.

---

## Installation et lancement

### Prérequis

- Python 3.8 ou supérieur
- pip

### Étapes

```bash
# 1. Cloner le dépôt
git clone https://github.com/Jozziiff/RT4-Mini-Projet-Crypto.git
cd RT4-Mini-Projet-Crypto

# 2. (Optionnel) Créer un environnement virtuel
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Lancer le serveur
python app.py
```

L'application est accessible sur **http://localhost:5000**

---

## Utilisation

1. Ouvrir http://localhost:5000
2. Sélectionner un fichier (txt, pdf, png, jpg) de 5 MB maximum
3. Envoyer le fichier via le formulaire
4. Copier l'URL signée générée ou cliquer sur "Télécharger maintenant"
5. Après expiration, la même URL est refusée

Notes :
- Si un fichier du même nom existe déjà, l'upload est refusé
- Le nom est nettoyé côté serveur pour éviter les chemins dangereux

## Endpoints HTTP

- `GET /` : interface web d'upload
- `POST /upload` : réception du fichier, génération de l'URL signée
- `GET /download` : téléchargement sécurisé via paramètres `filename`, `expires`, `signature`
- `GET /generate-link/<filename>` : génère une URL signée pour un fichier déjà stocké

---

## Configuration

Les paramètres du système sont centralisés dans `config.py` :

```python
# Clé secrète utilisée pour signer les URLs
# En production, cette valeur doit être chargée depuis une variable d'environnement
SECRET_KEY = "votre-cle-secrete"

# Durée de validité des URLs signées (en secondes)
EXPIRATION_SECONDS = 300  # 5 minutes
```

Le serveur limite aussi la taille des fichiers à 5 MB via `MAX_CONTENT_LENGTH` dans `app.py`.

Si vous déployez ailleurs que sur `http://127.0.0.1:5000`, remplacez l'URL de base
dans `routes/upload.py` et `app.py` (fonction `build_signed_url`).

> Ne jamais versionner `SECRET_KEY` dans un dépôt public. En production, utiliser une variable d'environnement ou un gestionnaire de secrets.

---

## Dépendances

| Bibliothèque | Rôle |
|---|---|
| `flask` | Serveur HTTP et routage |
| `hmac` | Génération et vérification de la signature |
| `hashlib` | Algorithme SHA-256 (utilisé en interne par `hmac`) |
| `time` | Horodatage UNIX pour l'expiration |
| `urllib.parse` | Encodage des paramètres d'URL |
| `os`, `re` | Gestion des fichiers et nettoyage des noms |

Seul Flask est externe. Toutes les autres dépendances font partie de la bibliothèque standard Python.

---

## Documentation académique

Un guide détaillé et pédagogique expliquant le fonctionnement complet du projet est
disponible dans `ACADEMIC_OVERVIEW.md`.

---

## Auteurs

Projet réalisé dans le cadre d'un mini-projet académique sur la cryptographie appliquée et la sécurité web

---

<div align="center">

*Projet académique — Institut National des Sciences Appliquées et de Technologie (INSAT)*

</div>
