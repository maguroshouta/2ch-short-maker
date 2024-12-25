import MeCab


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
