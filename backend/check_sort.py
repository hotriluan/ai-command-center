
try:
    print(f"Sorting [None, None]: {sorted([None, None])}")
except Exception as e:
    print(f"Sorting [None, None] failed: {e}")

try:
    print(f"Sorting [None, 1]: {sorted([None, 1])}")
except Exception as e:
    print(f"Sorting [None, 1] failed: {e}")
