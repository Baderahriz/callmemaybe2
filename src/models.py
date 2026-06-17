from typing import Any, Literal

from pydantic import BaseModel, ConfigDict


JsonType = Literal["string", "number", "integer", "boolean"]


class FunctionParameter(BaseModel):
    """Schema for a single function parameter.

    Attributes:
        type: The JSON type of the parameter ("string", "number", etc.).
    """
    type: JsonType


class FunctionReturn(BaseModel):
    """Schema for a function return type.

    Attributes:
        type: The JSON type of the return value.
    """
    type: JsonType


class FunctionDefinition(BaseModel):
    """Definition of a callable function exposed to the LLM.

    Attributes:
        name: Function name.
        description: Short description of the function.
        parameters: Mapping of parameter names to types.
        returns: The return type schema.
    """
    name: str
    description: str
    parameters: dict[str, FunctionParameter]
    returns: FunctionReturn


class PromptInput(BaseModel):
    """Input prompt model representing a user request.

    Attributes:
        prompt: The raw user prompt string.
    """
    prompt: str


class FunctionCallOutput(BaseModel):
    """Output model produced by the function-calling pipeline.

    Attributes:
        prompt: Original user prompt.
        name: Selected function name.
        parameters: Resolved parameters for the call.
    """
    model_config = ConfigDict(extra="forbid")

    prompt: str
    name: str
    parameters: dict[str, Any]
