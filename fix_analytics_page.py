"""
FINAL FIX: Remove ALL old production code by finding ChatWidget
"""

# Read file
with open('c:/dev/ai-command-center/frontend/app/analytics/page.tsx', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Strategy: Find production section, then find ChatWidget, remove everything in between

production_end = None  # The )} after <ProductionInsights />
chatwidget_line = None

for i, line in enumerate(lines):
    # Find where ProductionInsights component ends
    if '<ProductionInsights />' in line:
        # Look for the closing )}
        for j in range(i, min(i+5, len(lines))):
            if lines[j].strip() == ')}':
                production_end = j
                print(f"Production component ends at line {j}")
                break
    
    # Find ChatWidget
    if '<ChatWidget' in line or 'ChatWidget />' in line:
        chatwidget_line = i
        print(f"ChatWidget found at line {i}")
        break

if production_end and chatwidget_line:
    print(f"\nWill remove lines {production_end+1} to {chatwidget_line-1}")
    print(f"That's {chatwidget_line - production_end - 1} lines")
    
    # Build new file
    new_lines = []
    new_lines.extend(lines[:production_end+1])  # Keep up to )}
    new_lines.append('\n')
    new_lines.extend(lines[chatwidget_line:])  # Add from ChatWidget onwards
    
    # Write
    with open('c:/dev/ai-command-center/frontend/app/analytics/page.tsx', 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"\n✅ SUCCESS!")
    print(f"Removed {chatwidget_line - production_end - 1} lines")
    print(f"File: {len(lines)} → {len(new_lines)} lines")
else:
    print(f"\n❌ FAILED")
    print(f"production_end: {production_end}")
    print(f"chatwidget_line: {chatwidget_line}")
    
    if production_end:
        print(f"\nShowing 30 lines after production_end ({production_end}):")
        for i in range(production_end+1, min(production_end+31, len(lines))):
            print(f"{i}: {lines[i].rstrip()[:80]}")
