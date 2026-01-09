"""
Config for pytest for Flask stub tests and combined tests from all supported stubs.
"""

try:
    from kafka.tests.conftest_kafka import *
except ImportError:
    pass
