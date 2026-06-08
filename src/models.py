from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


JsonType = Literal["string", "number", "integer", "boolean"]


class FunctionParameter(BaseModel):
    type: JsonType


class FunctionReturn(BaseModel):
    type: JsonType


class FunctionDefinition(BaseModel):
    name: str
    description: str
    parameters: dict[str, FunctionParameter]
    returns: FunctionReturn


class PromptInput(BaseModel):
    prompt: str


class FunctionCallOutput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prompt: str
    name: str
    parameters: dict[str, Any]