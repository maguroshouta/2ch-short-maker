# frontend

NodeJS 22 + NextJS

# 開発

立ち上げに必要なもの

- [pnpm](https://pnpm.io/)
- [docker](https://www.docker.com/)

依存サービス(Postgres/MinIO)の立ち上げ
```
docker compose -f ../compose.yaml up -d
```

.envの作成
```
cp .env.example .env
```

依存関係のインストール
```
pnpm install
```

NextJSの立ち上げ
```
pnpm run dev
```
