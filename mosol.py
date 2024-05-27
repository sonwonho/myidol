import io
from typing import Optional

import requests
import uvicorn
from fastapi import FastAPI
from PIL import Image
from pydantic import BaseModel
from starlette.responses import StreamingResponse

from utils.karlo_api import KarloAPI
from utils.prompt_mapper import PromptMapper

app = FastAPI()
karlo = KarloAPI()
prompt_mapper = PromptMapper()


class SelectItem(BaseModel):
    age: Optional[str] = None
    sex: str
    mbti: Optional[str] = None
    lookLike: Optional[str] = None
    height: Optional[str] = None
    eyeShape: str
    faceShape: str
    fashion: Optional[str] = None
    hobby1: Optional[str] = None
    hobby2: Optional[str] = None
    hobbyList: Optional[list] = None
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": "10대",
                    "sex": "남성",
                    "mbti": "ISTJ",
                    "lookLike": "홍길동",
                    "height": "156cm ~ 160cm",
                    "eyeShape": "무쌍 실눈",
                    "faceShape": "강아지상",
                    "fashion": "미니멀",
                    "hobby1": "영화",
                    "hobby2": "축구",
                    "hobbyList": ["축구", "농구"],
                }
            ]
        }
    }


class PictureItem(BaseModel):
    age: Optional[str] = None
    sex: str
    mbti: Optional[str] = None
    lookLike: Optional[str] = None
    height: Optional[str] = None
    eyeShape: str
    faceShape: str
    fashion: Optional[str] = None
    hobby: Optional[str] = None
    picture: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "age": "10대",
                    "sex": "남성",
                    "mbti": "ISTJ",
                    "lookLike": "홍길동",
                    "height": "156cm ~ 160cm",
                    "eyeShape": "무쌍 실눈",
                    "faceShape": "강아지상",
                    "fashion": "미니멀",
                    "hobby": "축구, 농구",
                    "picture": "https://mk.kakaocdn.net/dna/karlo/image/yyyy-mm-dd/...",
                }
            ]
        }
    }


class ResultItem(BaseModel):
    code: str
    data: Optional[PictureItem] = None
    message: str
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "code": "200",
                    "data": {
                        "age": "10대",
                        "sex": "남성",
                        "mbti": "ISTJ",
                        "lookLike": "홍길동",
                        "height": "156cm ~ 160cm",
                        "eyeShape": "무쌍 실눈",
                        "faceShape": "강아지상",
                        "fashion": "미니멀",
                        "hobby": "축구, 농구",
                        "picture": "https://mk.kakaocdn.net/dna/karlo/image/yyyy-mm-dd/...",
                    },
                    "message": "OK",
                }
            ]
        }
    }


class EssentialPrompt(BaseModel):
    prompt: list[str]
    negative_prompt: list[str]
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "prompt": prompt_mapper.essential_prompt["prompt"],
                    "negative_prompt": prompt_mapper.essential_prompt[
                        "negative_prompt"
                    ],
                }
            ]
        }
    }


def get_looklike_image(looklike):
    image_url = "http://192.168.219.106:8080/code/image/looklike/" + looklike
    response = requests.get(image_url)
    try:
        image = Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(e)
        return
    return image


@app.post("/make_picture", response_model=ResultItem)
def make_image(select: SelectItem):
    prompt_data_list = [select.sex, select.eyeShape, select.faceShape]
    prompt, negative_prompt = prompt_mapper.make_prompt(prompt_data_list)
    image = get_looklike_image(select.lookLike)
    if image:
        image_url = karlo.modfiy_image(prompt, negative_prompt, image)
    else:
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


@app.post("/set_essential_prompt", response_model=EssentialPrompt)
def set_essential_prompt(prompts: EssentialPrompt):
    prompt_mapper.set_essential_prompt(prompts.prompt, prompts.negative_prompt)
    return prompt_mapper.essential_prompt


@app.post("/show_picture")
def show_image(select: SelectItem):
    prompt_data_list = [select.sex, select.eyeShape, select.faceShape]
    prompt, negative_prompt = prompt_mapper.make_prompt(prompt_data_list)
    image = get_looklike_image(select.lookLike)
    image = karlo.get_image(prompt, negative_prompt, image)
    imgio = io.BytesIO()
    image.save(imgio, "JPEG")
    imgio.seek(0)
    return StreamingResponse(content=imgio, media_type="image/jpeg")


if __name__ == "__main__":
    # uvicorn.run(app="mosol:app", host="0.0.0.0", port=5000, reload=False)
    uvicorn.run(app="mosol:app", host="127.0.0.1", port=8000, reload=True)
