"""Compatibility name for Sova's semantic resolution pass."""

from .semantic_analyzer import SemanticAnalyzer, SemanticReport

Resolver = SemanticAnalyzer

__all__ = ["Resolver", "SemanticAnalyzer", "SemanticReport"]
