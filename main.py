import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional

from database import create_document
from schemas import Cabinet, ModuleOption, Size, Configuration

app = FastAPI(title="Furniture Module Configurator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static catalog data for three cabinet types
CATALOG: List[Cabinet] = [
    Cabinet(
        code="BASE",
        name="Base Cabinet",
        modules=[
            ModuleOption(size=Size(width=600, height=720, depth=560), materials=["MDF", "Plywood", "Solid Wood"], colors=["White", "Oak", "Walnut", "Black"]),
            ModuleOption(size=Size(width=800, height=720, depth=560), materials=["MDF", "Plywood"], colors=["White", "Grey", "Oak"]),
        ],
    ),
    Cabinet(
        code="WALL",
        name="Wall Cabinet",
        modules=[
            ModuleOption(size=Size(width=600, height=720, depth=330), materials=["MDF", "Aluminum Frame"], colors=["White", "Glass", "Black"]),
            ModuleOption(size=Size(width=900, height=360, depth=330), materials=["MDF"], colors=["White", "Grey"]) ,
        ],
    ),
    Cabinet(
        code="TALL",
        name="Tall Cabinet",
        modules=[
            ModuleOption(size=Size(width=600, height=2140, depth=560), materials=["MDF", "Plywood"], colors=["White", "Oak", "Walnut"]),
            ModuleOption(size=Size(width=450, height=2140, depth=560), materials=["MDF"], colors=["White", "Graphite"]) ,
        ],
    ),
]


@app.get("/")
def read_root():
    return {"message": "Furniture Configurator Backend Running"}


@app.get("/api/cabinets", response_model=List[Cabinet])
def get_cabinets():
    return CATALOG


@app.get("/api/cabinets/{code}", response_model=Cabinet)
def get_cabinet(code: str):
    cab = next((c for c in CATALOG if c.code.lower() == code.lower()), None)
    if not cab:
        raise HTTPException(status_code=404, detail="Cabinet not found")
    return cab


@app.post("/api/configurations")
def create_configuration(config: Configuration):
    # Basic validation: ensure selected size/material/color exist for that cabinet
    cab = next((c for c in CATALOG if c.code == config.cabinet_code), None)
    if not cab:
        raise HTTPException(status_code=400, detail="Invalid cabinet code")

    def size_equals(a: Size, b: Size) -> bool:
        return a.width == b.width and a.height == b.height and a.depth == b.depth

    valid_variant = next(
        (m for m in cab.modules if size_equals(m.size, config.size)),
        None,
    )
    if not valid_variant:
        raise HTTPException(status_code=400, detail="Invalid size for selected cabinet")

    if config.material not in valid_variant.materials:
        raise HTTPException(status_code=400, detail="Invalid material for selected size")
    if config.color not in valid_variant.colors:
        raise HTTPException(status_code=400, detail="Invalid color for selected size")

    inserted_id = create_document("configuration", config)
    return {"id": inserted_id, "status": "saved"}


@app.get("/test")
def test_database():
    """Simple check used by the environment to verify DB connectivity"""
    resp = {"backend": "running"}
    try:
        from database import db
        if db is not None:
            resp["database"] = "connected"
            resp["collections"] = db.list_collection_names()
        else:
            resp["database"] = "not_configured"
    except Exception as e:
        resp["database"] = f"error: {str(e)[:80]}"
    return resp


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
