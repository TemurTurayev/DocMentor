"""
Patient Loader - Loads virtual patient cases from JSON files.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class PatientLoader:
    """
    Loads and manages virtual patient cases.

    Supports:
    - Loading from JSON files
    - Filtering by specialty, difficulty
    - Random case selection
    """

    def __init__(self, cases_dir: str = None):
        """
        Initialize patient loader.

        Args:
            cases_dir: Directory containing patient JSON files
        """
        if cases_dir:
            self.cases_dir = Path(cases_dir)
        else:
            # Default: core/modules/virtual_patient/examples
            self.cases_dir = Path(__file__).parent.parent / "modules" / "virtual_patient" / "examples"

        self.cases_cache = {}
        logger.info(f"PatientLoader initialized with dir: {self.cases_dir}")

    def load_case(self, case_id: str) -> Optional[Dict]:
        """
        Load a specific case by ID.

        Args:
            case_id: Case identifier (filename without .json)

        Returns:
            Patient data dict or None if not found
        """
        # Check cache first
        if case_id in self.cases_cache:
            logger.debug(f"Loaded case from cache: {case_id}")
            return self.cases_cache[case_id]

        # Try to load from file
        case_file = self.cases_dir / f"{case_id}.json"

        if not case_file.exists():
            logger.warning(f"Case file not found: {case_file}")
            return None

        try:
            with open(case_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Cache it
            self.cases_cache[case_id] = data
            logger.info(f"Loaded case: {case_id}")

            return data

        except Exception as e:
            logger.error(f"Error loading case {case_id}: {str(e)}")
            return None

    def list_all_cases(self) -> List[Dict]:
        """
        List all available cases.

        Returns:
            List of case summaries
        """
        if not self.cases_dir.exists():
            logger.warning(f"Cases directory not found: {self.cases_dir}")
            return []

        cases = []

        for case_file in self.cases_dir.glob("*.json"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                # Extract summary
                summary = {
                    "id": case_file.stem,
                    "name": data.get("name", "Unknown"),
                    "age": data.get("age"),
                    "gender": data.get("gender"),
                    "chief_complaint": data.get("chief_complaint", []),
                    "specialty": data.get("specialty", "general"),
                    "difficulty": data.get("difficulty", 3),
                    "diagnosis": data.get("diagnoses", [{}])[0].get("name", "Unknown") if data.get("diagnoses") else "Unknown"
                }

                cases.append(summary)

            except Exception as e:
                logger.error(f"Error reading case {case_file}: {str(e)}")
                continue

        logger.info(f"Found {len(cases)} cases")
        return cases

    def filter_cases(
        self,
        specialty: Optional[str] = None,
        difficulty: Optional[int] = None,
        min_difficulty: Optional[int] = None,
        max_difficulty: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter cases by criteria.

        Args:
            specialty: Filter by specialty (pediatrics, therapy, surgery, etc.)
            difficulty: Exact difficulty level (1-5)
            min_difficulty: Minimum difficulty
            max_difficulty: Maximum difficulty

        Returns:
            Filtered list of case summaries
        """
        all_cases = self.list_all_cases()

        filtered = all_cases

        if specialty:
            filtered = [c for c in filtered if c.get("specialty", "").lower() == specialty.lower()]

        if difficulty is not None:
            filtered = [c for c in filtered if c.get("difficulty") == difficulty]

        if min_difficulty is not None:
            filtered = [c for c in filtered if c.get("difficulty", 0) >= min_difficulty]

        if max_difficulty is not None:
            filtered = [c for c in filtered if c.get("difficulty", 5) <= max_difficulty]

        logger.info(f"Filtered to {len(filtered)} cases")
        return filtered

    def get_random_case(
        self,
        specialty: Optional[str] = None,
        difficulty: Optional[int] = None
    ) -> Optional[Dict]:
        """
        Get a random case matching criteria.

        Args:
            specialty: Filter by specialty
            difficulty: Filter by difficulty

        Returns:
            Full patient data or None
        """
        import random

        filtered = self.filter_cases(specialty=specialty, difficulty=difficulty)

        if not filtered:
            logger.warning("No cases match criteria")
            return None

        # Pick random
        chosen = random.choice(filtered)
        case_id = chosen["id"]

        # Load full data
        return self.load_case(case_id)

    def create_case_from_dict(self, case_data: Dict) -> Dict:
        """
        Validate and normalize case data from dict.

        Ensures all required fields are present.
        """
        required_fields = ["name", "age", "gender", "chief_complaint"]

        for field in required_fields:
            if field not in case_data:
                raise ValueError(f"Missing required field: {field}")

        # Set defaults
        defaults = {
            "patient_id": "CUSTOM",
            "specialty": "general",
            "difficulty": 3,
            "symptoms": [],
            "medical_history": "",
            "social_history": {},
            "allergies": [],
            "vitals": {},
            "physical_exam": {},
            "lab_results": {},
            "imaging": {},
            "diagnoses": [],
            "recommended_tests": [],
            "treatment": {},
            "expert_reasoning": {}
        }

        # Merge with defaults
        normalized = {**defaults, **case_data}

        return normalized

    def save_case(self, case_id: str, case_data: Dict) -> bool:
        """
        Save case to JSON file.

        Args:
            case_id: Case identifier
            case_data: Patient data dict

        Returns:
            True if successful
        """
        try:
            # Ensure directory exists
            self.cases_dir.mkdir(parents=True, exist_ok=True)

            case_file = self.cases_dir / f"{case_id}.json"

            with open(case_file, 'w', encoding='utf-8') as f:
                json.dump(case_data, f, ensure_ascii=False, indent=2)

            # Update cache
            self.cases_cache[case_id] = case_data

            logger.info(f"Case saved: {case_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving case {case_id}: {str(e)}")
            return False

    def __repr__(self):
        return f"PatientLoader(cases_dir={self.cases_dir}, cached={len(self.cases_cache)})"
