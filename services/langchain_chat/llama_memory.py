# Ref: https://yanshuai.name/integrating-llama-with-langchain-a-custom-memory-class-example

from typing import Any, Dict, List, Optional
from pydantic import root_validator
from langchain.memory.chat_memory import BaseMemory
from langchain.memory.utils import get_prompt_input_key


class LlamaMemory(BaseMemory):
    """Buffer for storing conversation memory."""

    human_prefix: str = "user"
    ai_prefix: str = "assistant"
    """Prefix to use for AI generated responses."""
    buffer: str = ""
    output_key: Optional[str] = None
    input_key: Optional[str] = None
    memory_key: str = "history"  #: :meta private:

    @root_validator()
    def validate_chains(cls, values: Dict) -> Dict:
        """Validate that return messages is not True."""
        if values.get("return_messages", False):
            raise ValueError(
                "return_messages must be False for LlamaMemory"
            )
        return values

    @property
    def memory_variables(self) -> List[str]:
        """Will always return list of memory variables.
        :meta private:
        """
        return [self.memory_key]

    def load_memory_variables(self, inputs: Dict[str, Any]) -> Dict[str, str]:
        """Return history buffer."""
        return {self.memory_key: self.buffer}

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, str]) -> None:
        """Save context from this conversation to buffer."""
        if self.input_key is None:
            prompt_input_key = get_prompt_input_key(
                inputs, self.memory_variables)
        else:
            prompt_input_key = self.input_key
        if self.output_key is None:
            if len(outputs) != 1:
                raise ValueError(
                    f"One output key expected, got {outputs.keys()}")
            output_key = list(outputs.keys())[0]
        else:
            output_key = self.output_key
        human = inputs[prompt_input_key]
        ai = outputs[output_key]
        self.buffer += "<|im_start|>" + self.human_prefix + "\n" + human + "<|im_end|>"
        self.buffer += "<|im_start|>" + self.ai_prefix + "\n" + ai + "<|im_end|>"

    def clear(self) -> None:
        """Clear memory contents."""
        self.buffer = ""
