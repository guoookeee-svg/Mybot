from mybot.agent import Agent
from mybot.tool import Tool, ToolParameter, ToolResult
from mybot.travel.models import WeatherInfo


class _GetWeatherTool(Tool):
    name = "get_weather"
    description = "获取指定城市和日期的天气预报信息"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="date", type="string", description="日期，格式YYYY-MM-DD"),
    ]

    WEATHER_DB = {
        "北京": [
            {"condition": "晴", "temp_high": 28, "temp_low": 18, "humidity": 35, "wind": "北风2级"},
            {"condition": "多云", "temp_high": 26, "temp_low": 17, "humidity": 50, "wind": "东风1级"},
            {"condition": "晴转多云", "temp_high": 27, "temp_low": 19, "humidity": 40, "wind": "微风"},
        ],
        "上海": [
            {"condition": "多云", "temp_high": 30, "temp_low": 24, "humidity": 75, "wind": "东南风3级"},
            {"condition": "小雨", "temp_high": 28, "temp_low": 23, "humidity": 85, "wind": "东风2级"},
            {"condition": "阴转晴", "temp_high": 29, "temp_low": 23, "humidity": 65, "wind": "南风2级"},
        ],
        "成都": [
            {"condition": "阴", "temp_high": 25, "temp_low": 19, "humidity": 80, "wind": "微风"},
            {"condition": "小雨", "temp_high": 23, "temp_low": 18, "humidity": 90, "wind": "北风1级"},
            {"condition": "多云", "temp_high": 26, "temp_low": 20, "humidity": 70, "wind": "微风"},
        ],
        "西安": [
            {"condition": "晴", "temp_high": 32, "temp_low": 20, "humidity": 30, "wind": "西风2级"},
            {"condition": "晴", "temp_high": 33, "temp_low": 21, "humidity": 25, "wind": "微风"},
            {"condition": "多云", "temp_high": 30, "temp_low": 19, "humidity": 45, "wind": "东风1级"},
        ],
        "杭州": [
            {"condition": "小雨", "temp_high": 27, "temp_low": 22, "humidity": 85, "wind": "东南风2级"},
            {"condition": "阴", "temp_high": 28, "temp_low": 22, "humidity": 75, "wind": "东风1级"},
            {"condition": "多云转晴", "temp_high": 29, "temp_low": 21, "humidity": 60, "wind": "南风2级"},
        ],
        "三亚": [
            {"condition": "晴", "temp_high": 33, "temp_low": 26, "humidity": 70, "wind": "东南风3级"},
            {"condition": "晴", "temp_high": 34, "temp_low": 27, "humidity": 65, "wind": "南风2级"},
            {"condition": "多云", "temp_high": 32, "temp_low": 26, "humidity": 75, "wind": "东风3级"},
        ],
    }

    def execute(self, city: str, date: str) -> ToolResult:
        city_data = self.WEATHER_DB.get(city)
        if not city_data:
            return ToolResult(
                success=True,
                data=WeatherInfo(
                    location=city, date=date,
                    temperature_high=25, temperature_low=18,
                    condition="多云", humidity=60, wind="微风"
                ).to_dict(),
            )

        day_index = 0
        try:
            from datetime import datetime
            day_index = (datetime.strptime(date, "%Y-%m-%d").day - 1) % len(city_data)
        except ValueError:
            day_index = 0

        info = city_data[day_index]
        weather = WeatherInfo(
            location=city, date=date,
            temperature_high=info["temp_high"],
            temperature_low=info["temp_low"],
            condition=info["condition"],
            humidity=info["humidity"],
            wind=info["wind"],
        )
        return ToolResult(success=True, data=weather.to_dict())


class _GetPackingAdviceTool(Tool):
    name = "get_packing_advice"
    description = "根据天气和旅行风格获取行李打包建议"
    parameters = [
        ToolParameter(name="condition", type="string", description="天气状况"),
        ToolParameter(name="temp_low", type="number", description="最低温度"),
        ToolParameter(name="style", type="string", description="旅行风格"),
    ]

    def execute(self, condition: str, temp_low: float, style: str) -> ToolResult:
        items = ["身份证/护照", "手机充电器", "充电宝"]

        if temp_low < 15:
            items.extend(["厚外套", "保暖内衣", "围巾手套"])
        elif temp_low < 22:
            items.extend(["薄外套", "长裤", "薄毛衣"])
        else:
            items.extend(["短袖", "薄裤", "防晒霜"])

        if "雨" in condition:
            items.extend(["雨伞", "防水鞋"])
        if "探险" in style:
            items.extend(["运动鞋", "双肩包", "手电筒"])
        if "豪华" in style:
            items.extend(["正装/礼服", "精致配饰"])

        return ToolResult(success=True, data={"packing_list": items})


class WeatherAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="WeatherAgent",
            description="天气查询助手，提供天气预报和出行建议",
            system_prompt=(
                "你是旅行天气助手。当用户询问旅行目的地天气时，"
                "使用 get_weather 工具获取天气数据，"
                "然后给出穿衣建议和出行提醒。"
                "用中文回复，语气友好。"
            ),
            **kwargs,
        )
        self.register_tool(_GetWeatherTool())
        self.register_tool(_GetPackingAdviceTool())

    def get_weather_for_trip(self, city: str, dates: list) -> list:
        results = []
        for date in dates:
            tool_result = self.tool_registry.execute("get_weather", city=city, date=date)
            if tool_result.success:
                data = tool_result.data
                results.append(WeatherInfo(
                    location=data["location"],
                    date=data["date"],
                    temperature_high=data["temperature_high"],
                    temperature_low=data["temperature_low"],
                    condition=data["condition"],
                    humidity=data["humidity"],
                    wind=data["wind"],
                ))
        return results
