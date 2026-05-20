#!/usr/bin/env node
/**
 * 天气查询 CLI — 基于 Open-Meteo 免费 API（无需 API Key）
 * 用法:
 *   node weather.js 北京
 *   node weather.js "New York" --days 5
 */

const https = require("https");

// ─── 天气代码映射 ──────────────────────────────────
const WMO_CODES = {
  0: "☀️ 晴天",
  1: "🌤️ 大部晴朗",
  2: "⛅ 多云",
  3: "☁️ 阴天",
  45: "🌫️ 雾",
  48: "🌫️ 冻雾",
  51: "🌦️ 小毛毛雨",
  53: "🌦️ 毛毛雨",
  55: "🌧️ 大毛毛雨",
  56: "🌧️ 冻毛毛雨",
  57: "🌧️ 冻毛毛雨（大）",
  61: "🌦️ 小雨",
  63: "🌧️ 中雨",
  65: "🌧️ 大雨",
  66: "🌧️ 冻雨（小）",
  67: "🌧️ 冻雨（大）",
  71: "🌨️ 小雪",
  73: "🌨️ 中雪",
  75: "❄️ 大雪",
  77: "🌨️ 雪粒",
  80: "🌦️ 阵雨（小）",
  81: "🌧️ 阵雨",
  82: "⛈️ 大阵雨",
  85: "🌨️ 阵雪（小）",
  86: "❄️ 阵雪（大）",
  95: "⛈️ 雷暴",
  96: "⛈️ 雷暴+冰雹（小）",
  99: "⛈️ 雷暴+冰雹（大）",
};

const WINDS = ["北", "东北", "东", "东南", "南", "西南", "西", "西北"];
const WEEKDAYS = ["周日", "周一", "周二", "周三", "周四", "周五", "周六"];

// ─── HTTP 工具 ─────────────────────────────────────
function httpGet(url) {
  return new Promise((resolve, reject) => {
    https
      .get(url, { headers: { "User-Agent": "WeatherCLI/1.0" } }, (res) => {
        let data = "";
        res.on("data", (chunk) => (data += chunk));
        res.on("end", () => {
          try {
            resolve(JSON.parse(data));
          } catch {
            reject(new Error("解析响应失败"));
          }
        });
      })
      .on("error", (e) => reject(new Error(`网络错误: ${e.message}`)));
  });
}

// ─── 地理编码 ──────────────────────────────────────
async function geocode(city) {
  const q = encodeURIComponent(city);
  const url = `https://geocoding-api.open-meteo.com/v1/search?name=${q}&count=5&language=zh&format=json`;
  const data = await httpGet(url);
  if (!data.results || data.results.length === 0) {
    console.error(`❌ 找不到城市: ${city}`);
    process.exit(1);
  }
  return data.results;
}

// ─── 选择城市 ──────────────────────────────────────
function pickCity(results) {
  if (results.length === 1) return results[0];

  console.log("\n🔍 找到多个匹配城市：");
  results.forEach((r, i) => {
    const region = [r.admin1, r.country].filter(Boolean).join(", ");
    console.log(
      `  [${i + 1}] ${r.name} — ${region} (lat=${r.latitude.toFixed(2)}, lon=${r.longitude.toFixed(2)})`
    );
  });

  // 非交互模式选第一个
  if (!process.stdin.isTTY) {
    console.log("  → 自动选择第 1 个");
    return results[0];
  }

  return new Promise((resolve) => {
    const rl = require("readline").createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    rl.question(`\n请选择 [1-${results.length}]（默认 1）: `, (ans) => {
      rl.close();
      const idx = ans.trim() === "" ? 0 : parseInt(ans) - 1;
      resolve(results[idx >= 0 && idx < results.length ? idx : 0]);
    });
  });
}

