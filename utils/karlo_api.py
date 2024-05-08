import json
import urllib
import urllib.request
from typing import Union

import requests
from PIL import Image


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

    def get_image(self, prompt: str, negative_prompt: str) -> Union[list, dict]:
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
