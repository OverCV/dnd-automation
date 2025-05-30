"""
Constantes de colores para la temática Arduino - PALETA ELEGANTE
"""


class ArduinoColors:
    """Paleta de colores Arduino elegante y profesional"""

    # Colores principales Arduino (mantenemos los originales como acentos)
    BLUE_LIGHT = "#4fccf3"  # Azul claro
    BLUE_MID = "#3186a0"  # Azul medio
    PURPLE = "#4a2370"  # Púrpura
    BLUE_DARK = "#1d2087"  # Azul oscuro

    # Colores de fondo elegantes (NO MÁS NEGRO HORRIBLE!)
    BACKGROUND_PRIMARY = "#f8f9fa"  # Gris muy claro elegante
    BACKGROUND_SECONDARY = "#e9ecef"  # Gris claro suave
    BACKGROUND_TERTIARY = "#dee2e6"  # Gris medio
    BACKGROUND_ACCENT = "#adb5bd"  # Gris azulado

    # Colores de texto legibles
    TEXT_PRIMARY = "#212529"  # Negro suave para texto
    TEXT_SECONDARY = "#495057"  # Gris oscuro para texto
    TEXT_ACCENT = "#6c757d"  # Gris medio para texto

    # Colores pastel complementarios mejorados
    PASTEL_GREEN = "#d4edda"  # Verde muy suave
    PASTEL_ORANGE = "#fff3cd"  # Amarillo suave
    PASTEL_PINK = "#f8d7da"  # Rosa muy suave
    PASTEL_BLUE = "#d1ecf1"  # Azul muy suave

    # Colores semánticos elegantes
    SUCCESS = "#28a745"  # Verde éxito
    WARNING = "#ffc107"  # Amarillo advertencia
    ERROR = "#dc3545"  # Rojo error
    INFO = "#17a2b8"  # Azul información

    # Aliases para compatibilidad (ELIMINAMOS BLACK!)
    BLACK = BACKGROUND_PRIMARY  # Ya no es negro!
    LIGHT_GRAY = BACKGROUND_SECONDARY

    @classmethod
    def get_theme_dict(cls):
        """Retorna diccionario con todos los colores para fácil acceso"""
        return {
            "bg_primary": cls.BACKGROUND_PRIMARY,
            "bg_secondary": cls.BACKGROUND_SECONDARY,
            "bg_tertiary": cls.BACKGROUND_TERTIARY,
            "bg_accent": cls.BACKGROUND_ACCENT,
            "fg_primary": cls.TEXT_PRIMARY,
            "fg_secondary": cls.TEXT_SECONDARY,
            "fg_accent": cls.TEXT_ACCENT,
            "btn_success": cls.SUCCESS,
            "btn_warning": cls.WARNING,
            "btn_error": cls.ERROR,
            "btn_info": cls.INFO,
            "arduino_blue": cls.BLUE_LIGHT,
            "arduino_purple": cls.PURPLE,
        }
