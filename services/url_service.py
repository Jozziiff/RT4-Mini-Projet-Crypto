"""
url_service.py — Construction et parsing des URLs signées
==========================================================

Ce module est responsable de la composition et de la décomposition des URLs
signées. Il fait le lien entre la logique cryptographique (crypto_service.py)
et les routes HTTP (routes/download.py).

Responsabilité unique : ce module ne fait pas de cryptographie lui-même.
Il délègue entièrement la signature à crypto_service.py et se concentre
sur la structure de l'URL.

Anatomie d'une URL signée générée par ce module :
--------------------------------------------------
    /download?filename=rapport.pdf&expires=1712345678&signature=a3f9c2...

    - filename  : nom du fichier tel qu'il est stocké dans /storage
    - expires   : timestamp UNIX (entier) représentant la limite de validité
    - signature : condensat HMAC-SHA256 hexadécimal liant filename et expires
"""

from urllib.parse import urlencode, urljoin

from services.crypto_service import generate_signature, generate_expiration_timestamp


def build_signed_url(base_url: str, filename: str) -> str:
    """
    Construit une URL signée et temporaire donnant accès à un fichier.

    Le timestamp d'expiration est calculé au moment de l'appel, puis inclus
    dans les données signées. Cela garantit qu'un attaquant ne peut pas
    prolonger la durée de validité sans invalider la signature.

    Args:
        base_url (str): URL de base du serveur (ex: "http://localhost:5000").
        filename (str): Nom du fichier pour lequel générer l'accès.

    Returns:
        str: URL complète et signée prête à être partagée.

    Exemple:
        >>> build_signed_url("http://localhost:5000", "rapport.pdf")
        "http://localhost:5000/download?filename=rapport.pdf&expires=...&signature=..."
    """
    expires = generate_expiration_timestamp()

    # La signature couvre filename ET expires : modifier l'un ou l'autre
    # rend la signature invalide côté serveur.
    signature = generate_signature(filename, expires)

    # urlencode() encode correctement les caractères spéciaux dans les paramètres
    # (espaces, accents, etc.), ce qui est essentiel pour des noms de fichiers arbitraires.
    params = urlencode({
        "filename": filename,
        "expires": expires,
        "signature": signature
    })

    return f"{base_url}/download?{params}"


def parse_signed_url_params(args: dict) -> tuple[str, int, str] | tuple[None, None, None]:
    """
    Extrait et valide les paramètres d'une requête de téléchargement.

    Cette fonction isole la logique d'extraction des paramètres HTTP,
    ce qui évite que les routes manipulent directement les query strings
    et simplifie les tests unitaires.

    Args:
        args (dict): Dictionnaire des paramètres de la requête (request.args de Flask).

    Returns:
        tuple: (filename, expires, signature) si tous les paramètres sont présents,
                (None, None, None) si un paramètre est manquant ou mal formé.
    """
    filename  = args.get("filename")
    signature = args.get("signature")

    # expires doit être un entier valide, une valeur non numérique
    # indique une URL malformée ou une tentative de manipulation.
    try:
        expires = int(args.get("expires"))
    except (TypeError, ValueError):
        return None, None, None

    # Les trois paramètres sont obligatoires pour qu'une vérification soit possible.
    if not filename or not signature:
        return None, None, None

    return filename, expires, signature