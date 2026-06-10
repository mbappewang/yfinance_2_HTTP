# yfinance_to_golang

基于 FastAPI 和 yfinance 的股票数据 HTTP API 服务。项目目标是把 yfinance 的常用数据能力包装成稳定的 JSON 接口，方便 Go 服务或其他后端系统调用。

## 功能

- 股票代码搜索
- 历史 K 线数据
- 历史元数据
- ISIN 查询
- 分红、拆股、公司行动
- 资本利得
- 历史股本
- 基础信息、快速行情信息
- 新闻列表

## 环境要求

- Python 3.14
- pip

## 本地运行

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

启动后访问：

```text
http://127.0.0.1:8000
```

接口文档：

```text
http://127.0.0.1:8000/docs
```

## 配置

项目使用 `pydantic-settings` 读取 `.env`，支持嵌套环境变量，分隔符为 `__`。

默认配置：

```text
BASE__PORT=8000
BASE__VERSION=v1
BASE__LOG_LEVEL=info
```

`.env` 是本地配置文件，不应提交到仓库。

## API

所有业务接口都挂载在 `/api/v1` 下。

### 搜索

```text
POST /api/v1/search/lookup
```

请求示例：

```json
{
  "query": "Apple",
  "type": "all",
  "count": 25,
  "timeout": 30
}
```

### 股票数据

```text
POST /api/v1/stock/get_isin
POST /api/v1/stock/history
POST /api/v1/stock/get_history_metadata
POST /api/v1/stock/get_dividends
POST /api/v1/stock/get_splits
POST /api/v1/stock/get_actions
POST /api/v1/stock/get_capital_gains
POST /api/v1/stock/get_shares_full
POST /api/v1/stock/get_info
POST /api/v1/stock/get_fast_info
POST /api/v1/stock/get_news
```

历史 K 线请求示例：

```json
{
  "ticker": "AAPL",
  "period": "max",
  "interval": "1d",
  "start": "",
  "end": "",
  "prepost": false,
  "actions": true,
  "auto_adjust": true,
  "back_adjust": false,
  "repair": false,
  "keepna": false,
  "rounding": false,
  "timeout": 10
}
```

新闻请求示例：

```json
{
  "ticker": "AAPL",
  "count": 10,
  "tab": "news"
}
```

## 响应格式

成功响应：

```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

失败响应：

```json
{
  "code": 400,
  "message": "错误信息",
  "data": null
}
```

## Docker

本仓库提供 `Dockerfile`，用于在 CI 中构建镜像。

本地如需运行镜像，可使用：

```bash
docker run --rm -p 8000:8000 ghcr.io/mbappewang/yfinance_to_golang:latest
```

## 自动发布

项目通过 GitHub Actions 自动构建并发布 Docker 镜像到 GitHub Container Registry。

触发条件：

- 推送到 `main`
- 推送 `v*` 标签
- 在 GitHub Actions 页面手动触发

镜像地址：

```text
ghcr.io/mbappewang/yfinance_to_golang
```

常见标签：

```text
latest
main
sha-xxxxxxx
v1.0.0
```

## 目录结构

```text
app/
  api/                 API 路由与异常处理
  core/                配置
  handler/             yfinance 调用封装
  schemas/             通用响应结构
Dockerfile             镜像构建文件
requirements.txt       Python 依赖
```

## 许可证

本项目使用 Apache License 2.0，与 yfinance 使用的 Apache Software License 保持一致。详见 [LICENSE](LICENSE)。

## 注意事项

- yfinance 依赖 Yahoo Finance 数据源，数据可用性和字段结构可能随上游变化。
- 新闻接口返回 yfinance 原始字典结构，字段可能随上游调整。
- `get_capital_gains` 对普通股票可能返回空列表，这是合理结果。
