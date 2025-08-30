# AI Prescription Verifier — Plain Python (no external libraries)
# Works in Programiz / any basic Python runner

import re

# --- Fake drug DB for demo (expandable) ---
# Map: drug -> {dosage_child, dosage_adult, alternative}
DRUG_DB = {
    "Aspirin": {
        "dosage_child": "Not recommended",
        "dosage_adult": "75–325 mg/day",
        "alternative": "Clopidogrel",
    },
    "Paracetamol": {
        "dosage_child": "10–15 mg/kg every 4–6h",
        "dosage_adult": "500 mg every 6h",
        "alternative": "Acetaminophen",
    },
    "Ibuprofen": {
        "dosage_child": "5–10 mg/kg every 6–8h",
        "dosage_adult": "200–400 mg every 6h",
        "alternative": "Naproxen",
    },
}

# --- Example interaction rules ---
# Use frozenset for order-independent pair lookup
INTERACTIONS = {
    frozenset(["Aspirin", "Ibuprofen"]): "↑ GI bleeding risk",
    frozenset(["Paracetamol", "Alcohol"]): "↑ Liver toxicity risk",
}

def extract_drugs(text, include_alcohol=False):
    """Return a deduplicated list of drugs found in text (case-insensitive, word-boundary matching)."""
    found = []
    for drug in DRUG_DB.keys():
        if re.search(rf"\b{re.escape(drug)}\b", text, flags=re.IGNORECASE):
            found.append(drug)
    if include_alcohol:
        found.append("Alcohol")
    # Deduplicate while preserving order
    seen = set()
    unique = []
    for d in found:
        if d not in seen:
            unique.append(d)
            seen.add(d)
    return unique

def find_interactions(drugs):
    """Return list of human-readable interaction strings among detected drugs."""
    results = []
    n = len(drugs)
    for i in range(n):
        for j in range(i + 1, n):
            pair = frozenset([drugs[i], drugs[j]])
            if pair in INTERACTIONS:
                results.append(f"{drugs[i]} + {drugs[j]} → {INTERACTIONS[pair]}")
    return results

def dosage_suggestions(drugs, age):
    """Return dict: drug -> suggested dosage string based on age."""
    cat = "dosage_child" if age < 18 else "dosage_adult"
    out = {}
    for d in drugs:
        if d in DRUG_DB:
            out[d] = DRUG_DB[d][cat]
    return out

def alternatives_for(drugs):
    """Return dict: drug -> alternative string (or 'No alternative')."""
    out = {}
    for d in drugs:
        if d in DRUG_DB:
            alt = DRUG_DB[d].get("alternative")
            out[d] = alt if alt else "No alternative"
    return out

def print_table(title, rows):
    print(f"\n=== {title} ===")
    if not rows:
        print("None")
        return
    if isinstance(rows, dict):
        width = max(len(k) for k in rows.keys()) if rows else 0
        for k, v in rows.items():
            print(f"{k:<{width}} : {v}")
    elif isinstance(rows, list):
        for r in rows:
            print(f"- {r}")
    else:
        print(rows)

def main():
    print("💊 AI Prescription Verifier (Demo) — Plain Python\n")

    # ---- Inputs ----
    prescription_text = input("Enter prescription text: ").strip()
    # Safe age input
    while True:
        age_str = input("Enter age (1–120): ").strip()
        if age_str.isdigit():
            age = int(age_str)
            if 1 <= age <= 120:
                break
        print("Please enter a valid number between 1 and 120.")
    alcohol_ans = input("Alcohol use? (y/n): ").strip().lower()
    alcohol_use = alcohol_ans.startswith("y")

    # ---- Processing ----
    drugs = extract_drugs(prescription_text, include_alcohol=alcohol_use)
    interactions = find_interactions(drugs)
    dosages = dosage_suggestions(drugs, age)
    alternatives = alternatives_for(drugs)

    # ---- Output ----
    print_table("Drugs Detected", drugs if drugs else ["❌ No drugs detected"])
    print_table("Potential Interactions", interactions if interactions else ["✅ No major interactions found"])
    print_table("Dosage Suggestions", dosages if dosages else {"Info": "No dosage information available"})
    print_table("Alternatives", alternatives if alternatives else {"Info": "No alternatives found"})

if __name__ == "__main__":
    main()
