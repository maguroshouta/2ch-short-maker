from io import BytesIO

import httpx
import MeCab
from bs4 import BeautifulSoup
from PIL import Image


def wrap_text(text: str, width: int):
    mecab = MeCab.Tagger("-Owakati")
    words = mecab.parse(text).strip().split()

    wrapped_text = []
    line = ""
    for word in words:
        if len(line) + len(word) > width:
            wrapped_text.append(line)
            line = word
        else:
            line += word
    wrapped_text.append(line)
    return wrapped_text


httpx_client = httpx.AsyncClient()


async def get_irasutoya_img(keyword: str):
    url = f"https://www.irasutoya.com/search?q={keyword}"
    response = await httpx_client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    boxim_list = soup.find_all("div", {"class": "boxim"})
    if boxim_list is None or len(boxim_list) == 0:
        return None
    url = boxim_list[0].find("a")["href"]
    response = await httpx_client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    entry = soup.find("div", {"class": "entry"})
    if entry is None:
        return None
    image_url = entry.find("a")["href"]

    response = await httpx_client.get(image_url)
    img = Image.open(BytesIO(response.content))

    return img
