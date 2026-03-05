from abc import ABC, abstractmethod
from typing import Any, Type, Dict

# Import model and viewmodel types lazily to avoid circular deps

class ViewModelCreator(ABC):
    """Creator declares the factory method which returns a ViewModel for a Model."""

    @abstractmethod
    def factory_method(self, model: Any):
        raise NotImplementedError

    def build(self, model: Any):
        """Template method that subclasses can keep or override"""
        return self.factory_method(model)


# Concrete creator ------------------------------------------------------------

class DefaultViewModelCreator(ViewModelCreator):
    """Chooses a matching ViewModel class based on a registry (slug-to-class map)."""

    _registry: Dict[Type, Type] = {}

    @classmethod
    def register(cls, model_cls: Type, vm_cls: Type) -> None:
        cls._registry[model_cls] = vm_cls

    def factory_method(self, model: Any):  # type: ignore[override]
        vm_cls = self._registry.get(type(model))
        if vm_cls is None:
            raise ValueError(f"No ViewModel registered for {type(model)}")
        return vm_cls.from_model(model)  # type: ignore[attr-defined]


# Registry --------------------------------------------------------------------

from src.models.example_page import ExamplePage
from src.viewmodels.example_page_viewmodel import ExamplePageViewModel

# Register ExamplePage → ExamplePageViewModel mapping at import time
DefaultViewModelCreator.register(ExamplePage, ExamplePageViewModel)

# Convenience singleton instance
viewmodel_factory = DefaultViewModelCreator()
