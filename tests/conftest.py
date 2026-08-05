"""Pytest configuration — adds src/ to the import path."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
