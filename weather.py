#!/usr/bin/env python3
"""
天气查询 CLI 工具 — 基于 Open-Meteo 免费 API（无需 API Key）
用法:
    python weather.py 北京
    python weather.py "New York"
    python weather.py 东京 --days 3
"""

import argparse
import json
import sys
import urllib.request
import urllib.parse
from datetime import datetime, timedelta, timezone

# ─── 配置 ───────────────────────────────────────────
GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
WEATHER_URL = "https://api.open-meteo.com/v1/forecast"

# 天气代码 → 中文描述 + Emoji
WMO_CODES = {
    0:  ("☀️ 晴天", "clear"),
    1:  ("🌤️ 大部晴朗", "mainly clear"),
    2:  ("⛅ 多云", "partly cloudy"),
    3:  ("☁️ 阴天", "overcast"),
    45: ("🌫️ 雾", "fog"),
    48: ("🌫️ 冻雾", "depositing rime fog"),
    51: ("🌦️ 小毛毛雨", "light drizzle"),
    53: ("🌦️ 毛毛雨", "moderate drizzle"),
    55: ("🌧️ 大毛毛雨", "dense drizzle"),
    56: ("🌧️ 冻毛毛雨", "light freezing drizzle"),
    57: ("🌧️ 冻毛毛雨（大）", "dense freezing drizzle"),
    61: ("🌦️ 小雨", "slight rain"),
    63: ("🌧️ 中雨", "moderate rain"),
    65: ("🌧️ 大雨", "heavy rain"),
    66: ("🌧️ 冻雨（小）", "light freezing rain"),
    67: ("🌧️ 冻雨（大）", "heavy freezing rain"),
    71: ("🌨️ 小雪", "slight snow"),
    73: ("🌨️ 中雪", "moderate snow"),
    75: ("❄️ 大雪", "heavy snow"),
    77: ("🌨️ 雪粒", "snow grains"),
    80: ("🌦️ 阵雨（小）", "slight rain showers"),
    81: ("🌧️ 阵雨", "moderate rain showers"),
    82: ("⛈️ 大阵雨", "violent rain showers"),
    85: ("🌨️ 阵雪（小）", "slight snow showers"),
    86: ("❄️ 阵雪（大）", "heavy snow showers"),
    95: ("⛈️ 雷暴", "thunderstorm"),
    96: ("⛈️ 雷暴+冰雹（小）", "thunderstorm with slight hail"),
    99: ("⛈️ 雷暴+冰雹（大）", "thunderstorm with heavy hail"),
}


