# anayama

FastAPI（Python）+ Next.js（TypeScript）+ PostgreSQL を Docker Compose で構築する開発用リポジトリです。

---

## 技術構成

* Frontend: Next.js (TypeScript, App Router)
* Backend: FastAPI (Python)
* Database: PostgreSQL
* Infrastructure: Docker / Docker Compose

---

## 前提条件

以下がインストールされていることを確認してください。

### 必須

* Git
* Docker Desktop

### 任意（ローカル開発用）

* Node.js (18以上)
* Python (3.11以上)

---

## セットアップ手順（Docker）

### 1. リポジトリをクローン

```bash
git clone https://github.com/sora47m0n/anayama.git
cd anayama
```

### 2. Docker コンテナを起動

```bash
docker compose up --build
```

---

## アクセス確認

| サービス               | URL                                                      |
| ------------------ | -------------------------------------------------------- |
| Backend (FastAPI)  | [http://localhost:8000](http://localhost:8000)           |
| API Docs (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs) |
| Frontend (Next.js) | [http://localhost:3000](http://localhost:3000)           |

---

## ディレクトリ構成

```text
anayama/
├─ backend/        # FastAPI
├─ frontend/       # Next.js
├─ docker-compose.yml
└─ README.md
```

---

## 開発ルール（最低限）

* 原則 Docker 経由で起動する
* main ブランチへ直接 push しない
* 機能追加はブランチを切って対応

---

## 補足

* Windows / macOS / WSL いずれでも Docker が動作すれば同一手順で起動可能
* DB のテーブル定義・マイグレーションは後続タスクで対応予定
