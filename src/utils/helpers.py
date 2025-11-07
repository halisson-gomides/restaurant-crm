"""Utility helper functions for the Restaurant CRM system."""

from typing import Any, Dict


def safe_value(key: str, data: Dict[str, Any], default: str = '') -> Any:
    """
    Safely extract and return a value from data dictionary with proper encoding handling.
    
    Args:
        key: The key to look up in the data dictionary
        data: The dictionary containing the data
        default: Default value to return if key is not found
        
    Returns:
        The value from data dictionary with proper encoding handling
    """
    value = data.get(key, default)
    if isinstance(value, str):
        # Handle Unicode encoding issues properly
        try:
            return value.encode('latin1').decode('utf-8')
        except (UnicodeDecodeError, UnicodeEncodeError):
            return value
    return value


def option_selected(option_value: str, selected_value: str) -> str:
    """
    Generate HTML option selected attribute.
    
    Args:
        option_value: The option value
        selected_value: The currently selected value
        
    Returns:
        'selected' if option is selected, empty string otherwise
    """
    return 'selected' if option_value == selected_value else ''


def checkbox_checked(is_checked: bool) -> str:
    """
    Generate HTML checkbox checked attribute.
    
    Args:
        is_checked: Whether the checkbox should be checked
        
    Returns:
        'checked' if checkbox should be checked, empty string otherwise
    """
    return 'checked' if is_checked else ''


def radio_checked(radio_value: str, selected_value: str) -> str:
    """
    Generate HTML radio button checked attribute.
    
    Args:
        radio_value: The radio button value
        selected_value: The currently selected value
        
    Returns:
        'checked' if radio should be checked, empty string otherwise
    """
    return 'checked' if radio_value == selected_value else ''


def remove_accents(text):
    import unicodedata
    import re
    
    if not isinstance(text, str):
        return text
    # Normalize to NFD (Canonical Decomposition) to separate base characters from diacritics
    nfd_form = unicodedata.normalize('NFD', text)
    # Filter out combining characters (diacritics)
    stripped_text = ''.join(char for char in nfd_form if unicodedata.category(char) != 'Mn')
    # Normalize back to NFC (Canonical Composition) for a cleaner representation
    clean_text = unicodedata.normalize('NFC', stripped_text)
    # Removing special characters
    clean_text = re.sub(r'[^a-zA-Z0-9\s]', '', clean_text)
    return clean_text