// ─── 获取天气 ──────────────────────────────────────
async function getWeather(lat, lon, days) {
  const params = new URLSearchParams({
    latitude: lat,
    longitude: lon,
    current:
      "temperature_2m,relative_humidity_2m,apparent_temperature,weather_code,wind_speed_10m,wind_direction_10m,pressure_msl",
    daily:
      "weather_code,temperature_2m_max,temperature_2m_min,precipitation_sum,wind_speed_10m_max",
    forecast_days: Math.max(days, 1),
    timezone: "auto",
  });
  return httpGet(`https://api.open-meteo.com/v1/forecast?${params}`);
}

// ─── 风向转文字 ────────────────────────────────────
function windDir(deg) {
  if (deg == null) return "未知";
  return WINDS[Math.round(deg / 45) % 8];
}

// ─── 分割线 ────────────────────────────────────────
function hr(char = "─", width = 50) {
  console.log(char.repeat(width));
}

// ─── 展示 ──────────────────────────────────────────
function display(data, cityName, country) {
  const cur = data.current || {};
  const daily = data.daily || {};
  const code = cur.weather_code ?? 0;

  console.log();
  hr("═");
  console.log(`  📍 ${cityName}, ${country}`);
  console.log(`  🕐 ${new Date().toLocaleString("zh-CN")}`);
  hr("═");
  console.log(`  ${WMO_CODES[code] || "❓ 未知"}`);
  console.log(
    `  🌡️  温度: ${cur.temperature_2m ?? "?"}°C  │  体感: ${cur.apparent_temperature ?? "?"}°C`
  );
  console.log(
    `  💧 湿度: ${cur.relative_humidity_2m ?? "?"}%  │  🌬️  风速: ${cur.wind_speed_10m ?? "?"} km/h (${windDir(cur.wind_direction_10m)})`
  );
  console.log(`  📊 气压: ${cur.pressure_msl ?? "?"} hPa`);
  hr("═");

  const dates = daily.time || [];
  if (!dates.length) return;

  console.log(`\n  📅 未来 ${dates.length} 天预报`);
  hr("─");
  dates.forEach((dateStr, i) => {
    const desc = WMO_CODES[daily.weather_code?.[i]] || "❓";
    const hi = daily.temperature_2m_max?.[i] ?? "?";
    const lo = daily.temperature_2m_min?.[i] ?? "?";
    const rain = daily.precipitation_sum?.[i] ?? 0;
    const ws = daily.wind_speed_10m_max?.[i] ?? "?";

    const dt = new Date(dateStr + "T00:00:00");
    const wd = WEEKDAYS[dt.getDay()];
    const today = dt.toDateString() === new Date().toDateString() ? " ⬅ 今天" : "";

    console.log(`  ${dateStr} ${wd}${today}`);
    console.log(`    ${desc}  🌡️ ${lo}°C ~ ${hi}°C  💧 ${rain}mm  🌬️ ${ws} km/h`);
  });
  hr("─");
  console.log();
}

// ─── 主函数 ────────────────────────────────────────
async function main() {
  const args = process.argv.slice(2);

  // 解析参数
  let city = "";
  let days = 3;
  let noDaily = false;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === "--days" && args[i + 1]) {
      days = Math.max(1, Math.min(parseInt(args[++i]), 16));
    } else if (args[i] === "--no-daily") {
      noDaily = true;
    } else if (!args[i].startsWith("--")) {
      city = args[i];
    }
  }

  if (!city) {
    console.log("用法: node weather.js <城市名> [--days N] [--no-daily]");
    console.log("示例: node weather.js 北京");
    console.log("      node weather.js Tokyo --days 5");
    process.exit(1);
  }

  // 1. 地理编码
  console.log(`\n🔎 正在搜索: ${city} ...`);
  const results = await geocode(city);
  const picked = await pickCity(results);

  const name = picked.name || city;
  const country = picked.country || "未知";

  // 2. 获取天气
  console.log(`🌐 正在获取 ${name} 的天气数据 ...`);
  const data = await getWeather(picked.latitude, picked.longitude, noDaily ? 1 : days);

  // 3. 展示
  display(data, name, country);
}

main().catch((e) => {
  console.error(`❌ ${e.message}`);
  process.exit(1);
});
