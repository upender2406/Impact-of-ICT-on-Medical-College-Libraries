"""Helper utility functions."""

from typing import List, Dict, Any
import numpy as np


def calculate_infrastructure_score(infrastructure: Dict[str, Any]) -> float:
    """Calculate overall infrastructure score."""
    return (
        infrastructure.get('hardware_quality', 0) +
        infrastructure.get('software_availability', 0) +
        infrastructure.get('internet_speed', 0) +
        infrastructure.get('digital_collection', 0)
    ) / 4


def calculate_barrier_score(barriers: Dict[str, Any]) -> float:
    """Calculate overall barrier score."""
    return (
        barriers.get('financial_barrier', 0) +
        barriers.get('technical_barrier', 0) +
        barriers.get('training_barrier', 0) +
        barriers.get('policy_barrier', 0)
    ) / 4


def get_satisfaction_category(score: float) -> str:
    """Categorize satisfaction score."""
    if score <= 4:
        return 'Low'
    elif score <= 7:
        return 'Medium'
    else:
        return 'High'
