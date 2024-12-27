import json
import subprocess
import uuid
from concurrent.futures import ThreadPoolExecutor
from io import BytesIO

import numpy
import requests
from moviepy import (
    AudioFileClip,
    CompositeAudioClip,
    CompositeVideoClip,
    ImageClip,
)
from openai import OpenAI
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from app.core.env import OPENAI_API_KEY
from app.utils import irasutoya_search, wrap_text

openai = OpenAI(
    api_key=OPENAI_API_KEY,
)


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

    img_width = text_width + padding
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


def create_voice_clip(text: str, voice_preset: str):
    id = uuid.uuid4()
    output_path = f"/tmp/{id}.wav"
    generate_aquestalk_voice(text, voice_preset, output_path)
    clip = AudioFileClip(output_path)
    return clip


def create_irasutoya_clip(keyword: str):
    irasutoya_image_url = irasutoya_search(keyword)
    if irasutoya_image_url is None:
        return None
    response = requests.get(irasutoya_image_url)
    img = Image.open(BytesIO(response.content))
    img_array = numpy.array(img)
    clip = ImageClip(img_array)

    _, image_height = img.size

    related_keyword_clip = clip.with_position(("center", 1920 - image_height))
    return related_keyword_clip


def create_voice_clips(voices: list[dict[str, str]]):
    with ThreadPoolExecutor() as executor:
        futures = []
        for voice in voices:
            for key, value in voice.items():
                text = value["text"]
                voice_preset = value["voice_preset"]
                future = executor.submit(create_voice_clip, text, voice_preset)
                futures.append((key, future))

        voice_clips = {}
        for key, future in futures:
            voice_clips[key] = future.result()

    return voice_clips


def create_irasutoya_clips(keywords: list[str]):
    with ThreadPoolExecutor() as executor:
        futures = []
        for keyword in keywords:
            future = executor.submit(create_irasutoya_clip, keyword)
            futures.append(future)

        irasutoya_clips = []
        for future in futures:
            irasutoya_clip = future.result()
            irasutoya_clips.append(irasutoya_clip)

    return irasutoya_clips


def create_2ch_video(prompt: str):
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": "以下の形式を必ず守って回答してください。\n登場人物はAとBが存在します。\n2chのネットオタクのような喋り口調で回答してください。\n「！」「？」は使わないでください。\n優しい語尾は使わないでください。\n\n以下回答形式(5位まで作成)\n{テーマに沿った}\n\n{n位}\nAが{テーマ}について回答(30文字程度)\nBが{テーマ}についてAの回答は無視して回答(25文字程度)",
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
                                    "ranking": {
                                        "type": "integer",
                                        "description": "ランキングの順位",
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
                                "required": ["title", "ranking", "A", "B", "keyword"],
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
    voice_clips_dict = []

    irasutoya_texts.append(keyword)

    voice_clips_dict.append(
        {
            "title": {
                "text": f"{title}あげてけ",
                "voice_preset": "女性２",
            }
        }
    )

    for index, item in enumerate(items):
        item_title = item["title"]
        item_keyword = item["keyword"]
        message_A = item["A"]
        message_B = item["B"]

        item_title_key = f"item_{index}_title"
        message_A_key = f"item_{index}_A"
        message_B_key = f"item_{index}_B"

        irasutoya_texts.append(item_keyword)

        voice_clips_dict.append(
            {
                item_title_key: {
                    "text": item_title,
                    "voice_preset": "女性２",
                },
                message_A_key: {
                    "text": message_A,
                    "voice_preset": "中性",
                },
                message_B_key: {
                    "text": message_B,
                    "voice_preset": "男声２",
                },
            }
        )

    voice_clips = create_voice_clips(voice_clips_dict)
    irasutoya_clips = create_irasutoya_clips(irasutoya_texts)

    total_voice_duration = sum([voice.duration for voice in voice_clips.values()])

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

        item_title_clip = (
            create_title_clip(
                text=item_title,
                text_color=(255, 0, 0, 255),
                stroke_color=(255, 255, 255, 255),
                stroke_width=16,
                shadow_stroke_width=48,
            )
            .with_start(cumulative_duration)
            .with_position(("center", 120))
            .with_duration(
                voice_clips[item_title_key].duration
                + voice_clips[message_A_key].duration
                + voice_clips[message_B_key].duration
            )
        )
        item_title_clip = item_title_clip.with_audio(voice_clips[item_title_key]).with_start(cumulative_duration)
        cumulative_duration += voice_clips[item_title_key].duration
        clips.append(item_title_clip)

        message_A_clip = (
            create_message_box_clip(
                texts=wrapped_A,
                border_color=(255, 0, 0, 255),
            )
            .with_start(cumulative_duration)
            .with_position((20, 400))
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
            .with_position((20, 800))
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
