import re
from typing import List, Tuple

from pydantic import BaseModel

from streamlit_ai_assist.backend.agents.llm import ChatLLM
from streamlit_ai_assist.backend.agents import prompts
from streamlit_ai_assist.backend.agents.data_analyst_agent import DataAnalystAgent


PROMPT_TEMPLATE = prompts.CONVERSATIONAL_PROMPT
FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Output from data analyst:"
THOUGHT_TOKEN = "Thought:"


class ConversationalAgent(BaseModel):
    llm: ChatLLM
    general_description: str
    prompt_template: str = PROMPT_TEMPLATE
    max_loops: int = 2
    data_analyst: DataAnalystAgent
    stop_pattern: List[str] = [
        f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}', '<|im_end|>'
    ]
    conversation_history: List[dict] = []
    data_analysis_results: List[dict] = []

    class Config:
        arbitrary_types_allowed = True

    def get_prompt_template(self, add_thought_token=False):
        prompt = [PROMPT_TEMPLATE]
        for dict_message in self.conversation_history:
            if dict_message["role"] == "user":
                prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
            elif dict_message["role"] == "assistant":
                prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
        prompt.append("<|im_start|>assistant")
        if add_thought_token:
            prompt.append(f"{THOUGHT_TOKEN}")
        else:
            prompt.append("")
        prompt_str = "\n".join(prompt)
        return prompt_str.format(general_description=self.general_description)

    def add_to_conversation_history(self, role, message):
        self.conversation_history.append(dict(role=role, content=message))

    def clear_data(self):
        self.data_analysis_results = []

    def _parse(self, generated: str) -> Tuple[str, str]:
        if FINAL_ANSWER_TOKEN in generated:
            print("End reached")
            return "Final Answer", generated.split(FINAL_ANSWER_TOKEN)[-1].strip()
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            return None, None
        tool = match.group(1).strip()
        tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')

    def decide_next_action(self, prompt: str) -> str:
        print(prompt)
        generated = self.llm.generate(prompt, r"{prompt}", stop=self.stop_pattern)
        print(generated)
        tool, tool_input = self._parse(generated)
        tool = tool.lower().strip()
        if "final answer" in tool:
            return generated, None, tool_input
        elif "ask for analysis" in tool:
            return generated, "ask for analysis", tool_input
        else:
            return generated, "Tool must be one of ('respond to user', 'ask for analysis')", None

    def run(self, query):
        self.add_to_conversation_history("user", query)
        num_loops = 0
        while num_loops < self.max_loops:
            num_loops += 1
            if num_loops > 1:
                add_thought_token = False
            else:
                add_thought_token = True
            prompt = self.get_prompt_template(add_thought_token=add_thought_token)
            generated, tool, tool_input = self.decide_next_action(prompt=prompt)
            self.add_to_conversation_history("assistant", generated)
            print('TOOL', tool)
            if tool is None:  # final answer reached
                self.add_to_conversation_history("assistant", tool_input)
                print("exiting run")
                return tool_input, self.data_analysis_results
            elif tool == "ask for analysis":
                data_analysis_results = list(self.data_analyst.run(tool_input))
                to_summarize = [
                    r[k].split("Action:")[0] for r in data_analysis_results
                    for k in r if k in ("thought", "observation")
                ]
                tool_result = '----'.join(to_summarize)
                self.data_analysis_results = data_analysis_results
            else:
                tool_result = None
            if tool_result:
                self.add_to_conversation_history(
                    "assistant", f"\n{OBSERVATION_TOKEN} {tool_result}"
                )
                self.add_to_conversation_history(
                    "assistant", f"\n{THOUGHT_TOKEN} I can now respond to the user"
                )
                self.add_to_conversation_history("assistant", "Action: respond to user")
            else:
                self.add_to_conversation_history(
                    "assistant",
                    f"\n{THOUGHT_TOKEN} Tool must be one of ('respond to user', 'ask for analysis')"
                )
        return '\n'.join([c['content'] for c in self.conversation_history]), []

    def generate(self, content_to_summarize="", conversation_history=[]):
        generated = self.llm.generate(
            prompt=self.get_prompt(content_to_summarize, conversation_history),
            prompt_template=r"{prompt}"
        )
        return generated
