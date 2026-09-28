import os

scripts = [
    'scripts/build_evaluator_part1.py',
    'scripts/build_evaluator_part2.py',
    'scripts/build_evaluator_part3.py',
    'scripts/build_evaluator_part4.py',
    'scripts/build_evaluator_package.py'
]

old_org = "<div>Ministry of Ports, Shipping & Waterways</div>"
new_org = "<div>Organization: Egreen Quanta</div>"

for s in scripts:
    if os.path.exists(s):
        with open(s, 'r', encoding='utf-8') as f:
            c = f.read()
        
        count = c.count(old_org)
        c = c.replace(old_org, new_org)
        # Also catch any variations with &amp;
        c = c.replace("<div>Ministry of Ports, Shipping &amp; Waterways</div>", new_org)
        c = c.replace("Ministry of Ports, Shipping & Waterways", "Organization: Egreen Quanta")
        c = c.replace("Ministry of Ports, Shipping &amp; Waterways", "Organization: Egreen Quanta")
        
        with open(s, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f"Updated organization in {s} ({count} replacements)")

print("Organization name update completed.")