def http_get(url: str) -> dict:
    """发送 GET 请求，返回 JSON"""
    req = urllib.request.Request(url, headers={"User-Agent": "WeatherCLI/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.URLError as e:
        print(f"❌ 网络错误: {e.reason}")
        sys.exit(1)
    except json.JSONDecodeError:
        print("❌ 解析服务器响应失败")
        sys.exit(1)


def geocode(city: str) -> list[dict]:
    """根据城市名查询经纬度，返回结果列表"""
    params = urllib.parse.urlencode({
        "name": city,
        "count": 5,
        "language": "zh",
        "format": "json",
    })
    data = http_get(f"{GEOCODING_URL}?{params}")
    results = data.get("results", [])
    if not results:
        print(f"❌ 找不到城市: {city}")
        sys.exit(1)
    return results


def pick_city(results: list[dict]) -> dict:
    """从搜索结果中选取最佳匹配"""
    if len(results) == 1:
        return results[0]

    print("\n🔍 找到多个匹配城市：")
    for i, r in enumerate(results):
        name = r.get("name", "?")
        country = r.get("country", "?")
        admin = r.get("admin1", "")
        region = f"{admin}, {country}" if admin else country
        print(f"  [{i + 1}] {name} — {region} (lat={r['latitude']:.2f}, lon={r['longitude']:.2f})")

    while True:
        try:
            choice = input(f"\n请选择 [1-{len(results)}]（默认 1）: ").strip()
            if choice == "":
                return results[0]
            idx = int(choice) - 1
            if 0 <= idx < len(results):
                return results[idx]
        except ValueError:
            pass
        print(f"⚠️ 请输入 1 到 {len(results)} 之间的数字")


def get_weather(lat: float, lon: float, days: int = 1) -> dict:
    """获取天气预报数据"""
    params = urllib.parse.urlencode({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl",
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
        "forecast_days": max(days, 1),
        "timezone": "auto",
        "language": "zh",
    })
    return http_get(f"{WEATHER_URL}?{params}")


def wind_direction_text(deg: float) -> str:
    """风向角度 → 中文"""
    if deg is None:
        return "未知"
    dirs = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"]
    idx = round(deg / 45) % 8
    return dirs[idx]


def print_divider(char: str = "─", width: int = 50):
    print(char * width)


def display_weather(data: dict, city_name: str, country: str):
    """美化输出天气信息"""
    current = data.get("current", {})
    daily = data.get("daily", {})

    # ── 当前天气 ──
    weather_code = current.get("weather_code", 0)
    weather_desc, _ = WMO_CODES.get(weather_code, ("❓ 未知", "unknown"))
    temp = current.get("temperature_2m", "?")
    feels_like = current.get("apparent_temperature", "?")
    humidity = current.get("relative_humidity_2m", "?")
    wind_speed = current.get("wind_speed_10m", "?")
    wind_dir = current.get("wind_direction_10m", 0)
    pressure = current.get("pressure_msl", "?")

    print()
    print_divider("═")
    print(f"  📍 {city_name}, {country}")
    print(f"  🕐 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print_divider("═")
    print(f"  {weather_desc}")
    print(f"  🌡️  温度: {temp}°C  │  体感: {feels_like}°C")
    print(f"  💧 湿度: {humidity}%  │  🌬️  风速: {wind_speed} km/h ({wind_direction_text(wind_dir)})")
    print(f"  📊 气压: {pressure} hPa")
    print_divider("═")

    # ── 逐日预报 ──
    dates = daily.get("time", [])
    codes = daily.get("weather_code", [])
    highs = daily.get("temperature_2m_max", [])
    lows = daily.get("temperature_2m_min", [])
    precip = daily.get("precipitation_sum", [])
    winds = daily.get("wind_speed_10m_max", [])

    if dates:
        print(f"\n  📅 未来 {len(dates)} 天预报")
        print_divider("─")
        for i, date_str in enumerate(dates):
            code = codes[i] if i < len(codes) else 0
            desc, _ = WMO_CODES.get(code, ("❓", "unknown"))
            hi = highs[i] if i < len(highs) else "?"
            lo = lows[i] if i < len(lows) else "?"
            rain = precip[i] if i < len(precip) else 0
            ws = winds[i] if i < len(winds) else "?"

            # 中文星期
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            weekdays = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
            wd = weekdays[dt.weekday()]
            today = " ⬅ 今天" if dt.date() == datetime.now().date() else ""

            print(f"  {date_str} {wd}{today}")
            print(f"    {desc}  🌡️ {lo}°C ~ {hi}°C  💧 {rain}mm  🌬️ {ws} km/h")
        print_divider("─")

    print()


def main():
    parser = argparse.ArgumentParser(
        description="🌤️  天气查询 CLI — 基于 Open-Meteo 免费 API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  python weather.py 北京
  python weather.py "San Francisco" --days 5
  python weather.py 东京 --no-daily
        """,
    )
    parser.add_argument("city", help="城市名称（中文/英文均可）")
    parser.add_argument("--days", type=int, default=3, help="预报天数（默认 3，最多 16）")
    parser.add_argument("--no-daily", action="store_true", help="不显示逐日预报")
    args = parser.parse_args()

    days = max(1, min(args.days, 16))

    # 1. 地理编码
    print(f"\n🔎 正在搜索: {args.city} ...")
    results = geocode(args.city)
    city = pick_city(results)

    name = city.get("name", args.city)
    country = city.get("country", "未知")
    lat = city["latitude"]
    lon = city["longitude"]

    # 2. 获取天气
    print(f"🌐 正在获取 {name} 的天气数据 ...")
    if args.no_daily:
        days = 1  # 只要当前天气
    data = get_weather(lat, lon, days=days)

    # 3. 展示
    display_weather(data, name, country)


if __name__ == "__main__":
    main()
