# 2ch ショートメーカー

ChatGPT (gpt-5-nano)とMoviePyを使用してよくある動画を生成します。  
https://2ch-maker.yakimaguro.com

## 開発環境

開発用の Docker Compose はルートの `compose.yaml` 1つに統一しています。

### 1. 依存サービスを起動

```sh
docker compose up -d
```

起動されるサービス:

- Postgres (`localhost:5432`)
- MinIO (`localhost:9000`)

### 2. バックエンドを起動

```sh
cd backend
cp .env.example .env
uv sync
uv run fastapi run app/main.py --port 8000
```

### 3. フロントエンドを起動

```sh
cd frontend
cp .env.example .env
pnpm install
pnpm run dev
```
