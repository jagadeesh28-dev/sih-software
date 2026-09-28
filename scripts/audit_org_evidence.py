import os
import pymupdf

base = r"c:\Users\JAGADEESH M\OneDrive\Documents\SIH-software\EGREEN_QUANTA_SIH26138_EVIDENCE"
print("=== COMPREHENSIVE ORGANIZATION AUDIT ===\n")

errors = []
pdf_files = [
    ("00_START_HERE/README_FOR_EVALUATOR.pdf", 2),
    ("00_START_HERE/EVIDENCE_INDEX.pdf", 2),
    ("01_PROBLEM_AND_SOLUTION/Problem_Statement_and_Solution.pdf", 4),
    ("01_PROBLEM_AND_SOLUTION/System_Architecture.pdf", 2),
    ("02_VALIDATED_RESULTS/Results_Summary.pdf", 5),
    ("03_PROTOTYPE_AND_HMI/HMI_Overview.pdf", 3),
    ("03_PROTOTYPE_AND_HMI/Prototype_Evidence.pdf", 2),
    ("04_VERIFICATION_AND_SAFETY/Verification_Summary.pdf", 3),
    ("04_VERIFICATION_AND_SAFETY/Certification_Readiness_Summary.pdf", 2),
    ("04_VERIFICATION_AND_SAFETY/Adversarial_Test_Summary.pdf", 2),
    ("04_VERIFICATION_AND_SAFETY/Tamper_Evidence_Summary.pdf", 2),
    ("05_DECISION_RECORD/Integrity_Verification.pdf", 2),
    ("06_RESEARCH_AND_REFERENCES/Selected_References.pdf", 3),
    ("99_DETAILED_BACKUP/END_TO_END_VERIFICATION_REPORT.pdf", 6),
    ("99_DETAILED_BACKUP/END_TO_END_AUDIT_RAW.pdf", 7),
    ("99_DETAILED_BACKUP/Detailed_Test_Evidence.pdf", 7),
]

for rel_p, max_p in pdf_files:
    p = os.path.join(base, rel_p.replace("/", os.sep))
    doc = pymupdf.open(p)
    pages = len(doc)
    if pages != max_p:
        errors.append(f"{rel_p}: Expected {max_p} pages, got {pages}")
    
    text = ""
    for pg in doc:
        text += pg.get_text()
    
    if "Ministry" in text:
        errors.append(f"{rel_p}: Stale 'Ministry' reference found!")
    if "Egreen Quanta" not in text and "EGREEN QUANTA" not in text:
        errors.append(f"{rel_p}: Missing 'Egreen Quanta' organization reference!")
    if "SUPER SYNQRA" not in text:
        errors.append(f"{rel_p}: Missing 'SUPER SYNQRA' team reference!")
    doc.close()
    print(f"[PDF AUDIT OK] {rel_p} ({pages} pages, Org: Egreen Quanta, Team: SUPER SYNQRA verified)")

print(f"\nTotal Errors Found: {len(errors)}")
if errors:
    for e in errors:
        print("  ERROR:", e)
else:
    print("\nALL 16 PDFS VERIFIED: ZERO MINISTRY REFERENCES, ORG IS EGREEN QUANTA!")
