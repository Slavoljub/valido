"""
SQL Patterns Repository
Reusable SQL query patterns and database design patterns
"""

from .factory import LLMModelFactory, InferenceStrategyFactory
from .observer import DatabaseObserver, EventManager, register_default_observers
from .repository import Repository, BaseRepository
from .singleton import Singleton, DatabaseConnection, ConfigurationManager, LoggerManager, CacheManager, ThreadManager
from .strategy import DatabaseStrategy, SQLiteStrategy, MySQLStrategy
from .command import DatabaseCommand, CommandInvoker
from .template import QueryTemplate, TemplateMethod

__all__ = [
    'LLMModelFactory',
    'InferenceStrategyFactory',
    'DatabaseObserver',
    'EventManager',
    'register_default_observers',
    'Repository',
    'BaseRepository',
    'Singleton',
    'DatabaseConnection',
    'ConfigurationManager',
    'LoggerManager',
    'CacheManager',
    'ThreadManager',
    'DatabaseStrategy',
    'SQLiteStrategy',
    'MySQLStrategy',
    'DatabaseCommand',
    'CommandInvoker',
    'QueryTemplate',
    'TemplateMethod'
]
