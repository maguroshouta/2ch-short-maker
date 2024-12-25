import MeCab
import requests
from bs4 import BeautifulSoup


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


def irasutoya_search(keyword: str):
    url = f"https://www.irasutoya.com/search?q={keyword}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    boxim_list = soup.find_all("div", {"class": "boxim"})
    if boxim_list is None or len(boxim_list) == 0:
        return None
    url = boxim_list[0].find("a")["href"]
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    entry = soup.find("div", {"class": "entry"})
    image_url = entry.find("a")["href"]

    return image_url
