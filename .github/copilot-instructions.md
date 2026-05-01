# SYSTEM DIRECTIVE: COPILOT INSTRUCTIONS — SECURESHARE
CRITICAL: You are an expert academic programming assistant. You are writing code for the "SecureShare" project. You MUST strictly adhere to the constraints, architecture, and coding styles defined in this document. Any deviation from these rules is considered a fatal error. Never stray out of this context.

> Ces instructions définissent le comportement attendu de GitHub Copilot pour ce projet.
> Tout membre de l'équipe travaillant sur ce repo doit les respecter.

---

## Contexte du projet

**SecureShare** est un mini-projet académique implémentant un système de partage de fichiers
sécurisé par URLs signées cryptographiquement. Il est réalisé dans le cadre d'un cours de
sécurité des réseaux et de cryptographie appliquée à l'INSAT.

L'objectif est de produire un code **propre, pédagogique et bien documenté**, compréhensible
par un professeur qui évalue à la fois la maîtrise technique et la qualité de l'explication.

---

## Stack technique

| Composant     | Technologie                          |
|---------------|--------------------------------------|
| Backend       | Python 3.8+ avec Flask               |
| Cryptographie | `hmac` + `hashlib` (SHA-256) stdlib  |
| Frontend      | HTML + CSS vanilla (pas de framework)|
| Stockage      | Fichiers locaux dans `/storage`      |

**Ne jamais introduire :**
- JWT ou tout autre mécanisme de token externe
- Base de données (SQLite, PostgreSQL, etc.)
- Services cloud (AWS, GCP, Azure...)
- Frameworks frontend (React, Vue, Bootstrap...)
- Librairies cryptographiques tierces (`pycryptodome`, `cryptography`, etc.)

---

## Architecture — Séparation stricte des responsabilités

```
securesharee/
├── app.py                        # Initialisation Flask uniquement
├── config.py                     # Constantes globales (SECRET_KEY, EXPIRATION_SECONDS)
├── routes/
│   ├── upload.py                 # POST /upload — HTTP uniquement, pas de logique métier
│   └── download.py               # GET /download — HTTP uniquement, pas de logique métier
├── services/
│   ├── crypto_service.py         # HMAC : signature, vérification, expiration
│   ├── url_service.py            # Construction et parsing des URLs signées
│   └── file_service.py           # Lecture et écriture des fichiers dans /storage
├── templates/                    # Jinja2 — présentation uniquement
└── static/                       # CSS uniquement
```

**Règle absolue :** chaque fichier a une seule responsabilité.
- Les routes ne font **jamais** de cryptographie
- Les services ne font **jamais** d'I/O HTTP (pas de `request`, pas de `jsonify`)
- `config.py` est la **seule** source de vérité pour les constantes

---

## Logique cryptographique — À respecter exactement

La signature est calculée ainsi :

```
données    = "filename:expires"
signature  = HMAC(SECRET_KEY, données, SHA-256)
```

La vérification recompute la signature et la compare avec `hmac.compare_digest()`
(comparaison en temps constant — obligatoire pour éviter les timing attacks).

Ne jamais utiliser `==` pour comparer deux signatures HMAC.

---

## Style de code

### Langue
- **Code** (noms de variables, fonctions, classes) : **anglais**
- **Commentaires et docstrings** : **français**
- **Messages d'erreur HTTP** : **français**

### Formatage
- Indentation : 4 espaces (PEP8)
- Longueur de ligne maximale : 100 caractères
- Une ligne vide entre les blocs logiques à l'intérieur d'une fonction
- Deux lignes vides entre chaque fonction ou classe

### Nommage
- Fonctions et variables : `snake_case`
- Constantes : `UPPER_SNAKE_CASE`
- Pas d'abréviations ambiguës (`sig` est acceptable, `fn` ne l'est pas)

---

## Docstrings — Format obligatoire

Chaque fonction doit avoir une docstring structurée comme suit :

```python
def ma_fonction(param1: str, param2: int) -> bool:
    """
    Une phrase décrivant CE QUE fait la fonction et POURQUOI elle existe.

    Expliquer ici tout choix technique non évident (algorithme, structure
    de données, cas limite) — le "pourquoi", pas le "quoi".

    Args:
        param1 (str): Description du paramètre.
        param2 (int): Description du paramètre.

    Returns:
        bool: Ce que retourne la fonction et dans quelles conditions.
    """
```

Chaque fichier `.py` doit commencer par un **docstring de module** expliquant :
1. Le rôle du module dans l'architecture globale
2. Les choix techniques importants (algorithmes, patterns)
3. Ce que le module ne fait PAS (pour clarifier les frontières de responsabilité)

---

## Règles de commentaires

### Ce qu'un commentaire doit expliquer
Le **pourquoi**, jamais le quoi. Un commentaire doit apporter une information
que le code seul ne peut pas exprimer.

```python
# ✅ BON — explique une décision non évidente
# hmac.compare_digest() est utilisé à la place de == pour garantir une
# comparaison en temps constant et prévenir les attaques temporelles.
signature_is_valid = hmac.compare_digest(expected, received)

# ❌ MAUVAIS — répète ce que le code dit déjà
# Comparer les signatures
signature_is_valid = hmac.compare_digest(expected, received)
```

```python
# ✅ BON — justifie le choix du séparateur
# Le séparateur ':' lie filename et expires en une seule chaîne atomique.
# Sans lui, "file9" + "9" serait indiscernable de "file" + "99".
data = f"{filename}:{expires}"

# ❌ MAUVAIS — évident
# Créer la chaîne de données
data = f"{filename}:{expires}"
```

### Densité des commentaires
- Commenter les **décisions cryptographiques** systématiquement
- Commenter les **cas limites** et les **comportements défensifs**
- Ne pas commenter les imports, les assignations triviales, les prints de debug

---

## Gestion des erreurs

Les routes retournent des réponses HTTP claires avec le bon code de statut :

```python
# ✅ Format attendu pour les erreurs dans les routes
return {"erreur": "URL expirée ou signature invalide."}, 403
return {"erreur": "Paramètre manquant : filename."}, 400
return {"erreur": "Fichier introuvable."}, 404
```

Les services ne lèvent pas d'exceptions HTTP — ils retournent `None` ou `False`
et laissent la route décider de la réponse HTTP.

---

## Ce qu'il ne faut jamais faire

```python
# ❌ Comparer des signatures avec ==
if expected == received:  # vulnérable aux timing attacks

# ❌ Stocker SECRET_KEY en dur dans une route ou un service
SECRET_KEY = "abc123"  # appartient uniquement à config.py

# ❌ Logique métier dans une route
@app.route("/download")
def download():
    sig = hmac.new(...)  # la crypto appartient à crypto_service.py

# ❌ Accès à request dans un service
def verify_signature(request):  # les services ne connaissent pas Flask

# ❌ Commentaire inutile
x = x + 1  # incrémenter x
```

---

## Checklist avant chaque commit

- [ ] Le fichier a un docstring de module complet
- [ ] Chaque fonction a une docstring (Args + Returns + explication du pourquoi)
- [ ] Les commentaires expliquent des décisions, pas des évidences
- [ ] Aucune logique métier dans les routes
- [ ] Aucun accès HTTP dans les services
- [ ] `SECRET_KEY` n'apparaît que dans `config.py`
- [ ] Les signatures HMAC sont comparées avec `hmac.compare_digest()`
- [ ] Le code respecte PEP8 (indentation, espacement, nommage)