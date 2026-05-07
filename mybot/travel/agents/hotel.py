from mybot.agent import Agent
from mybot.tool import Tool, ToolParameter, ToolResult
from mybot.travel.models import Hotel


class _SearchHotelsTool(Tool):
    name = "search_hotels"
    description = "搜索指定城市的酒店，可按类型和价格筛选"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="hotel_type", type="string", description="酒店类型：经济型/舒适型/豪华型", required=False),
        ToolParameter(name="max_price", type="number", description="最高每晚价格", required=False),
    ]

    HOTEL_DB = {
        "北京": [
            Hotel(name="北京王府井希尔顿", hotel_type="豪华型", rating=4.7, price_per_night=1200,
                  location="王府井大街", amenities=["健身房", "游泳池", "商务中心", "免费WiFi"],
                  highlights="步行可达故宫天安门"),
            Hotel(name="北京前门建国饭店", hotel_type="舒适型", rating=4.3, price_per_night=480,
                  location="前门大街", amenities=["免费WiFi", "早餐", "停车场"],
                  highlights="老北京风情，近天坛"),
            Hotel(name="如家酒店(北京站店)", hotel_type="经济型", rating=3.8, price_per_night=220,
                  location="北京站附近", amenities=["免费WiFi", "24小时热水"],
                  highlights="交通便利，性价比高"),
        ],
        "上海": [
            Hotel(name="上海外滩华尔道夫", hotel_type="豪华型", rating=4.8, price_per_night=1800,
                  location="外滩", amenities=["江景房", "SPA", "米其林餐厅", "免费WiFi"],
                  highlights="外滩绝美江景，顶级享受"),
            Hotel(name="上海南京路全季酒店", hotel_type="舒适型", rating=4.2, price_per_night=420,
                  location="南京路步行街", amenities=["免费WiFi", "早餐", "健身房"],
                  highlights="南京路核心位置"),
            Hotel(name="汉庭酒店(人民广场店)", hotel_type="经济型", rating=3.9, price_per_night=250,
                  location="人民广场", amenities=["免费WiFi", "24小时热水"],
                  highlights="地铁直达，出行方便"),
        ],
        "成都": [
            Hotel(name="成都瑞吉酒店", hotel_type="豪华型", rating=4.6, price_per_night=1100,
                  location="春熙路", amenities=["SPA", "室内泳池", "川菜餐厅", "免费WiFi"],
                  highlights="春熙路商圈，尽享成都繁华"),
            Hotel(name="成都太古里亚朵酒店", hotel_type="舒适型", rating=4.4, price_per_night=380,
                  location="太古里", amenities=["免费WiFi", "早餐", "书吧"],
                  highlights="紧邻太古里，文艺范十足"),
            Hotel(name="7天酒店(宽窄巷子店)", hotel_type="经济型", rating=3.7, price_per_night=160,
                  location="宽窄巷子", amenities=["免费WiFi", "24小时热水"],
                  highlights="步行可达宽窄巷子"),
        ],
        "西安": [
            Hotel(name="西安威斯汀酒店", hotel_type="豪华型", rating=4.5, price_per_night=900,
                  location="大雁塔", amenities=["健身房", "泳池", "唐风餐厅", "免费WiFi"],
                  highlights="大雁塔景观房，唐风体验"),
            Hotel(name="西安钟楼亚朵酒店", hotel_type="舒适型", rating=4.3, price_per_night=350,
                  location="钟楼", amenities=["免费WiFi", "早餐", "书吧"],
                  highlights="钟楼回民街步行5分钟"),
            Hotel(name="如家酒店(钟楼店)", hotel_type="经济型", rating=3.8, price_per_night=180,
                  location="钟楼附近", amenities=["免费WiFi", "24小时热水"],
                  highlights="市中心位置，出行便利"),
        ],
        "杭州": [
            Hotel(name="杭州西湖国宾馆", hotel_type="豪华型", rating=4.9, price_per_night=2000,
                  location="西湖边", amenities=["湖景房", "私家园林", "杭帮菜", "免费WiFi"],
                  highlights="西湖畔私家园林，极致江南体验"),
            Hotel(name="杭州西湖全季酒店", hotel_type="舒适型", rating=4.3, price_per_night=450,
                  location="西湖大道", amenities=["免费WiFi", "早餐", "茶室"],
                  highlights="步行10分钟到西湖"),
            Hotel(name="汉庭酒店(西湖店)", hotel_type="经济型", rating=3.9, price_per_night=230,
                  location="西湖附近", amenities=["免费WiFi", "24小时热水"],
                  highlights="近西湖，性价比高"),
        ],
        "三亚": [
            Hotel(name="三亚亚特兰蒂斯", hotel_type="豪华型", rating=4.8, price_per_night=2500,
                  location="海棠湾", amenities=["水上乐园", "水族馆", "私人沙滩", "免费WiFi"],
                  highlights="顶级度假体验，水世界畅玩"),
            Hotel(name="三亚湾红树林度假酒店", hotel_type="舒适型", rating=4.4, price_per_night=600,
                  location="三亚湾", amenities=["泳池", "私人沙滩", "免费WiFi", "早餐"],
                  highlights="三亚湾椰梦长廊"),
            Hotel(name="三亚湾家庭公寓", hotel_type="经济型", rating=4.0, price_per_night=200,
                  location="三亚湾", amenities=["厨房", "免费WiFi", "洗衣机"],
                  highlights="家庭出行首选，可做饭"),
        ],
    }

    def execute(self, city: str, hotel_type: str = "", max_price: float = 0) -> ToolResult:
        hotels = self.HOTEL_DB.get(city, [])
        if not hotels:
            return ToolResult(success=True, data=[])

        filtered = hotels
        if hotel_type:
            filtered = [h for h in filtered if h.hotel_type == hotel_type]
        if max_price > 0:
            filtered = [h for h in filtered if h.price_per_night <= max_price]

        return ToolResult(success=True, data=[h.to_dict() for h in filtered])


