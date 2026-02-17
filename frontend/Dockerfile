FROM node:20-slim

WORKDIR /app

# package.jsonなどをコピー
COPY package.json package-lock.json* ./

# 依存関係をインストール
RUN if [ -f package.json ]; then npm install; fi

# サーバー起動
CMD ["npm", "run", "dev", "--", "--host"]
