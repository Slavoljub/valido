from dataclasses import asdict, dataclass
from typing import Dict, Any

from src.models.example_page import ExamplePage

@dataclass
class ExamplePageViewModel:
    """Thin adapter exposing ExamplePage in a template-friendly structure."""

    slug: str
    title: str
    description: str
    created_at: str

    @classmethod
    def from_model(cls, model: ExamplePage) -> 'ExamplePageViewModel':
        return cls(
            slug=model.slug,
            title=model.title,
            description=model.description or '',
            created_at=model.created_at.isoformat() if model.created_at else ''
        )

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
