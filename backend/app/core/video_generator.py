import asyncio
import json
import subprocess
import uuid
from io import BytesIO
from logging import getLogger

import httpx
import MeCab
import numpy
from bs4 import BeautifulSoup
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
)
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.core.env import OPENAI_API_KEY

openai = OpenAI(
    api_key=OPENAI_API_KEY,
)

logger = getLogger(__name__)

httpx_client = httpx.AsyncClient()

mecab = MeCab.Tagger("-Owakati")


def wrap_text(text: str, width: int):
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


async def get_irasutoya_img(keyword: str):
    url = f"https://www.irasutoya.com/search?q={keyword}"
    response = await httpx_client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    boxim_list = soup.find_all("div", {"class": "boxim"})
    if boxim_list is None or len(boxim_list) == 0:
        return None
    url = boxim_list[0].find("a")["href"]
    if url is None:
        return None
    response = await httpx_client.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    entry = soup.find("div", {"class": "entry"})
    if entry is None:
        return None
    image_url = entry.find("a")["href"]
    if image_url is None:
        return None

    response = await httpx_client.get(image_url)
    img = Image.open(BytesIO(response.content))

    return img


def create_title_text(
    text: str,
    color: tuple[int, int, int, int],
    stroke_color: tuple[int, int, int, int],
    stroke_width: int,
    shadow_stroke_width: int,
):
    font = ImageFont.truetype("static/fonts/keifont.ttf", 130)
    left, top, right, bottom = font.getbbox(text)
    text_width = right - left
    text_height = bottom - top

    padding = 120

    img_width = text_width + padding
    img_height = text_height + padding

    img_size = (img_width, img_height)
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    center_x = (img_size[0] - text_width) // 2
    center_y = (img_size[1] - text_height) // 2

    shadow_image = Image.new("RGBA", img_size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow_image)
    shadow_draw.text(
        (center_x, center_y),
        text,
        font=font,
        stroke_width=shadow_stroke_width,
        stroke_fill=(0, 0, 0),
        fill=(0, 0, 0),
    )

    blurred_image = shadow_image.filter(ImageFilter.GaussianBlur(radius=8))

    img.paste(blurred_image, blurred_image)

    draw.text(
        (center_x, center_y),
        text,
        font=font,
        stroke_width=stroke_width,
        stroke_fill=stroke_color,
        fill=color,
    )

    return img


def create_message_box(texts: list[str], border_color: tuple[int, int, int, int]):
    font = ImageFont.truetype("static/fonts/keifont.ttf", 80)

    longest_line = max(texts, key=len)

    left, top, right, bottom = font.getbbox(longest_line)
    text_width = right - left
    text_height = bottom - top

    padding = 60

    img_width = text_width + padding + 20
    img_height = text_height * len(texts) + padding

    img_size = (img_width, img_height)
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle(
        (0, 0, img_size[0], img_size[1]),
        fill=(255, 255, 255),
        outline=border_color,
        width=8,
    )

    for i, line in enumerate(texts):
        draw.text(
            (25, 25 + i * 80),
            line,
            font=font,
            fill=(0, 0, 0),
        )

    return img


def create_title_clip(
    text: str,
    text_color: tuple[int, int, int, int],
    stroke_color: tuple[int, int, int, int],
    stroke_width: int,
    shadow_stroke_width: int,
):
    img = create_title_text(text, text_color, stroke_color, stroke_width, shadow_stroke_width)
    img_array = numpy.array(img)
    clip = ImageClip(img_array)
    return clip


def create_message_box_clip(
    texts: list[str],
    border_color: tuple[int, int, int, int],
):
    img = create_message_box(texts, border_color)
    img_array = numpy.array(img)
    clip = ImageClip(img_array)
    return clip


def generate_aquestalk_voice(text: str, voice_preset: str, output_path: str):
    cmd = [
        "wine",
        "static/aquestalkplayer/AquesTalkPlayer.exe",
        "/nogui",
        "/T",
        text,
        "/P",
        voice_preset,
        "/W",
        output_path,
    ]
    subprocess.run(" ".join(cmd), shell=True)


def create_voice_clip(text: str, voice_preset: str):
    id = uuid.uuid4()
    output_path = f"/tmp/{id}.wav"
    generate_aquestalk_voice(text, voice_preset, output_path)
    clip = AudioFileClip(output_path)
    return clip


