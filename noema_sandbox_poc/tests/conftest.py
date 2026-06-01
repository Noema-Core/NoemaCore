import sys
import os
# Dodaj root projektu do PYTHONPATH, żeby testy widziały moduł 'sandbox'
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
