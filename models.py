"""
Shared data shapes for the pipeline.

Week 1: a simple dataclass
"""

from dataclasses import dataclass


@dataclass
class Paper:
    """represents one pubmed article after fetching details."""

    pubmed_id: str
    title: str
    journal: str
    year: str
    abstract: str
    authors: list[str] | None = None
