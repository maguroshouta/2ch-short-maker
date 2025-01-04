# backend

Python 3.10 + FastAPI

# 開発

立ち上げに必要なもの

- [uv](https://docs.astral.sh/uv/)
- [docker](https://www.docker.com/)
- [OpenAIのAPIキー](https://openai.com/)

開発用コマンド

.envの作成
```
cp .env.example .env
```
OPENAI_API_KEYに自分のAPIキーを入れる


依存関係のインストール
```sh
uv sync
```

postgresとminioの立ち上げ
```
docker compose up -d
```

fastapiの立ち上げ
```
uv run fastapi run dev
```
