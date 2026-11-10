"""Исключения приложения."""


class AppError(Exception):
    """Базовая ошибка приложения."""


class ConfigError(AppError):
    """Некорректные параметры командной строки."""

class RepoError(AppError):
    """Ошибка чтения или разбора репозитория."""

class RenderError(AppError):
    """Ошибка построения изображения."""