import os

scripts = [
    'scripts/build_evaluator_part1.py',
    'scripts/build_evaluator_part2.py',
    'scripts/build_evaluator_part3.py',
    'scripts/build_evaluator_part4.py',
    'scripts/build_evaluator_package.py'
]

for s in scripts:
    if os.path.exists(s):
        with open(s, 'r', encoding='utf-8') as f:
            c = f.read()
        
        c = c.replace(
            'Smart India Hackathon 2026 &bull; Problem Statement SIH26138',
            'Smart India Hackathon 2026 &bull; SIH26138 &bull; Team SUPER SYNQRA'
        )
        c = c.replace(
            '<div>SIH26138 &bull; EGREEN QUANTA Evidence Repository</div>',
            '<div>SIH26138 &bull; Team SUPER SYNQRA &bull; EGREEN QUANTA</div>'
        )
        c = c.replace(
            '<div class="org">Smart India Hackathon 2026 &bull; SIH26138</div>',
            '<div class="org">Smart India Hackathon 2026 &bull; SIH26138 &bull; Team SUPER SYNQRA</div>'
        )
        
        with open(s, 'w', encoding='utf-8') as f:
            f.write(c)
        print(f'Updated team name in {s}')

# Also update Results_Data.csv
csv_path = r'c:\Users\JAGADEESH M\OneDrive\Documents\SIH-software\EGREEN_QUANTA_SIH26138_EVIDENCE\02_VALIDATED_RESULTS\Results_Data.csv'
if os.path.exists(csv_path):
    with open(csv_path, 'r', encoding='utf-8') as f:
        csv_text = f.read()
    if 'Team: SUPER SYNQRA' not in csv_text:
        csv_text = csv_text.replace(
            '# EGREEN QUANTA',
            '# EGREEN QUANTA (Team: SUPER SYNQRA)'
        )
        with open(csv_path, 'w', encoding='utf-8') as f:
            f.write(csv_text)
        print('Updated Results_Data.csv with Team: SUPER SYNQRA')

print('Team name updates completed.')
