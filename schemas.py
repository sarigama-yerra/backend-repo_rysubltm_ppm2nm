"""
Database Schemas for Furniture Configurator

Each Pydantic model corresponds to a MongoDB collection whose name is the
lowercased class name. For example:
- Configuration -> "configuration" collection

Only user-created data is persisted (configurations). The available cabinet
options are static and served by the API without persistence.
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class Size(BaseModel):
    width: int = Field(..., gt=0, description="Width in mm")
    height: int = Field(..., gt=0, description="Height in mm")
    depth: int = Field(..., gt=0, description="Depth in mm")


class ModuleOption(BaseModel):
    size: Size
    materials: List[str]
    colors: List[str]


class Cabinet(BaseModel):
    code: str = Field(..., description="Unique code for cabinet type, e.g. BASE, WALL, TALL")
    name: str = Field(..., description="Human-readable name")
    modules: List[ModuleOption] = Field(default_factory=list)


class Configuration(BaseModel):
    customer: Optional[str] = Field(None, description="Customer name or identifier")
    cabinet_code: str = Field(..., description="Selected cabinet type code")
    size: Size
    material: str
    color: str
    notes: Optional[str] = None