async def create_irasutoya_clip(keyword: str):
    irasutoya_image = await get_irasutoya_img(keyword)
    if irasutoya_image is None:
        return None
    img_array = numpy.array(irasutoya_image)
    clip = ImageClip(img_array)

    _, image_height = irasutoya_image.size

    related_keyword_clip = clip.with_position(("center", 1920 - image_height))
    return related_keyword_clip


def create_voice_clips(voices: dict[str, dict[str, str]]):
    clips = {}
    for key, value in voices.items():
        text = value["text"]
        voice_preset = value["voice_preset"]
        clip = create_voice_clip(text, voice_preset)
        clips[key] = clip
    return clips


async def create_irasutoya_clips(keywords: list[str]):
    tasks = []
    for keyword in keywords:
        tasks.append(create_irasutoya_clip(keyword))

    results = await asyncio.gather(*tasks)
    return results


async def create_2ch_video(prompt: str):
    system_prompt = """
**指示**
登場人物は「A」と「B」。以下の形式で回答する。
形式：
- テーマに沿ったランキング形式（3位まで）を作成
- ランキングの順番は下から上になるようにする
- AとBは2chのネットオタク風の喋り口調で発言
- 「！」と「？」は禁止、優しい語尾も禁止
- 卑猥な言葉は禁止

**回答例形式**
{テーマ}

{n位}
Aが{テーマ}について回答（30文字程度）
Bが{テーマ}についてAの回答は無視して回答（25文字程度
"""
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": system_prompt,
            },
            {"role": "user", "content": prompt},
        ],
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "2ch_ranking",
                "strict": True,
                "schema": {
                    "type": "object",
                    "properties": {
                        "title": {
                            "type": "string",
                            "description": "テーマに沿ったランキングのタイトル",
                        },
                        "keyword": {
                            "type": "string",
                            "description": "タイトルの単語",
                        },
                        "items": {
                            "type": "array",
                            "description": "ランキングのアイテム",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {
                                        "type": "string",
                                        "description": "アイテムの名前(10文字以内)",
                                    },
                                    "keyword": {
                                        "type": "string",
                                        "description": "アイテムの単語",
                                    },
                                    "A": {
                                        "type": "string",
                                        "description": "Aのメッセージ",
                                    },
                                    "B": {
                                        "type": "string",
                                        "description": "Bのメッセージ",
                                    },
                                },
                                "required": ["title", "A", "B", "keyword"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["title", "items", "keyword"],
                    "additionalProperties": False,
                },
            },
        },
    )

    data = json.loads(response.choices[0].message.content)

    title = data["title"]
    keyword = data["keyword"]
    items = data["items"]

    title_wrapped = wrap_text(title, 8)

    clips = []
    cumulative_duration = 0

    irasutoya_texts = []
    voice_clips_dict = {}

    irasutoya_texts.append(keyword)

    voice_clips_dict["title"] = {
        "text": f"{title}あげてけ",
        "voice_preset": "女性２",
    }

    for index, item in enumerate(items):
        item_title = item["title"]
        item_keyword = item["keyword"]
        message_A = item["A"]
        message_B = item["B"]

        item_title_key = f"item_{index}_title"
        message_A_key = f"item_{index}_A"
        message_B_key = f"item_{index}_B"

        irasutoya_texts.append(item_keyword)

        voice_clips_dict[item_title_key] = {
            "text": item_title,
            "voice_preset": "女性２",
        }
        voice_clips_dict[message_A_key] = {
            "text": message_A,
            "voice_preset": "中性",
        }

        voice_clips_dict[message_B_key] = {
            "text": message_B,
            "voice_preset": "男声２",
        }

    voice_clips = create_voice_clips(voice_clips_dict)
    irasutoya_clips = await create_irasutoya_clips(irasutoya_texts)

    total_voice_duration = sum([clip.duration for clip in voice_clips.values()])

    main_clip = ImageClip("static/images/background.png")
    main_clip = main_clip.with_duration(total_voice_duration)
    main_clip = main_clip.resized((1080, 1920))

    bgm = AudioFileClip("static/audio/bgm.mp3")
    bgm = bgm.subclipped(0, total_voice_duration)

    title_voice = voice_clips["title"]
    cumulative_duration += title_voice.duration
    combined_audio = CompositeAudioClip([title_voice, bgm])

    main_clip = main_clip.with_audio(combined_audio)

    clips.append(main_clip)

    total_height = len(title_wrapped) * 240

    for index, text in enumerate(title_wrapped):
        title_text_clip = (
            create_title_clip(
                text=text,
                text_color=(255, 0, 0, 255),
                stroke_color=(255, 255, 255, 255),
                stroke_width=16,
                shadow_stroke_width=48,
            )
            .with_position(("center", (index * 240) + 120))
            .with_duration(voice_clips["title"].duration)
        )
        clips.append(title_text_clip)

    ageteke_text_clip = (
        create_title_clip(
            text="挙げてけｗ",
            text_color=(255, 255, 255, 255),
            stroke_color=(0, 0, 0, 255),
            stroke_width=0,
            shadow_stroke_width=32,
        )
        .with_position(("center", total_height + 120))
        .with_duration(voice_clips["title"].duration)
    )
    clips.append(ageteke_text_clip)

    irasutoya_clip = irasutoya_clips[0]
    if irasutoya_clip is not None:
        irasutoya_clip = irasutoya_clip.with_duration(voice_clips["title"].duration)
        clips.append(irasutoya_clip)

    for index, item in enumerate(items):
        item_title = item["title"]
        item_keyword = item["keyword"]
        message_A = item["A"]
        message_B = item["B"]

        wrapped_item_title = wrap_text(item_title, 8)
        wrapped_A = wrap_text(message_A, 12)
        wrapped_B = wrap_text(message_B, 12)

        item_title_key = f"item_{index}_title"
        message_A_key = f"item_{index}_A"
        message_B_key = f"item_{index}_B"

        irasutoya_clip = irasutoya_clips[index + 1]
        if irasutoya_clip is not None:
            irasutoya_clip = irasutoya_clip.with_start(cumulative_duration).with_duration(
                voice_clips[item_title_key].duration
                + voice_clips[message_A_key].duration
                + voice_clips[message_B_key].duration
            )
            clips.append(irasutoya_clip)

        for index, text in enumerate(wrapped_item_title):
            item_title_clip = (
                create_title_clip(
                    text=text,
                    text_color=(255, 0, 0, 255),
                    stroke_color=(255, 255, 255, 255),
                    stroke_width=16,
                    shadow_stroke_width=48,
                )
                .with_start(cumulative_duration)
                .with_position(("center", (240 * index) + 120))
                .with_duration(
                    voice_clips[item_title_key].duration
                    + voice_clips[message_A_key].duration
                    + voice_clips[message_B_key].duration
                )
            )
            clips.append(item_title_clip)
        item_title_clip = item_title_clip.with_audio(voice_clips[item_title_key]).with_start(cumulative_duration)
        cumulative_duration += voice_clips[item_title_key].duration
        clips.append(item_title_clip)

        message_A_clip = (
            create_message_box_clip(
                texts=wrapped_A,
                border_color=(255, 0, 0, 255),
            )
            .with_start(cumulative_duration)
            .with_position((20, 800))
            .with_duration(voice_clips[message_A_key].duration + voice_clips[message_B_key].duration)
        )
        message_A_clip = message_A_clip.with_audio(voice_clips[message_A_key]).with_start(cumulative_duration)
        cumulative_duration += voice_clips[message_A_key].duration
        clips.append(message_A_clip)

        message_B_clip = (
            create_message_box_clip(
                texts=wrapped_B,
                border_color=(0, 0, 255, 255),
            )
            .with_start(cumulative_duration)
            .with_position((20, 1200))
            .with_duration(voice_clips[message_B_key].duration)
        )
        message_B_clip = message_B_clip.with_audio(voice_clips[message_B_key]).with_start(cumulative_duration)
        cumulative_duration += voice_clips[message_B_key].duration
        clips.append(message_B_clip)

    id = uuid.uuid4()
    video_path = f"/tmp/{id}.mp4"
    thumbnail_path = f"/tmp/thumbnail-{id}.png"

    final_clip = CompositeVideoClip(clips)
    final_clip.write_videofile(
        video_path,
        threads=8,
        fps=3,
        codec="libx264",
        audio_codec="aac",
    )
    frame = final_clip.get_frame(0)
    thumbnail = Image.fromarray(frame)
    thumbnail.save(thumbnail_path)
    final_clip.close()
    return video_path, thumbnail_path
