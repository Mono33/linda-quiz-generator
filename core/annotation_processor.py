"""Annotation processing functionality."""

import pandas as pd
from typing import List, Dict


class AnnotationProcessor:
    """Class to process annotation data from CSV files."""

    @staticmethod
    def load_annotations(file_path: str) -> pd.DataFrame:
        """
        Load annotations from a CSV file.

        Args:
            file_path: Path to the CSV file containing annotations

        Returns:
            DataFrame containing the annotations
        """
        return pd.read_csv(file_path)

    @staticmethod
    def group_annotations_by_tag(annotations: pd.DataFrame) -> Dict[str, List[str]]:
        """
        Group annotation text by their tag categories.

        Args:
            annotations: DataFrame containing the annotations

        Returns:
            Dictionary with tag categories as keys and lists of text snippets as values
        """
        grouped = {}
        for _, row in annotations.iterrows():
            tag = row["title"]
            text = row["text"]
            if tag not in grouped:
                grouped[tag] = []
            grouped[tag].append(text)
        return grouped


