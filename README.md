# Tarot

Tarot 抽牌项目，包含：

- 后端：FastAPI（入口在 `backend/src/tarot_bkd/api.py`）
- 前端：Taro + React（路径 `frontend/tarot-app`）

## 目录结构

```text
tarot/
	backend/         # FastAPI 服务
	frontend/
		tarot-app/     # Taro 前端
```

## 1. 启动后端

### 1.1 环境准备

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install -e .
pip install fastapi uvicorn pydantic
```

说明：当前 `backend/pyproject.toml` 的 `dependencies` 为空，所以这里显式安装运行期依赖。

### 1.2 启动命令

方式 A（按当前入口文件直接运行）：

```bash
cd backend
source .venv/bin/activate
python src/tarot_bkd/api.py
```

方式 B（用 uvicorn 的 factory 模式）：

```bash
cd backend
source .venv/bin/activate
uvicorn tarot_bkd.api:build_app --factory --host 127.0.0.1 --port 8000
```

默认监听：`http://127.0.0.1:8000`

### 1.3 快速验证

```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/spreads
```

## 2. 启动前端（Taro）

```bash
cd frontend/tarot-app
npm install
```

常用启动方式：

- H5 本地开发：

```bash
npm run dev:h5
```

- 微信小程序开发：

```bash
npm run dev:weapp
```

## 3. 前后端联调注意事项

前端请求地址定义在：`frontend/tarot-app/src/api/tarot_bkd.ts`

当前是：

```ts
const BASE_URL = "http://192.168.240.1:8000"
```

如果你本机直连后端（后端在本机 8000 端口），可改为：

```ts
const BASE_URL = "http://127.0.0.1:8000"
```

如果是手机/模拟器访问，需要把 `BASE_URL` 改成后端所在机器的局域网 IP，并确保端口可访问。

## 4. 一键启动顺序（建议）

1. 终端 1：启动后端（监听 8000）。
2. 终端 2：启动前端 `npm run dev:h5` 或 `npm run dev:weapp`。
3. 打开前端页面后，先调用 `/health` 检查连通性，再执行抽牌。
