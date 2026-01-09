"""Test compare endpoint with detailed error."""
import sys
sys.path.insert(0, '.')

from routers.compare import compare_institutions
from fastapi import Query
from unittest.mock import MagicMock

try:
    # Create fake query
    batch_ids = "batch_aicte_20260109_165539_eb6b4d3f,batch_aicte_20260109_161540_073bbce7"
    
    # Call the function directly
    result = compare_institutions(batch_ids=batch_ids, user=None)
    print(f"SUCCESS: {result}")
except Exception as e:
    import traceback
    print(f"ERROR: {e}")
    traceback.print_exc()
