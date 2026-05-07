from mybot.agent import Agent
from mybot.tool import Tool, ToolParameter, ToolResult
from mybot.travel.models import Attraction


class _SearchAttractionsTool(Tool):
    name = "search_attractions"
    description = "搜索指定城市的景点，可按类别筛选"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="category", type="string", description="景点类别：历史/自然/文化/娱乐", required=False),
    ]

    ATTRACTION_DB = {
        "北京": [
            Attraction(name="故宫博物院", description="世界最大宫殿建筑群，明清两代皇宫",
                       category="历史", rating=4.9, visit_duration="4-5小时", ticket_price=60,
                       best_time="上午8:30", location="东城区景山前街4号"),
            Attraction(name="天安门广场", description="世界最大城市广场，国家象征",
                       category="历史", rating=4.7, visit_duration="1-2小时", ticket_price=0,
                       best_time="清晨看升旗", location="东城区天安门"),
            Attraction(name="颐和园", description="皇家园林，世界文化遗产",
                       category="历史", rating=4.8, visit_duration="3-4小时", ticket_price=30,
                       best_time="上午", location="海淀区新建宫门路"),
            Attraction(name="八达岭长城", description="万里长城最著名段",
                       category="历史", rating=4.8, visit_duration="4-5小时", ticket_price=40,
                       best_time="上午早出发", location="延庆区"),
            Attraction(name="天坛公园", description="明清祭天圣地，回音壁奇妙",
                       category="文化", rating=4.6, visit_duration="2-3小时", ticket_price=15,
                       best_time="上午", location="东城区天坛东路"),
            Attraction(name="南锣鼓巷", description="老北京胡同文化体验",
                       category="文化", rating=4.2, visit_duration="2小时", ticket_price=0,
                       best_time="下午", location="东城区南锣鼓巷"),
            Attraction(name="798艺术区", description="当代艺术聚集地",
                       category="文化", rating=4.3, visit_duration="3小时", ticket_price=0,
                       best_time="下午", location="朝阳区酒仙桥"),
        ],
        "上海": [
            Attraction(name="外滩", description="万国建筑博览群，浦江夜景绝佳",
                       category="历史", rating=4.8, visit_duration="2小时", ticket_price=0,
                       best_time="傍晚看夜景", location="黄浦区中山东一路"),
            Attraction(name="东方明珠", description="上海地标，俯瞰全城",
                       category="娱乐", rating=4.5, visit_duration="2-3小时", ticket_price=199,
                       best_time="傍晚", location="浦东新区世纪大道"),
            Attraction(name="豫园", description="江南古典园林，城隍庙小吃",
                       category="历史", rating=4.4, visit_duration="2-3小时", ticket_price=40,
                       best_time="上午", location="黄浦区安仁街"),
            Attraction(name="田子坊", description="文艺小巷，创意小店聚集",
                       category="文化", rating=4.2, visit_duration="2小时", ticket_price=0,
                       best_time="下午", location="黄浦区泰康路"),
            Attraction(name="上海迪士尼", description="梦幻乐园，亲子首选",
                       category="娱乐", rating=4.6, visit_duration="全天", ticket_price=475,
                       best_time="工作日人少", location="浦东新区川沙"),
        ],
        "成都": [
            Attraction(name="大熊猫繁育研究基地", description="近距离观赏国宝大熊猫",
                       category="自然", rating=4.8, visit_duration="3-4小时", ticket_price=55,
                       best_time="上午9点前", location="成华区外北熊猫大道"),
            Attraction(name="宽窄巷子", description="清代古街，成都慢生活代表",
                       category="文化", rating=4.4, visit_duration="2-3小时", ticket_price=0,
                       best_time="下午", location="青羊区宽窄巷子"),
            Attraction(name="武侯祠", description="三国文化圣地，诸葛亮祠堂",
                       category="历史", rating=4.5, visit_duration="2-3小时", ticket_price=50,
                       best_time="上午", location="武侯区武侯祠大街"),
            Attraction(name="锦里古街", description="西蜀第一街，小吃手工艺品",
                       category="文化", rating=4.3, visit_duration="2小时", ticket_price=0,
                       best_time="晚上", location="武侯区锦里"),
            Attraction(name="都江堰", description="世界文化遗产，古代水利工程奇迹",
                       category="历史", rating=4.7, visit_duration="4-5小时", ticket_price=80,
                       best_time="上午", location="都江堰市"),
        ],
        "西安": [
            Attraction(name="秦始皇兵马俑", description="世界第八大奇迹",
                       category="历史", rating=4.9, visit_duration="4-5小时", ticket_price=120,
                       best_time="上午早出发", location="临潼区"),
            Attraction(name="大雁塔", description="唐代佛塔，玄奘藏经处",
                       category="历史", rating=4.6, visit_duration="2小时", ticket_price=40,
                       best_time="傍晚看喷泉", location="雁塔区"),
            Attraction(name="回民街", description="西安美食天堂",
                       category="文化", rating=4.3, visit_duration="2-3小时", ticket_price=0,
                       best_time="傍晚", location="莲湖区"),
            Attraction(name="华清宫", description="唐代皇家温泉行宫",
                       category="历史", rating=4.5, visit_duration="3小时", ticket_price=120,
                       best_time="上午", location="临潼区"),
            Attraction(name="古城墙", description="中国最完整古城墙，可骑行",
                       category="历史", rating=4.7, visit_duration="2-3小时", ticket_price=54,
                       best_time="傍晚骑行", location="市中心"),
        ],
        "杭州": [
            Attraction(name="西湖", description="人间天堂，世界文化遗产",
                       category="自然", rating=4.9, visit_duration="半天", ticket_price=0,
                       best_time="清晨或傍晚", location="西湖区"),
            Attraction(name="灵隐寺", description="千年古刹，杭州最著名寺庙",
                       category="文化", rating=4.6, visit_duration="2-3小时", ticket_price=75,
                       best_time="上午", location="西湖区灵隐路"),
            Attraction(name="河坊街", description="南宋御街，杭州小吃聚集地",
                       category="文化", rating=4.2, visit_duration="2小时", ticket_price=0,
                       best_time="下午", location="上城区"),
            Attraction(name="西溪湿地", description="城市湿地公园，非诚勿扰取景地",
                       category="自然", rating=4.5, visit_duration="4小时", ticket_price=80,
                       best_time="上午", location="西湖区"),
            Attraction(name="龙井村", description="龙井茶产地，品茶赏景",
                       category="自然", rating=4.4, visit_duration="2-3小时", ticket_price=0,
                       best_time="上午", location="西湖区龙井路"),
        ],
        "三亚": [
            Attraction(name="亚龙湾", description="天下第一湾，碧海白沙",
                       category="自然", rating=4.8, visit_duration="全天", ticket_price=0,
                       best_time="上午", location="吉阳区亚龙湾"),
            Attraction(name="蜈支洲岛", description="中国的马尔代夫，潜水天堂",
                       category="自然", rating=4.7, visit_duration="全天", ticket_price=144,
                       best_time="上午早出发", location="海棠区"),
            Attraction(name="天涯海角", description="浪漫地标，海角天涯",
                       category="自然", rating=4.3, visit_duration="2-3小时", ticket_price=81,
                       best_time="下午", location="天涯区"),
            Attraction(name="南山文化旅游区", description="108米海上观音像",
                       category="文化", rating=4.5, visit_duration="3-4小时", ticket_price=129,
                       best_time="上午", location="崖州区"),
            Attraction(name="第一市场夜市", description="海鲜夜市，三亚烟火气",
                       category="文化", rating=4.2, visit_duration="2小时", ticket_price=0,
                       best_time="晚上", location="天涯区"),
        ],
    }

    def execute(self, city: str, category: str = "") -> ToolResult:
        attractions = self.ATTRACTION_DB.get(city, [])
        if not attractions:
            return ToolResult(success=True, data=[])

        if category:
            filtered = [a for a in attractions if category in a.category]
        else:
            filtered = attractions

        return ToolResult(success=True, data=[a.to_dict() for a in filtered])