class _RecommendHotelTool(Tool):
    name = "recommend_hotel"
    description = "根据预算和偏好推荐最佳酒店"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="budget_per_night", type="number", description="每晚预算"),
        ToolParameter(name="style", type="string", description="旅行风格"),
    ]

    def execute(self, city: str, budget_per_night: float, style: str = "") -> ToolResult:
        search_tool = _SearchHotelsTool()
        result = search_tool.execute(city=city, max_price=budget_per_night)
        if not result.success or not result.data:
            result = search_tool.execute(city=city)
            if not result.data:
                return ToolResult(success=False, error=f"未找到{city}的酒店")

        hotels = [Hotel(**h) for h in result.data]
        hotels.sort(key=lambda h: h.rating, reverse=True)

        if "豪华" in style:
            luxury = [h for h in hotels if h.hotel_type == "豪华型"]
            if luxury:
                best = luxury[0]
            else:
                best = hotels[0]
        elif "经济" in style:
            budget = [h for h in hotels if h.hotel_type == "经济型"]
            if budget:
                best = budget[0]
            else:
                best = hotels[-1]
        else:
            best = hotels[0]

        return ToolResult(success=True, data=best.to_dict())


class HotelAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="HotelAgent",
            description="酒店推荐助手，根据预算和偏好推荐住宿",
            system_prompt=(
                "你是旅行住宿助手。根据用户的预算和偏好，"
                "使用 search_hotels 搜索酒店，用 recommend_hotel 推荐最佳选择。"
                "用中文回复，给出推荐理由。"
            ),
            **kwargs,
        )
        self.register_tool(_SearchHotelsTool())
        self.register_tool(_RecommendHotelTool())

    def recommend_for_trip(self, city: str, budget_per_night: float, style: str = "") -> Hotel:
        result = self.tool_registry.execute(
            "recommend_hotel", city=city, budget_per_night=budget_per_night, style=style
        )
        if result.success and result.data:
            return Hotel(**result.data)
        return Hotel(
            name=f"{city}推荐酒店", hotel_type="舒适型",
            rating=4.0, price_per_night=budget_per_night,
            location=f"{city}市中心", amenities=["免费WiFi", "早餐"],
            highlights="位置便利",
        )
