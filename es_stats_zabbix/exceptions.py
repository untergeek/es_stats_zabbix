"""
Exception module
"""

class ESZException(Exception):
    """
    Base class for all exceptions raised by es_stats_zabbix which are not Elasticsearch
    exceptions.
    """

class ConfigurationError(ESZException):
    """
    Exception raised when a misconfiguration is detected
    """

class MissingArgument(ESZException):
    """
    Exception raised when a needed argument is not passed.
    """

class NotFound(ESZException):
    """
    Exception raised when expected information is not found.
    """

class FailedExecution(ESZException):
    """
    Exception raised when a function fails to execute for some reason.
    """

class EmptyResult(ESZException):
    """
    Exception raised when there is no result at all.
    """
