import re

from pydantic import BaseModel

from streamlit_ai_assist.backend.agents.llm import ChatLLM
from streamlit_ai_assist.backend.agents import prompts


PROMPT_TEMPLATE = prompts.FUNCTION_REWRITE_PROMPT


class FunctionRewriteAgent(BaseModel):
    llm: ChatLLM
    prompt_template: str = PROMPT_TEMPLATE

    def rewrite_function(self, code_str: str):
        generated = self.llm.generate(prompt=code_str, prompt_template=self.prompt_template)
        if len(generated) < 10:
            return self.clean_function(code_str)
        return self.clean_function(generated)

    def clean_function(self, code_str: str):
        code_str = re.sub(r'^```(?:python\s*)?|```$', '', code_str)
        return code_str + '\n    return fig'