class _PlanDayRouteTool(Tool):
    name = "plan_day_route"
    description = "规划一天景点游览路线，考虑时间和距离"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="day_theme", type="string", description="当天主题，如历史文化/自然风光"),
        ToolParameter(name="max_attractions", type="integer", description="最多安排景点数", required=False),
    ]

    def execute(self, city: str, day_theme: str, max_attractions: int = 3) -> ToolResult:
        search_tool = _SearchAttractionsTool()
        category = ""
        if "历史" in day_theme:
            category = "历史"
        elif "自然" in day_theme or "风光" in day_theme:
            category = "自然"
        elif "文化" in day_theme or "文艺" in day_theme:
            category = "文化"
        elif "娱乐" in day_theme or "休闲" in day_theme:
            category = "娱乐"

        result = search_tool.execute(city=city, category=category)
        if not result.success or not result.data:
            result = search_tool.execute(city=city)

        attractions = result.data[:max_attractions]
        return ToolResult(success=True, data=attractions)


class ItineraryAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="ItineraryAgent",
            description="行程规划助手，规划每日景点游览路线",
            system_prompt=(
                "你是旅行行程规划助手。根据用户的目的地、天数和偏好，"
                "使用 search_attractions 搜索景点，用 plan_day_route 规划每日路线。"
                "用中文回复，合理安排时间。"
            ),
            **kwargs,
        )
        self.register_tool(_SearchAttractionsTool())
        self.register_tool(_PlanDayRouteTool())

    def get_attractions(self, city: str, category: str = "") -> list:
        result = self.tool_registry.execute("search_attractions", city=city, category=category)
        if result.success and result.data:
            return [Attraction(**a) for a in result.data]
        return []

    def plan_day(self, city: str, day_theme: str, max_attractions: int = 3) -> list:
        result = self.tool_registry.execute(
            "plan_day_route", city=city, day_theme=day_theme, max_attractions=max_attractions
        )
        if result.success and result.data:
            return [Attraction(**a) for a in result.data]
        return []
