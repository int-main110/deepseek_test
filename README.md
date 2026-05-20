# 🌤️ 天气查询工具集

基于 [Open-Meteo](https://open-meteo.com/) 免费 API 的天气查询应用，**无需 API Key**，支持全球城市搜索。

---

## 📁 项目结构

```
e:\test1/
├── web/
│   └── index.html          # Web 网页版（前端 UI）
├── cli/
│   ├── js/
│   │   └── weather.js      # Node.js 命令行版
│   └── python/
│       └── weather.py      # Python 命令行版
└── README.md
```

---

## 🌐 weather.html — Web 网页版

一个精美的天气查询网页，具有 Apple 风格的 UI 设计。

### ✨ 功能亮点

| 功能 | 说明 |
|------|------|
| 🔍 城市搜索 | 支持中文/英文城市名搜索，自动补全"市"后缀 |
| 🌈 动态主题 | 根据天气自动切换背景（晴/多云/雨/雪/雷暴/雾） |
| 📊 当前天气 | 温度、体感温度、湿度、风速、风向、气压、日出日落 |
| 📅 7日预报 | 未来一周的天气趋势，含最高/最低温度、降水量 |
| 💡 智能提示 | 根据天气给出出行建议（带伞、防暑、保暖等） |
| 🎨 浮动光斑 | 背景动态光斑装饰动画 |

### 🚀 使用方法

直接在浏览器中打开 `web/index.html` 即可，默认加载**北京**天气。

### 🛠 技术实现

- **纯前端**：HTML + CSS + JavaScript，无框架依赖
- **API 调用**：通过 `fetch` 调用 Open-Meteo 的 Geocoding API 和 Forecast API
- **城市匹配**：智能排序（按人口降序），中文短词自动尝试加"市"后缀
- **防抖搜索**：输入框 400ms 防抖 + 回车立即搜索
- **主题系统**：6 种天气主题，CSS class 动态切换 + 渐变背景

### 🎯 天气代码映射（WMO Codes）

支持 28 种天气代码的完整映射，包括：
- ☀️ 晴天 / 🌤️ 大部晴朗 / ⛅ 多云 / ☁️ 阴天
- 🌦️ 小雨~大雨 / 🌧️ 毛毛雨~暴雨 / ⛈️ 雷暴
- 🌨️ 小雪~大雪 / ❄️ 阵雪
- 🌫️ 雾 / 冻雾

---

## 📟 weather.js — Node.js CLI 版

基于 Node.js 的命令行天气查询工具。

### 🚀 使用方法

```bash
# 基本查询
node cli/js/weather.js 北京

# 指定预报天数（最多 16 天）
node cli/js/weather.js "New York" --days 5

# 只显示当前天气，不显示预报
node cli/js/weather.js 东京 --no-daily
```

### 📋 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `<城市名>` | 要查询的城市（必填） | — |
| `--days N` | 预报天数（1-16） | 3 |
| `--no-daily` | 不显示逐日预报 | false |

### 📤 输出示例

```
══════════════════════════════════════════════════
  📍 北京, 中国
  🕐 2026/5/20 14:30:00
══════════════════════════════════════════════════
  ☀️ 晴天
  🌡️  温度: 26.5°C  │  体感: 28.2°C
  💧 湿度: 45%  │  🌬️  风速: 12 km/h (南)
  📊 气压: 1013.2 hPa
══════════════════════════════════════════════════

  📅 未来 3 天预报
──────────────────────────────────────────────────
  2026-05-21 周三
    ☀️ 晴天  🌡️ 18°C ~ 30°C  💧 0mm  🌬️ 10 km/h
  ...
```

### 🛠 技术实现

- **核心模块**：仅使用 Node.js 内置 `https` 和 `readline` 模块
- **城市选择**：多个匹配时交互式选择，非 TTY 环境自动选第一个
- **数据展示**：当前天气 + 逐日预报，含中文天气描述、风向等

---

## 🐍 weather.py — Python CLI 版

基于 Python 3 的命令行天气查询工具。

### 🚀 使用方法

```bash
# 基本查询
python cli/python/weather.py 北京

# 指定预报天数
python cli/python/weather.py "San Francisco" --days 5

# 只显示当前天气
python cli/python/weather.py 东京 --no-daily
```

### 📋 参数说明

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `city` | 城市名称（必填，位置参数） | — |
| `--days N` | 预报天数（1-16） | 3 |
| `--no-daily` | 不显示逐日预报 | false |

### 🛠 技术实现

- **核心模块**：仅使用 Python 标准库 `urllib.request`、`argparse`、`json`、`datetime`
- **城市选择**：多个匹配时交互式选择，含输入校验
- **数据展示**：与 JS 版一致的输出格式

---

## 🔗 共同依赖的 API

所有版本均使用 Open-Meteo 的免费 API：

| API | 用途 | 地址 |
|-----|------|------|
| Geocoding API | 城市名 → 经纬度 | `https://geocoding-api.open-meteo.com/v1/search` |
| Forecast API | 获取天气预报 | `https://api.open-meteo.com/v1/forecast` |

### 请求的天气字段

**当前天气（current）**：
- `temperature_2m` — 2米处温度
- `relative_humidity_2m` — 相对湿度
- `apparent_temperature` — 体感温度
- `weather_code` — WMO 天气代码
- `wind_speed_10m` / `wind_direction_10m` — 风速/风向
- `pressure_msl` — 海平面气压

**逐日预报（daily）**：
- `weather_code` — 天气代码
- `temperature_2m_max` / `temperature_2m_min` — 最高/最低温度
- `precipitation_sum` — 降水量
- `wind_speed_10m_max` — 最大风速
- `sunrise` / `sunset` — 日出/日落（仅 Web 版）

---

## 📊 版本对比

| 特性 | HTML 版 | Node.js 版 | Python 版 |
|------|:-------:|:----------:|:---------:|
| 图形界面 | ✅ | ❌ | ❌ |
| 命令行 | ❌ | ✅ | ✅ |
| 动态主题 | ✅ | ❌ | ❌ |
| 智能提示 | ✅ | ❌ | ❌ |
| 7日预报 | ✅ | 可配置 | 可配置 |
| 日出/日落 | ✅ | ❌ | ❌ |
| 智能搜索补全 | ✅ | ❌ | ❌ |
| 防抖搜索 | ✅ | ❌ | ❌ |
| 无外部依赖 | ✅ | ✅ | ✅ |

---

## 📝 许可

本项目仅供学习参考，天气数据来源于 [Open-Meteo](https://open-meteo.com/) 免费 API。
