"""KB loader: reads JSON files and matches symptoms to conditions / red flags."""

import json
from pathlib import Path
from typing import List, Dict, Any

BASE_PATH = Path(__file__).parent / "data"


class KnowledgeBase:
    def __init__(self):
        self.conditions = self._load_json("conditions.json").get("conditions", [])
        self.red_flags = self._load_json("red_flags.json").get("red_flags", [])
        self.triage_rules = self._load_json("triage_rules.json")

    @staticmethod
    def _load_json(filename: str) -> dict:
        try:
            with open(BASE_PATH / filename) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            return {}

    def get_relevant_conditions(self, symptoms: str) -> List[Dict[str, Any]]:
        """Find conditions matching the symptom keywords."""
        symptoms_lower = symptoms.lower()
        matched = []

        for condition in self.conditions:
            score = sum(
                symptoms_lower.count(sym.lower())
                for sym in condition.get("symptoms", [])
            )
            if score > 0:
                matched.append((condition, score))

        matched.sort(key=lambda x: x[1], reverse=True)
        return [c[0] for c in matched[:10]]

    def check_red_flags(self, symptoms: str) -> List[Dict[str, Any]]:
        """Check symptoms against red flag patterns."""
        symptoms_lower = symptoms.lower()
        detected_flags = []

        for flag in self.red_flags:
            keywords_match = any(
                kw.lower() in symptoms_lower for kw in flag.get("keywords", [])
            )
            if keywords_match:
                detected_flags.append(flag)

        return detected_flags

    def get_triage_level(self, symptoms: str) -> str:
        """Quick triage based on symptom keywords."""
        symptoms_lower = symptoms.lower()
        triage_rules = self.triage_rules.get("triage_criteria", {})

        red_keywords = self.triage_rules.get("triage_keywords", {}).get("red_keywords", [])
        yellow_keywords = self.triage_rules.get("triage_keywords", {}).get("yellow_keywords", [])

        red_count = sum(1 for kw in red_keywords if kw.lower() in symptoms_lower)
        yellow_count = sum(1 for kw in yellow_keywords if kw.lower() in symptoms_lower)

        if red_count > 0:
            return "RED"
        elif yellow_count > 0:
            return "YELLOW"
        else:
            return "GREEN"


kb = KnowledgeBase()
