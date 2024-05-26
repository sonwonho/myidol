import base64
import io
import json
import urllib
import urllib.request
from typing import Union

import numpy as np
import requests
from PIL import Image


def imageToString(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format="PNG")
    my_encoded_img = base64.encodebytes(img_byte_arr.getvalue()).decode("ascii")
    return my_encoded_img


class KarloAPI:
    def __init__(self) -> None:
        self.config = self._get_config()
        return

    def _get_config(self) -> dict:
        with open("env/karlo_config.json", "r", encoding="utf8") as f:
            config = json.load(f)
        return config

    def t2i(self, prompt: str, negative_prompt: str) -> Union[dict, int]:
        r = requests.post(
            "https://api.kakaobrain.com/v2/inference/karlo/t2i",
            json={
                "version": self.config["version"],
                "prompt": prompt,
                "negative_prompt": negative_prompt,
                "width": self.config["width"],
                "height": self.config["height"],
                "upscale": self.config["upscale"],
                "scale": self.config["scale"],
                "image_format": self.config["image_format"],
                "image_quality": self.config["image_quality"],
                "samples": self.config["samples"],
                "return_type": self.config["return_type"],
                "prior_num_inference_steps": self.config[
                    "prior_num_inference_steps"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-num-inference-steps
                "prior_guidance_scale": self.config[
                    "prior_guidance_scale"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-guidance-scale
                "num_inference_steps": self.config[
                    "num_inference_steps"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-num-interence-steps
                "guidance_scale": self.config[
                    "guidance_scale"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-guidance-scale
            },
            headers={
                "Authorization": f"KakaoAK {self.config['api_key']}",
                "Content-Type": "application/json",
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content)
            return response
        else:
            return r.status_code

    def i2i(self, base64_image: str) -> Union[dict, int]:
        r = requests.post(
            "https://api.kakaobrain.com/v2/inference/karlo/variations",
            json={
                "version": self.config["version"],
                "image": base64_image.decode("utf-8"),
                "width": self.config["width"],
                "height": self.config["height"],
                "upscale": self.config["upscale"],
                "scale": self.config["scale"],
                "image_format": self.config["image_format"],
                "image_quality": self.config["image_quality"],
                "samples": self.config["samples"],
                "return_type": self.config["return_type"],
                "prior_num_inference_steps": self.config[
                    "prior_num_inference_steps"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-num-inference-steps
                "prior_guidance_scale": self.config[
                    "prior_guidance_scale"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-guidance-scale
                "num_inference_steps": self.config[
                    "num_inference_steps"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-num-interence-steps
                "guidance_scale": self.config[
                    "guidance_scale"
                ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-guidance-scale
            },
            headers={
                "Authorization": f"KakaoAK {self.config['api_key']}",
                "Content-Type": "application/json",
            },
        )
        if r.status_code == 200:
            response = json.loads(r.content)
            return response
        else:
            return r.status_code

    def ici(self, prompt: str, negative_prompt: str, image: Image) -> Union[dict, int]:
        mask = Image.new("RGB", image.size, (0, 0, 0))
        try:
            r = requests.post(
                "https://api.kakaobrain.com/v2/inference/karlo/inpainting",
                json={
                    # "version": "v2.0",
                    "prompt": prompt,
                    "negative_prompt": negative_prompt,
                    "image": imageToString(image),
                    "mask": imageToString(mask),
                    "reference_image": imageToString(image),
                    "upscale": self.config["upscale"],
                    "scale": self.config["scale"],
                    "image_format": self.config["image_format"],
                    "image_quality": self.config["image_quality"],
                    "samples": self.config["samples"],
                    "return_type": self.config["return_type"],
                    "prior_num_inference_steps": self.config[
                        "prior_num_inference_steps"
                    ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-num-inference-steps
                    "prior_guidance_scale": self.config[
                        "prior_guidance_scale"
                    ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-prior-guidance-scale
                    "num_inference_steps": self.config[
                        "num_inference_steps"
                    ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-num-interence-steps
                    "guidance_scale": self.config[
                        "guidance_scale"
                    ],  # https://developers.kakao.com/docs/latest/ko/karlo/how-to-use#parameter-guidance-scale
                },
                headers={
                    "Authorization": f"KakaoAK {self.config['api_key']}",
                    "Content-Type": "application/json",
                },
            )
        except Exception as e:
            print(e)

        if r.status_code == 200:
            response = json.loads(r.content)
            return response
        else:
            return r.status_code

    def get_image(
        self, prompt: str, negative_prompt: str, image: str
    ) -> Union[list, dict]:
        if image:
            response = self.ici(prompt, negative_prompt, image)
        else:
            response = self.t2i(prompt, negative_prompt)
        try:
            image = Image.open(
                urllib.request.urlopen(response.get("images")[0].get("image"))
            )
            print(type(image))
            return image
        except:
            return response

    def get_image_url(self, prompt: str, negative_prompt: str) -> str:
        response = self.t2i(prompt, negative_prompt)
        try:
            url = response.get("images")[0].get("image")
            return url
        except:
            return response

    def modfiy_image(self, prompt: str, negative_prompt: str, image: bytes) -> str:
        response = self.ici(prompt, negative_prompt, image)
        try:
            url = response.get("images")[0].get("image")
            return url
        except:
            return response


if __name__ == "__main__":
    import time

    karlo = KarloAPI()
    prompt = "A picture of korean handsome man, chic-looking face, big eyes, symmetric eyes, detail description of face, masterpiece"
    negative_prompt = "asymmetry eyes, ugly, grotesque, scary, strange, hanbok"

    s = time.time()
    image = karlo.get_image(prompt, negative_prompt)
    print(time.time() - s)
    try:
        image.show()
        print()
    except:
        print(image)
