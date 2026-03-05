"""
Localization System for AI Valido Online
Handles multi-language support with Serbian as primary language
"""

import os
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from functools import wraps
from flask import request, session, g, current_app
from babel import Locale, UnknownLocaleError
from babel.support import Translations
from babel.messages import Catalog, Message
from babel.messages.pofile import read_po, write_po
from babel.messages.mofile import write_mo
import gettext
from src.config.unified_config import config

logger = logging.getLogger(__name__)

class LanguageInfo:
    """Language information structure"""
    
    def __init__(self, code: str, name: str, native_name: str, flag: str = None, rtl: bool = False):
        self.code = code
        self.name = name
        self.native_name = native_name
        self.flag = flag or f"flag-{code.lower()}"
        self.rtl = rtl

class LocalizationManager:
    """
    Manages localization and translations for the application
    """
    
    def __init__(self):
        self.config = config.localization
        self.translations_path = Path(self.config.translation_files_path)
        self.translations_path.mkdir(parents=True, exist_ok=True)
        
        # Supported languages with their information
        self.languages = {
            'sr': LanguageInfo('sr', 'Serbian', 'Српски', '🇷🇸'),
            'en': LanguageInfo('en', 'English', 'English', '🇺🇸'),
            'sl': LanguageInfo('sl', 'Slovenian', 'Slovenščina', '🇸🇮'),
            'sk': LanguageInfo('sk', 'Slovak', 'Slovenčina', '🇸🇰'),
            'hu': LanguageInfo('hu', 'Hungarian', 'Magyar', '🇭🇺'),
            'de': LanguageInfo('de', 'German', 'Deutsch', '🇩🇪'),
            'es': LanguageInfo('es', 'Spanish', 'Español', '🇪🇸'),
            'it': LanguageInfo('it', 'Italian', 'Italiano', '🇮🇹'),
            'nl': LanguageInfo('nl', 'Dutch', 'Nederlands', '🇳🇱'),
            'fr': LanguageInfo('fr', 'French', 'Français', '🇫🇷'),
            'pt': LanguageInfo('pt', 'Portuguese', 'Português', '🇵🇹'),
            'pl': LanguageInfo('pl', 'Polish', 'Polski', '🇵🇱'),
            'cs': LanguageInfo('cs', 'Czech', 'Čeština', '🇨🇿'),
            'ro': LanguageInfo('ro', 'Romanian', 'Română', '🇷🇴'),
            'bg': LanguageInfo('bg', 'Bulgarian', 'Български', '🇧🇬'),
            'hr': LanguageInfo('hr', 'Croatian', 'Hrvatski', '🇭🇷'),
            'mk': LanguageInfo('mk', 'Macedonian', 'Македонски', '🇲🇰'),
            'bs': LanguageInfo('bs', 'Bosnian', 'Bosanski', '🇧🇦'),
            'tr': LanguageInfo('tr', 'Turkish', 'Türkçe', '🇹🇷'),
            'ru': LanguageInfo('ru', 'Russian', 'Русский', '🇷🇺'),
            'zh': LanguageInfo('zh', 'Chinese', '中文', '🇨🇳'),
            'ja': LanguageInfo('ja', 'Japanese', '日本語', '🇯🇵'),
            'ko': LanguageInfo('ko', 'Korean', '한국어', '🇰🇷'),
            'ar': LanguageInfo('ar', 'Arabic', 'العربية', '🇸🇦', rtl=True),
            'hi': LanguageInfo('hi', 'Hindi', 'हिन्दी', '🇮🇳'),
        }
        
        # Translation cache
        self._translation_cache = {}
        self._gettext_translations = {}
        
        # Initialize translations
        self._initialize_translations()
    
    def _initialize_translations(self):
        """Initialize translation files and load them"""
        for lang_code in self.config.supported_languages:
            if lang_code in self.languages:
                self._load_translations(lang_code)
    
    def _load_translations(self, lang_code: str):
        """Load translations for a specific language"""
        try:
            # Create language directory
            lang_dir = self.translations_path / lang_code / 'LC_MESSAGES'
            lang_dir.mkdir(parents=True, exist_ok=True)
            
            # Translation file paths
            po_file = lang_dir / 'messages.po'
            mo_file = lang_dir / 'messages.mo'
            
            # Create default translation file if it doesn't exist
            if not po_file.exists():
                self._create_default_translation_file(lang_code, po_file)
            
            # Compile .po to .mo if needed
            if po_file.exists() and (not mo_file.exists() or po_file.stat().st_mtime > mo_file.stat().st_mtime):
                self._compile_translation(po_file, mo_file)
            
            # Load gettext translations
            if mo_file.exists():
                translations = gettext.translation('messages', str(self.translations_path), languages=[lang_code])
                self._gettext_translations[lang_code] = translations
            
            logger.info(f"Loaded translations for language: {lang_code}")
            
        except Exception as e:
            logger.error(f"Error loading translations for {lang_code}: {e}")
    
    def _create_default_translation_file(self, lang_code: str, po_file: Path):
        """Create default translation file for a language"""
        try:
            catalog = Catalog()
            
            # Add default messages (these will be in Serbian/English)
            default_messages = self._get_default_messages()
            
            for msg_id, msg_str in default_messages.items():
                message = Message(msg_id, msg_str)
                catalog.add(message)
            
            # Write the .po file
            with open(po_file, 'w', encoding='utf-8') as f:
                write_po(f, catalog)
            
            logger.info(f"Created default translation file for {lang_code}")
            
        except Exception as e:
            logger.error(f"Error creating translation file for {lang_code}: {e}")
    
    def _get_default_messages(self) -> Dict[str, str]:
        """Get default messages for translation"""
        return {
            # Navigation
            'Dashboard': 'Dashboard',
            'Finance': 'Finance',
            'Global Finance': 'Global Finance',
            'Business Management': 'Business Management',
            'Settings': 'Settings',
            'Profile': 'Profile',
            'Logout': 'Logout',
            
            # Common actions
            'Save': 'Save',
            'Cancel': 'Cancel',
            'Delete': 'Delete',
            'Edit': 'Edit',
            'Add': 'Add',
            'Search': 'Search',
            'Filter': 'Filter',
            'Export': 'Export',
            'Import': 'Import',
            'Download': 'Download',
            'Upload': 'Upload',
            
            # Status messages
            'Success': 'Success',
            'Error': 'Error',
            'Warning': 'Warning',
            'Info': 'Info',
            'Loading': 'Loading',
            'Processing': 'Processing',
            'Completed': 'Completed',
            'Failed': 'Failed',
            
            # Financial terms
            'Invoice': 'Invoice',
            'Payment': 'Payment',
            'Tax': 'Tax',
            'Revenue': 'Revenue',
            'Expense': 'Expense',
            'Profit': 'Profit',
            'Loss': 'Loss',
            'Balance': 'Balance',
            'Account': 'Account',
            'Transaction': 'Transaction',
            
            # Serbian business specific
            'PIB': 'PIB',
            'Matični broj': 'Matični broj',
            'Preduzetnik': 'Preduzetnik',
            'DOO': 'DOO',
            'AD': 'AD',
            'OD': 'OD',
            'KD': 'KD',
            'PDV': 'PDV',
            'Withholding Tax': 'Withholding Tax',
            
            # Settings
            'Language': 'Language',
            'Theme': 'Theme',
            'Notifications': 'Notifications',
            'Security': 'Security',
            'API Keys': 'API Keys',
            'JWT Tokens': 'JWT Tokens',
            'Configuration': 'Configuration',
            
            # API related
            'API Key': 'API Key',
            'API Token': 'API Token',
            'Generate': 'Generate',
            'Revoke': 'Revoke',
            'Validate': 'Validate',
            'Permissions': 'Permissions',
            'Rate Limiting': 'Rate Limiting',
            
            # LLM related
            'Model': 'Model',
            'Download': 'Download',
            'Status': 'Status',
            'Chat': 'Chat',
            'Response': 'Response',
            'Context': 'Context',
            
            # Design system
            'Components': 'Components',
            'UI Examples': 'UI Examples',
            'Design System': 'Design System',
            'Accessibility': 'Accessibility',
            'Performance': 'Performance',
        }
    
    def _compile_translation(self, po_file: Path, mo_file: Path):
        """Compile .po file to .mo file"""
        try:
            with open(po_file, 'r', encoding='utf-8') as f:
                catalog = read_po(f)
            
            with open(mo_file, 'wb') as f:
                write_mo(f, catalog)
            
            logger.info(f"Compiled translation: {po_file} -> {mo_file}")
            
        except Exception as e:
            logger.error(f"Error compiling translation: {e}")
    
    def get_current_language(self) -> str:
        """Get current language from session, cookie, or request"""
        # Check session first
        if session.get(self.config.language_session_key):
            lang = session[self.config.language_session_key]
            if lang in self.config.supported_languages:
                return lang
        
        # Check cookie
        if request.cookies.get(self.config.language_cookie_name):
            lang = request.cookies.get(self.config.language_cookie_name)
            if lang in self.config.supported_languages:
                return lang
        
        # Check Accept-Language header
        if self.config.language_detection_enabled:
            accept_lang = request.accept_languages.best_match(self.config.supported_languages)
            if accept_lang:
                return accept_lang
        
        # Return default language
        return self.config.default_language
    
    def set_language(self, lang_code: str) -> bool:
        """Set language for current session"""
        if lang_code in self.config.supported_languages:
            session[self.config.language_session_key] = lang_code
            return True
        return False
    
    def get_language_info(self, lang_code: str) -> Optional[LanguageInfo]:
        """Get language information"""
        return self.languages.get(lang_code)
    
    def get_supported_languages(self) -> List[LanguageInfo]:
        """Get list of supported languages"""
        return [self.languages[code] for code in self.config.supported_languages if code in self.languages]
    
    def translate(self, text: str, lang_code: str = None) -> str:
        """Translate text to specified language"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        # Check if language is supported
        if lang_code not in self.config.supported_languages:
            lang_code = self.config.fallback_language
        
        # If it's the default language (Serbian), return as is
        if lang_code == self.config.default_language:
            return text
        
        # Try to get translation
        try:
            if lang_code in self._gettext_translations:
                translation = self._gettext_translations[lang_code].gettext(text)
                if translation != text:
                    return translation
            
            # If no translation found and fallback mode is enabled
            if self.config.translation_fallback_mode and lang_code != self.config.fallback_language:
                return self.translate(text, self.config.fallback_language)
            
            # Log missing translation if enabled
            if self.config.translation_missing_log:
                logger.warning(f"Missing translation for '{text}' in language '{lang_code}'")
            
            return text
            
        except Exception as e:
            logger.error(f"Error translating '{text}' to '{lang_code}': {e}")
            return text
    
    def ntranslate(self, singular: str, plural: str, count: int, lang_code: str = None) -> str:
        """Translate text with plural forms"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        # Check if language is supported
        if lang_code not in self.config.supported_languages:
            lang_code = self.config.fallback_language
        
        # If it's the default language (Serbian), return as is
        if lang_code == self.config.default_language:
            return singular if count == 1 else plural
        
        # Try to get translation
        try:
            if lang_code in self._gettext_translations:
                translation = self._gettext_translations[lang_code].ngettext(singular, plural, count)
                if translation != singular and translation != plural:
                    return translation
            
            # If no translation found and fallback mode is enabled
            if self.config.translation_fallback_mode and lang_code != self.config.fallback_language:
                return self.ntranslate(singular, plural, count, self.config.fallback_language)
            
            # Return appropriate form based on count
            return singular if count == 1 else plural
            
        except Exception as e:
            logger.error(f"Error translating plural '{singular}'/'{plural}' to '{lang_code}': {e}")
            return singular if count == 1 else plural
    
    def format_number(self, number: float, lang_code: str = None) -> str:
        """Format number according to language locale"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        try:
            locale = Locale.parse(lang_code)
            return locale.number_symbols['decimal'].join([
                f"{int(number):,}".replace(',', locale.number_symbols['group']),
                f"{number % 1:.2f}"[2:] if number % 1 != 0 else ''
            ])
        except (UnknownLocaleError, KeyError):
            # Fallback to default formatting
            return f"{number:,.2f}"
    
    def format_currency(self, amount: float, currency: str = None, lang_code: str = None) -> str:
        """Format currency according to language locale"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        if not currency:
            currency = config.serbian_business.default_currency
        
        try:
            locale = Locale.parse(lang_code)
            return locale.currency_formats['standard'].format(
                amount,
                currency,
                locale.number_symbols
            )
        except (UnknownLocaleError, KeyError):
            # Fallback to default formatting
            return f"{amount:,.2f} {currency}"
    
    def format_date(self, date, lang_code: str = None, format_type: str = 'medium') -> str:
        """Format date according to language locale"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        try:
            locale = Locale.parse(lang_code)
            return date.strftime(locale.date_formats[format_type])
        except (UnknownLocaleError, KeyError):
            # Fallback to default formatting
            return date.strftime('%Y-%m-%d')
    
    def is_rtl(self, lang_code: str = None) -> bool:
        """Check if language is right-to-left"""
        if not lang_code:
            lang_code = self.get_current_language()
        
        lang_info = self.get_language_info(lang_code)
        return lang_info.rtl if lang_info else False

# Global localization manager instance
localization_manager = LocalizationManager()

def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance"""
    return localization_manager

def gettext(text: str) -> str:
    """Get translated text"""
    return localization_manager.translate(text)

def ngettext(singular: str, plural: str, count: int) -> str:
    """Get translated text with plural forms"""
    return localization_manager.ntranslate(singular, plural, count)

def format_number(number: float) -> str:
    """Format number according to current language"""
    return localization_manager.format_number(number)

def format_currency(amount: float, currency: str = None) -> str:
    """Format currency according to current language"""
    return localization_manager.format_currency(amount, currency)

def format_date(date, format_type: str = 'medium') -> str:
    """Format date according to current language"""
    return localization_manager.format_date(date, format_type=format_type)

def is_rtl() -> bool:
    """Check if current language is right-to-left"""
    return localization_manager.is_rtl()

def require_language(f):
    """Decorator to set up language context"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Set current language in Flask g
        g.current_language = localization_manager.get_current_language()
        g.language_info = localization_manager.get_language_info(g.current_language)
        g.is_rtl = localization_manager.is_rtl()
        
        return f(*args, **kwargs)
    
    return decorated_function

def get_language_from_request() -> str:
    """Get language from request parameters"""
    return request.args.get('lang') or request.form.get('lang') or localization_manager.get_current_language()
