from llm_sdk import Small_LLM_Model


class LLMClient:
    def __init__(self) -> None:
        self.model = Small_LLM_Model()

    def encode(self, text: str) -> list[int]:
        return self.model.encode(text)[0].tolist()

    def decode(self, token_ids: list[int]) -> str:
        return self.model.decode(token_ids)

    def get_logits(self, input_ids: list[int]) -> list[float]:
        return self.model.get_logits_from_input_ids(input_ids)

    def get_vocab_path(self) -> str:
        return self.model.get_path_to_vocab_file()