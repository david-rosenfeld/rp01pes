#!/usr/bin/env python3
"""Reference outputs for task_04_refactor validation."""

# These are the expected outputs that refactored code must match exactly

SALES_TEST_DATA = [
    {'product': 'Widget', 'amount': 25.00},
    {'product': 'Gadget', 'amount': 49.99},
]

INVENTORY_TEST_DATA = [
    {'name': 'Widget', 'quantity': 100},
    {'name': 'Gadget', 'quantity': 50},
]

EXPECTED_SALES_OUTPUT = """==================================================
SALES REPORT
==================================================

  Widget: $25.00
  Gadget: $49.99

--------------------------------------------------
  TOTAL: $74.99
=================================================="""

EXPECTED_INVENTORY_OUTPUT = """==================================================
INVENTORY REPORT
==================================================

  Widget: 100 units
  Gadget: 50 units

--------------------------------------------------
  TOTAL ITEMS: 150
=================================================="""
