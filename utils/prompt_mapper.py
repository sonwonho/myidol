import json
from typing import Union

import pandas as pd

MAPPING_FILE_PATH = "env/prompt_mapping.csv"


class PromptMapper:
    def __init__(self) -> None:
        self._get_mapping()
        self._get_essential_prompt()
        return

    def _get_mapping(self) -> None:
        self.df = pd.read_csv(MAPPING_FILE_PATH)
        return

    def _get_essential_prompt(self) -> None:
        with open("env/essential_prompt.json", "r", encoding="utf8") as f:
            loaded_json = json.load(f)
        self.essential_prompt = loaded_json
        return

    def get_prompt(self, key: str) -> str:
        try:
            result = str(self.df[(self.df["key"] == key)]["prompt"].values[0])
        except:
            result = ""
        return result

    def make_prompt(self, keys: list) -> Union[str, str]:
        prompt_list = [self.get_prompt(k) for k in keys]
        prompt = ", ".join(prompt_list + self.essential_prompt["prompt"])
        negative_prompt = ", ".join(self.essential_prompt["negative_prompt"])
        return prompt, negative_prompt


if __name__ == "__main__":
    pm = PromptMapper()
    p, n = pm.make_prompt(["남성", "무쌍 실눈", "고양이상"])
    print(p)
    print(n)
