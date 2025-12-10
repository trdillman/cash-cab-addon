"""
Base classes and interfaces for route services

Provides common patterns for service implementation including
result types, error handling, and service interfaces.
"""

from dataclasses import dataclass
from typing import Generic, TypeVar, Optional
from abc import ABC, abstractmethod


# Type variable for generic result types
T = TypeVar('T')


class ServiceError(Exception):
    """Base exception for service layer errors"""

    def __init__(self, message: str, details: Optional[dict] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def __str__(self):
        if self.details:
            return f"{self.message} (details: {self.details})"
        return self.message


@dataclass
class ServiceResult(Generic[T]):
    """
    Generic result wrapper for service operations

    Provides consistent interface for success/failure handling
    without using exceptions for control flow.

    Usage:
        result = service.do_something()
        if result.success:
            data = result.data
        else:
            error = result.error
    """

    success: bool
    data: Optional[T] = None
    error: Optional[str] = None
    details: Optional[dict] = None

    @classmethod
    def ok(cls, data: T) -> 'ServiceResult[T]':
        """Create a successful result"""
        return cls(success=True, data=data, error=None)

    @classmethod
    def fail(cls, error: str, details: Optional[dict] = None) -> 'ServiceResult[T]':
        """Create a failed result"""
        return cls(success=False, data=None, error=error, details=details)

    def __bool__(self):
        """Allow using result in boolean context"""
        return self.success


class IService(ABC):
    """
    Base interface for all services

    Provides common service lifecycle methods and configuration access.
    """

    @abstractmethod
    def validate(self) -> bool:
        """
        Validate service configuration and dependencies

        Returns:
            bool: True if service is properly configured
        """
        pass


class ILogger(ABC):
    """
    Logging interface for services

    Allows dependency injection of different logging implementations.
    """

    @abstractmethod
    def info(self, message: str):
        """Log informational message"""
        pass

    @abstractmethod
    def warning(self, message: str):
        """Log warning message"""
        pass

    @abstractmethod
    def error(self, message: str):
        """Log error message"""
        pass


class ConsoleLogger(ILogger):
    """Simple console logger implementation"""

    def __init__(self, prefix: str = "[BLOSM]"):
        self.prefix = prefix

    def info(self, message: str):
        print(f"{self.prefix} INFO: {message}")

    def warning(self, message: str):
        print(f"{self.prefix} WARN: {message}")

    def error(self, message: str):
        print(f"{self.prefix} ERROR: {message}")


class NullLogger(ILogger):
    """No-op logger for testing or when logging is disabled"""

    def info(self, message: str):
        pass

    def warning(self, message: str):
        pass

    def error(self, message: str):
        pass


__all__ = [
    'ServiceError',
    'ServiceResult',
    'IService',
    'ILogger',
    'ConsoleLogger',
    'NullLogger',
]
