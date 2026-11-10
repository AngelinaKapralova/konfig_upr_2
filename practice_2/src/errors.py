"""Исключения приложения."""


class AppError(Exception):
    """Базовая ошибка приложения."""


class ConfigError(AppError):
    """Некорректные параметры командной строки."""

