"""
Fortigate Integration Module
"""

from .fortigate_api import FortiManagerAPI, FortiGateDirectAPI, build_fortigate_topology_data

__all__ = ['FortiManagerAPI', 'FortiGateDirectAPI', 'build_fortigate_topology_data']
