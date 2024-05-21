from pydantic import BaseModel
import replicate
from typing import List


class ChatLLM(BaseModel):
    model: str = "snowflake/snowflake-arctic-instruct"
    temperature: float = 0.0
    top_p: float = 1.0

    def generate(self, prompt: str, prompt_template: str, stop: List[str] = ["<|im_end|>"]):
        prediction = replicate.models.predictions.create(
                    self.model,
                    input={
                        "prompt": prompt,
                        "prompt_template": prompt_template,
                        "temperature": self.temperature,
                        "top_p": self.top_p,
                        "stop_sequences": ','.join(stop)
                    }
        )
        prediction.wait()
        completion = "".join(prediction.output)
        return completion
