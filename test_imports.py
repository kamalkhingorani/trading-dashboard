import os
import sys

print("Current directory:", os.getcwd())
print("Files in current directory:")
for file in os.listdir('.'):
    if file.endswith('.py'):
        print(f"  - {file}")

print("\nPython path:")
for path in sys.path:
    print(f"  - {path}")

print("\nTrying to import modules...")
try:
    import indian_stock_logic
    print("✓ indian_stock_logic imported successfully")
except Exception as e:
    print(f"✗ Error importing indian_stock_logic: {e}")

try:
    import us_stock_logic
    print("✓ us_stock_logic imported successfully")
except Exception as e:
    print(f"✗ Error importing us_stock_logic: {e}")

try:
    import news_logic
    print("✓ news_logic imported successfully")
except Exception as e:
    print(f"✗ Error importing news_logic: {e}")

try:
    import fixed_fno_options_logic
    print("✓ fixed_fno_options_logic imported successfully")
except Exception as e:
    print(f"✗ Error importing fixed_fno_options_logic: {e}")
