from llm_sdk import Small_LLM_Model  # type: ignore[attr-defined]


class LLMClient:
    """Thin wrapper around the small LLM model providing encode/decode."""

    def __init__(self) -> None:
        """Initialize the underlying small LLM model client."""
        self.model = Small_LLM_Model()

    def encode(self, text: str) -> list[int]:
        """Encode text into token ids.

        Args:
            text: The input string to encode.

        Returns:
            A list of token ids representing `text`.
        """
        result: list[int] = self.model.encode(text)[0].tolist()
        return result

    def decode(self, token_ids: list[int]) -> str:
        """Decode token ids into a string.

        Args:
            token_ids: Sequence of token ids to decode.

        Returns:
            The decoded string.
        """
        result: str = self.model.decode(token_ids)
        return result

    def get_logits(self, input_ids: list[int]) -> list[float]:
        """Return logits for the given input ids.

        Args:
            input_ids: Token ids to compute logits for.

        Returns:
            A list of logits matching the model vocabulary.
        """
        result: list[float] = self.model.get_logits_from_input_ids(input_ids)
        return result
