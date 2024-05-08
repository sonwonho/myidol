from typing import Optional

import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel

from utils.karlo_api import KarloAPI
from utils.prompt_mapper import PromptMapper

app = FastAPI()
karlo = KarloAPI()
prompt_mapper = PromptMapper()


class SelectItem(BaseModel):
    age: Optional[str]
    sex: str
    mbti: Optional[str]
    lookLike: Optional[str]
    height: Optional[str]
    eyeShape: str
    faceShape: str
    fashion: Optional[str]
    hobby1: Optional[str]
    hobby2: Optional[str]
    hobbyList: list


@app.post("/make_picture")
def make_image(select: SelectItem):
    prompt_data_list = [select.sex, select.eyeShape, select.faceShape]
    prompt, negative_prompt = prompt_mapper.make_prompt(prompt_data_list)
    image_url = karlo.get_image_url(prompt, negative_prompt)
    select_dict = select.model_dump()
    select_dict.pop("hobby1", None)
    select_dict.pop("hobby2", None)
    hobby = select_dict.pop("hobbyList", None)
    if hobby:
        hobby = ", ".join(hobby)
    select_dict.update({"hobby": hobby})
    select_dict.update({"picture": image_url})
    result = {"code": "200", "data": select_dict, "message": "OK"}
    return result


if __name__ == "__main__":
    uvicorn.run(app="mosol:app", host="0.0.0.0", port=5000, reload=False)
