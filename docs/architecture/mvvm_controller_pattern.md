# MVVM Controller & Thin-Adapter Pattern in ValidoAI

> Status: Draft ‑ initial guidance for contributors

## Purpose
This document explains **how ValidoAI implements a clean Model-View-ViewModel (MVVM) flow** on top of Flask while still retaining a single, central `routes.py` file for route declaration.

The goals are:
1. Keep all HTTP routes visible in one place (discoverability).
2. Maintain a clear separation of concerns:
   * **Model** – data & business rules (SQLAlchemy models).
   * **ViewModel (Thin Adapter)** – shape Models into template-friendly objects; no business logic.
   * **Controller / Service** – coordinate retrieval, manipulation and ViewModel creation.
3. Make every layer **unit-testable** and **type-safe**.

## How It Works
```mermaid
graph TD;
  route[/routes.py\n@main_bp.route('/examples/<slug>')/] --> controller[ExampleController.show()]
  controller --> model[ExamplePage (SQLAlchemy)]
  model --> viewmodel[ExamplePageViewModel]
  viewmodel --> template[example-pages/slug.html]
```

1. `routes.py` imports the desired controller and delegates the request.
2. The **Controller** fetches/updates the **Model** and instantiates a **ViewModel** (thin adapter).
3. The Jinja **template** consumes only the ViewModel, keeping logic out of templates.

### Why Not Blueprints per Controller?
Centralised routes support quick auditing and avoid hidden endpoints. Controllers stay framework-agnostic; only `routes.py` has Flask specifics.

## Singleton-Style Access to Services
For shared resources (e.g., DB session, cache, email client) use the **application wide service container** already provided by Flask’s `current_app` context:
```python
from flask import current_app

def get_cache_service():
    if not hasattr(current_app, 'cache_service'):
        current_app.cache_service = CacheService()
    return current_app.cache_service
```

*This lazy-initialised accessor is effectively a Singleton tied to the Flask app instance, keeping global state predictable in tests.*

## Best-Practice Checklist
- [x] **Models** have zero presentation code.
- [x] **ViewModels** are `@dataclass`-es exposing only serialisable fields.
- [x] **Controllers** never import `render_template` outside their own file.
- [x] Unit tests cover Controller ↔ Model logic & ViewModel transforms.
- [x] Services obtained via `current_app` helper functions (singleton pattern).

## Further Reading
* Clean Architecture – R. Martin
* MVVM in Web Apps – patterns.dev
