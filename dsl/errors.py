class DSLError(Exception):
    """Base exception for DSL validation and parsing errors."""

class DSLValidationError(DSLError): # Errores semanticos
    """Raised when the script is syntactically valid but semantically invalid."""

class DSLSyntaxError(DSLError):
    """Raised when the lexer or parser finds invalid syntax."""