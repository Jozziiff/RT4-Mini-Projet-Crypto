"""
crypto_service.py — core cryptographique du système SecureShare
================================================================

Ce module implémente la logique de signature et de vérification des URLs
à l'aide d'un HMAC (Hash-based Message Authentication Code) basé sur SHA-256.

Pourquoi HMAC et non une simple fonction de hachage ?
------------------------------------------------------
Une fonction de hachage seule (ex: SHA-256(secret + données)) est vulnérable
à l'attaque par extension de longueur (length extension attack). HMAC résout
ce problème en appliquant le hachage en deux passes imbriquées :

    HMAC(K, m) = H((K ⊕ opad) || H((K ⊕ ipad) || m))

Cette construction garantit que sans la clé secrète K, il est impossible de
générer ou de modifier un code d'authentification valide.

Pourquoi SHA-256 ?
------------------
SHA-256 appartient à la famille SHA-2, standardisée par le NIST. Il produit
un condensat de 256 bits, ce qui offre une résistance aux collisions de l'ordre
de 2^128 (sécurité de 128 bits). Il est actuellement considéré comme sûr
pour les applications cryptographiques modernes.

Propriétés garanties par ce module :
- Intégrité   : toute modification des paramètres invalide la signature
- Authenticité : seul le détenteur de SECRET_KEY peut produire une signature valide
- Résistance aux timing attacks : comparaison en temps constant via compare_digest()
"""

import hmac
import hashlib
import time

from config import SECRET_KEY, EXPIRATION_SECONDS


def generate_signature(filename: str, expires: int) -> str:
    """
    Génère une signature HMAC-SHA256 pour un couple (filename, expires).

    Les deux paramètres sont concaténés en une chaîne "filename:expires"
    avant d'être signés. Cette liaison est essentielle : elle empêche un
    attaquant de réutiliser une signature valide avec des paramètres différents.

    Args:
        filename (str): Nom du fichier à signer.
        expires  (int): Timestamp UNIX représentant la date limite d'accès.

    Returns:
        str: Signature hexadécimale (64 caractères pour SHA-256).
    """
    # Les deux paramètres sont liés dans une seule chaîne avant signature.
    # Séparer filename et expires par ':' évite les ambiguïtés de concaténation
    # (ex: "file9" + "99" ≠ "file" + "999" avec le séparateur).
    data = f"{filename}:{expires}"

    signature = hmac.new(
        key=SECRET_KEY.encode("utf-8"),
        msg=data.encode("utf-8"),
        digestmod=hashlib.sha256
    ).hexdigest()

    return signature


def verify_signature(filename: str, expires: int, received_signature: str) -> bool:
    """
    Vérifie qu'une signature reçue est valide et que l'URL n'a pas expiré.

    La vérification s'effectue en deux étapes indépendantes :
    1. Vérification cryptographique de la signature (intégrité + authenticité)
    2. Vérification temporelle de l'expiration

    Cette séparation est intentionnelle : même si une URL est expirée,
    la validité de la signature reste vérifiable — utile pour la journalisation.

    Args:
        filename            (str): Nom du fichier extrait de l'URL.
        expires             (int): Timestamp d'expiration extrait de l'URL.
        received_signature  (str): Signature HMAC reçue dans l'URL.

    Returns:
        bool: True si la signature est valide ET l'URL non expirée, False sinon.
    """
    # Recalculer la signature attendue avec les mêmes paramètres.
    # Si filename ou expires ont été modifiés, expected != received.
    expected_signature = generate_signature(filename, expires)

    # hmac.compare_digest() effectue une comparaison en temps constant.
    # Une comparaison classique (==) s'arrête au premier caractère différent,
    # ce qui crée une fuite d'information exploitable (timing attack).
    signature_is_valid = hmac.compare_digest(expected_signature, received_signature)

    # Vérifier que le timestamp d'expiration n'est pas dépassé.
    # time.time() retourne le temps actuel en secondes depuis l'epoch UNIX.
    url_is_not_expired = time.time() < expires

    return signature_is_valid and url_is_not_expired


def generate_expiration_timestamp() -> int:
    """
    Calcule le timestamp UNIX d'expiration à partir du moment présent.

    Le délai d'expiration est défini dans config.py (EXPIRATION_SECONDS).
    Centraliser ce calcul ici garantit que toute l'application utilise
    la même logique temporelle.

    Returns:
        int: Timestamp UNIX du moment à partir duquel l'URL sera invalide.
    """
    return int(time.time()) + EXPIRATION_SECONDS