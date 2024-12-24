import json
import subprocess
import uuid

import budoux
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

parser = budoux.load_default_japanese_parser()


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


def create_message_box(text: str, border_color: tuple[int, int, int, int]):
    font = ImageFont.truetype("static/fonts/keifont.ttf", 80)
    text_splited = text.split("\n")

    longest_line = max(text_splited, key=len)

    left, top, right, bottom = font.getbbox(longest_line)
    text_width = right - left
    text_height = bottom - top

    padding = 60

    img_width = text_width + padding
    img_height = text_height * len(text_splited) + padding

    img_size = (img_width, img_height)
    img = Image.new("RGBA", img_size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    draw.rectangle(
        (0, 0, img_size[0], img_size[1]),
        fill=(255, 255, 255),
        outline=border_color,
        width=8,
    )

    for i, line in enumerate(text_splited):
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
    id = uuid.uuid4()
    img = create_title_text(text, text_color, stroke_color, stroke_width, shadow_stroke_width)
    output_path = f"/tmp/{id}.png"
    img.save(output_path)
    clip = ImageClip(output_path)
    return clip


def create_message_box_clip(
    text: str,
    border_color: tuple[int, int, int, int],
):
    id = uuid.uuid4()
    img = create_message_box(text, border_color)
    output_path = f"/tmp/{id}.png"
    img.save(output_path)
    clip = ImageClip(output_path)
    return clip


def create_voice_clip(text: str, voice_preset: str):
    id = uuid.uuid4()
    output_path = f"/tmp/{id}.wav"
    generate_aquestalk_voice(text, voice_preset, output_path)
    clip = AudioFileClip(output_path)
    return clip


def wrap_text(text: str, least_width: int):
    phrases = parser.parse(text)

    lines = [""]
    for phrase in phrases:
        if len(lines) > 0 and len(lines[-1]) >= least_width:
            lines.append("")
        lines[-1] += phrase

    if len(lines) >= 2 and len(lines[-1]) <= 2:
        last_line = lines.pop()
        lines[-1] += last_line

    return lines


def create_2ch_video(prompt: str):
    id = uuid.uuid4()
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
                                "required": ["title", "ranking", "A", "B"],
                                "additionalProperties": False,
                            },
                        },
                    },
                    "required": ["title", "items"],
                    "additionalProperties": False,
                },
            },
        },
    )

    data = json.loads(response.choices[0].message.content)

    title = data["title"]
    items = data["items"]

    title_wrapped = parser.parse(title)

    clips = []
    cumulative_duration = 0

    voice_clips = {}

    title_voice_clip = create_voice_clip(f"{title}あげてけ", "女性２")
    voice_clips["title"] = title_voice_clip

    for index, item in enumerate(items):
        item_title = item["title"]
        message_A = item["A"]
        message_B = item["B"]

        item_title_key = f"item_{index}_title"
        message_A_key = f"item_{index}_A"
        message_B_key = f"item_{index}_B"

        voice_clips[item_title_key] = create_voice_clip(item_title, "女性２")
        voice_clips[message_A_key] = create_voice_clip(message_A, "中性")
        voice_clips[message_B_key] = create_voice_clip(message_B, "男声２")

    total_voice_duration = sum([voice_clip.duration for voice_clip in voice_clips.values()])

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
        if index == len(title_wrapped) - 1:
            ageteke_text_clip = (
                create_title_clip(
                    text="挙げてけｗ",
                    text_color=(255, 255, 255, 255),
                    stroke_color=(0, 0, 0, 255),
                    stroke_width=0,
                    shadow_stroke_width=32,
                )
                .with_position(("center", (index + 1 * 240) + 120))
                .with_duration(voice_clips["title"].duration)
            )
            clips.append(ageteke_text_clip)

    for index, item in enumerate(items):
        item_title = item["title"]
        message_A = item["A"]
        message_B = item["B"]

        wrapped_A = "\n".join(wrap_text(message_A, 5))
        wrapped_B = "\n".join(wrap_text(message_B, 5))

        item_title_key = f"item_{index}_title"
        message_A_key = f"item_{index}_A"
        message_B_key = f"item_{index}_B"

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
                text=wrapped_A,
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
                text=wrapped_B,
                border_color=(0, 0, 255, 255),
            )
            .with_start(cumulative_duration)
            .with_position((20, 1200))
            .with_duration(voice_clips[message_B_key].duration)
        )
        message_B_clip = message_B_clip.with_audio(voice_clips[message_B_key]).with_start(cumulative_duration)
        cumulative_duration += voice_clips[message_B_key].duration
        clips.append(message_B_clip)

    final_clip = CompositeVideoClip(clips)
    final_clip.write_videofile(f"/tmp/{id}.mp4", threads=8, fps=3)
    final_clip.close()
    return id
