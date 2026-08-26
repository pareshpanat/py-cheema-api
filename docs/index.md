# py-cheema-api Documentation

`py-cheema-api` API docs and usage guide for GitHub Pages publishing from `/docs`.

## Start Here

- [Complete API Reference](api-reference.md)
- [Tutorial](tutorial.md)
- [Advanced](advanced.md)
- [Security Recipes](security-recipes.md)
- [Deployment](deployment.md)
- [Why py-cheema-api](why-py-cheema-api.md)

## Quick Install

```bash
pip install py-cheema-api
```

## Quick Example

```python
from cheema import Cheema

app = Cheema(title="Example API", version="1.0.0")

@app.get("/ping")
async def ping():
    return {"ok": True}
```

## Built-in Docs Endpoints

- OpenAPI JSON: `/openapi.json`
- Swagger UI: `/docs`
- ReDoc: `/redoc`
