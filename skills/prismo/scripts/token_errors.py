"""Categorias de validação de tokens compartilhadas."""
class UnsupportedTokenFormat(ValueError):
    """Formato válido ou desconhecido que o helper não consegue avaliar."""

class InvalidTokenType(ValueError):
    """Tipo DTCG inválido no conjunto suportado."""
