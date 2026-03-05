import pytest

from src.models.example_page import ExamplePage
from src.factories.viewmodel_factory import viewmodel_factory, DefaultViewModelCreator


def test_factory_returns_viewmodel(app_context):  # app_context fixture from conftest
    ExamplePage.seed_demo()
    page = ExamplePage.query.first()
    vm = viewmodel_factory.build(page)
    assert vm.slug == page.slug


def test_factory_missing_mapping():
    class Dummy:  # model with no mapping
        pass

    with pytest.raises(ValueError):
        DefaultViewModelCreator().build(Dummy())
