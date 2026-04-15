# Tarot 塔罗牌小程序

AI 驱动的塔罗牌占卜工具，支持智能牌阵推荐和 AI 解读。

- 后端：FastAPI + MiniMax M2.7 AI
- 前端：Taro + React（编译为微信小程序）

## 功能流程

```
用户输入问题 → AI 推荐牌阵（三张牌 / 凯尔特十字）
    ↓
用户确认并抽牌 → AI 生成完整解读
```

## 目录结构

```
tarot/
├── backend/                    # FastAPI 后端
│   └── src/tarot_bkd/
│       ├── api.py            # API 入口
│       ├── spreads.json       # 牌阵定义
│       └── rider_waite_cards.json  # 塔罗牌数据
├── frontend/
│   └── tarot-app/           # Taro 前端
│       └── src/
│           ├── api/          # API 调用
│           └── pages/         # 页面组件
└── README.md
```

## 1. 启动后端

### 1.1 环境准备

```bash
cd backend
pip install fastapi uvicorn pydantic anthropic
```

### 1.2 配置 API Key

在 `backend/` 目录下创建 `.env` 文件：

```bash
# backend/.env
MINIMAX_API_KEY=你的MiniMax API Key
```

### 1.3 启动命令

```bash
cd backend
./start.sh
```

或手动设置环境变量：

```bash
cd backend
source .env  # 加载环境变量
python3 -c "
import sys, pathlib, uvicorn
sys.path.insert(0, 'src')
from tarot_bkd.api import build_app
app = build_app()
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

### 1.4 环境变量

| 变量 | 必填 | 说明 |
|------|------|------|
| `MINIMAX_API_KEY` | 是 | MiniMax API Key，从 platform.minimaxi.com 获取 |

### 1.4 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/health` | GET | 健康检查 |
| `/spreads` | GET | 获取可用牌阵列表 |
| `/recommend-spread` | POST | AI 推荐牌阵（需要 body: `{question: string}`） |
| `/draw` | POST | 抽牌（需要 body: `{id, name, arcana, orientation}`） |
| `/interpret` | POST | AI 解读（需要 body: `{question, spread}`） |

## 2. 启动前端（Taro）

```bash
cd frontend/tarot-app
npm install
npm run build:weapp   # 编译为微信小程序
```

### 2.1 前后端联调

前端 API 地址在 `src/api/tarot_bkd.ts`：

```ts
const BASE_URL = "http://你的服务器IP:8000"
```

- 本地开发：`http://127.0.0.1:8000`
- 手机预览：改为后端所在机器的局域网 IP

## 3. 微信开发者工具

1. 导入项目目录：`frontend/tarot-app`
2. AppID：使用测试号或正式 AppID
3. 详情 → 本地开发：勾选「不校验合法域名、web-view...」

## 4. 部署到云服务器

```bash
# 服务器上
git clone https://github.com/hyoitsugun19970709/tarot-main
cd tarot-main/backend

# 创建 .env 文件（包含你的 API Key）
vi .env
# 添加：MINIMAX_API_KEY=你的Key

# 安装依赖
pip install fastapi uvicorn pydantic anthropic

# 启动（后台运行）
chmod +x start.sh
nohup ./start.sh &

# 开放端口 8000
sudo ufw allow 8000  # 或在云控制台安全组开放
```

## 5. 小程序发布流程

1. 微信开发者工具 → 上传
2. mp.weixin.qq.com → 管理中心 → 版本管理
3. 提交审核 → 体验版 → 正式发布
