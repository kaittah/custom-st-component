import datetime
import re
from typing import List, Dict, Tuple

from pydantic import BaseModel

from streamlit_ai_assist.backend.agents.llm import ChatLLM
from streamlit_ai_assist.backend.agents import prompts
from streamlit_ai_assist.backend.tools.base import ToolInterface
from streamlit_ai_assist.backend.data.database_connection import DatabaseConnection

import logging

logger = logging.getLogger(__name__)

FINAL_ANSWER_TOKEN = "Final Answer:"
OBSERVATION_TOKEN = "Observation:"
THOUGHT_TOKEN = "Thought:"
PROMPT_TEMPLATE = prompts.DATA_ANALYST_PROMPT


class DataAnalystAgent(BaseModel):
    llm: ChatLLM
    tools: List[ToolInterface]
    db: DatabaseConnection
    max_loops: int = 8
    stop_pattern: List[str] = [f'\n{OBSERVATION_TOKEN}', f'\n\t{OBSERVATION_TOKEN}', '<|im_end|>']
    conversation_history: List[dict] = []

    class Config:
        arbitrary_types_allowed = True

    @property
    def tool_description(self) -> str:
        return "\n".join([f"{tool.name}: {tool.get_description(self.db)}" for tool in self.tools])

    @property
    def tool_names(self) -> str:
        return ",".join([tool.name for tool in self.tools])

    @property
    def tool_by_names(self) -> Dict[str, ToolInterface]:
        return {tool.name: tool for tool in self.tools}

    def get_prompt_template(self, add_thought_token=False):
        prompt = [PROMPT_TEMPLATE]
        for dict_message in self.conversation_history:
            if dict_message["role"] == "user":
                prompt.append("<|im_start|>user\n" + dict_message["content"] + "<|im_end|>")
            elif dict_message["role"] == "data_analyst":
                prompt.append("<|im_start|>assistant\n" + dict_message["content"] + "<|im_end|>")
        prompt.append("<|im_start|>assistant")
        if add_thought_token:
            prompt.append(f"{THOUGHT_TOKEN}")
        else:
            prompt.append("")
        prompt_str = "\n".join(prompt)
        return prompt_str.format(
                today=datetime.date.today(),
                tool_description=self.tool_description,
                tool_names=self.tool_names,)

    def add_to_conversation_history(self, role, message):
        self.conversation_history.append(dict(role=role, content=message))

    def edit_latest_conversation_history(self, message):
        if self.conversation_history:
            self.conversation_history[-1]["content"] = message

    def run(self, query):
        self.add_to_conversation_history("user", query)
        num_loops = 0

        while num_loops < self.max_loops:
            num_loops += 1
            prompt = self.get_prompt_template(add_thought_token=True)

            logger.info("Deciding next action")
            logger.info(prompt)
            generated, tool, tool_input = self.decide_next_action(prompt=prompt)

            logger.info(generated)
            logger.info(tool)
            logger.info(tool_input)

            if not generated:
                self.edit_latest_conversation_history(
                    "Thought: I need to think again about what to do"
                )
                prompt = self.get_prompt_template(add_thought_token=True)
                generated, tool, tool_input = self.decide_next_action(
                        prompt=prompt)
                if not generated:
                    break

            output_row = {
                'rendered_prompt': prompt,
                'loop_number': num_loops,
                'thought': generated,
                'tool': tool,
            }

            if tool == 'Final Answer':
                output_row['observation'] = 'Final'
                output_row["eval"] = None
                output_row["exec"] = None
                output_row["print"] = None
                output_row["dataframe"] = None
                yield output_row
                break
            if tool not in self.tool_by_names:
                output_row['observation'] = 'Failed to proceed.'
                output_row["eval"] = None
                output_row["exec"] = None
                output_row["print"] = None
                output_row["dataframe"] = None
                yield output_row
                continue

            tool_result = self.tool_by_names[tool].use(tool_input, self.db)
            tool_result_observation = tool_result["observation"]
            output_row['observation'] = tool_result_observation
            output_row["eval"] = tool_result.get("eval")
            output_row["exec"] = tool_result.get("exec")
            output_row["print"] = tool_result.get("print")
            output_row["dataframe"] = tool_result.get("dataframe")

            self.add_to_conversation_history("data_analyst", generated)
            self.add_to_conversation_history(
                "data_analyst", f"\n{OBSERVATION_TOKEN} {tool_result_observation}"
            )
            yield output_row

    def decide_next_action(self, prompt: str) -> str:
        generated = self.llm.generate(prompt, r"{prompt}", stop=self.stop_pattern)
        tool, tool_input = self._parse(generated)
        try_num = 0
        while not tool and try_num < 3:
            generated = self.llm.generate(prompt, r"{prompt}", stop=self.stop_pattern)
            tool, tool_input = self._parse(generated)
            try_num += 1
        if not tool:
            return None, None, None
        return generated, tool, tool_input

    def _parse(self, generated: str) -> Tuple[str, str]:
        if FINAL_ANSWER_TOKEN in generated:
            return "Final Answer", generated.split(FINAL_ANSWER_TOKEN)[-1].strip()
        regex = r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)"
        match = re.search(regex, generated, re.DOTALL)
        if not match:
            return None, None
        tool = match.group(1).strip()
        tool_input = match.group(2)
        return tool, tool_input.strip(" ").strip('"')
