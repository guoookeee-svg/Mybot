from mybot.agent import Agent
from mybot.tool import Tool, ToolParameter, ToolResult
from mybot.travel.models import Restaurant


class _SearchRestaurantsTool(Tool):
    name = "search_restaurants"
    description = "搜索指定城市的美食餐厅，可按菜系筛选"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
        ToolParameter(name="cuisine", type="string", description="菜系类型，如川菜、粤菜、本地菜", required=False),
        ToolParameter(name="must_try", type="boolean", description="是否只看必吃餐厅", required=False),
    ]

    RESTAURANT_DB = {
        "北京": [
            Restaurant(name="全聚德烤鸭店(前门店)", cuisine="北京烤鸭", rating=4.3, avg_price=180,
                       signature_dish="果木烤鸭", location="前门大街", must_try=True),
            Restaurant(name="四季民福烤鸭(故宫店)", cuisine="北京烤鸭", rating=4.6, avg_price=160,
                       signature_dish="酥香烤鸭", location="南池子大街", must_try=True),
            Restaurant(name="护国寺小吃", cuisine="北京小吃", rating=4.1, avg_price=50,
                       signature_dish="豆汁焦圈", location="护国寺街", must_try=True),
            Restaurant(name="东来顺饭庄", cuisine="涮羊肉", rating=4.2, avg_price=150,
                       signature_dish="手切鲜羊肉", location="王府井", must_try=False),
            Restaurant(name="局气", cuisine="京菜", rating=4.4, avg_price=120,
                       signature_dish="蜂窝煤炒饭", location="多家分店", must_try=False),
        ],
        "上海": [
            Restaurant(name="南翔馒头店", cuisine="上海小吃", rating=4.2, avg_price=40,
                       signature_dish="南翔小笼包", location="城隍庙", must_try=True),
            Restaurant(name="上海老饭店", cuisine="本帮菜", rating=4.3, avg_price=150,
                       signature_dish="红烧肉", location="福佑路", must_try=True),
            Restaurant(name="鼎泰丰(环贸店)", cuisine="台湾小笼", rating=4.5, avg_price=130,
                       signature_dish="蟹粉小笼", location="南京西路", must_try=False),
            Restaurant(name="小杨生煎", cuisine="上海小吃", rating=4.0, avg_price=30,
                       signature_dish="生煎馒头", location="多家分店", must_try=True),
        ],
        "成都": [
            Restaurant(name="大龙燚火锅", cuisine="川味火锅", rating=4.5, avg_price=110,
                       signature_dish="牛油红锅", location="玉林路", must_try=True),
            Restaurant(name="陈麻婆豆腐", cuisine="川菜", rating=4.3, avg_price=70,
                       signature_dish="麻婆豆腐", location="青华路", must_try=True),
            Restaurant(name="马路边边麻辣烫", cuisine="川味小吃", rating=4.1, avg_price=50,
                       signature_dish="冒脑花", location="多家分店", must_try=False),
            Restaurant(name="小龙坎火锅", cuisine="川味火锅", rating=4.4, avg_price=100,
                       signature_dish="鲜毛肚", location="春熙路", must_try=False),
            Restaurant(name="甘食记肥肠粉", cuisine="成都小吃", rating=4.0, avg_price=25,
                       signature_dish="肥肠粉", location="宽窄巷子", must_try=True),
        ],
        "西安": [
            Restaurant(name="老孙家泡馍", cuisine="西安小吃", rating=4.2, avg_price=45,
                       signature_dish="羊肉泡馍", location="东大街", must_try=True),
            Restaurant(name="贾三灌汤包", cuisine="西安小吃", rating=4.1, avg_price=35,
                       signature_dish="灌汤包", location="回民街", must_try=True),
            Restaurant(name="子午路张记肉夹馍", cuisine="西安小吃", rating=4.4, avg_price=20,
                       signature_dish="腊汁肉夹馍", location="子午路", must_try=True),
            Restaurant(name="长安大牌档", cuisine="陕菜", rating=4.3, avg_price=90,
                       signature_dish="葫芦鸡", location="小寨", must_try=False),
        ],
        "杭州": [
            Restaurant(name="楼外楼", cuisine="杭帮菜", rating=4.4, avg_price=160,
                       signature_dish="西湖醋鱼", location="孤山路", must_try=True),
            Restaurant(name="知味观", cuisine="杭帮菜", rating=4.2, avg_price=100,
                       signature_dish="东坡肉", location="仁和路", must_try=True),
            Restaurant(name="新白鹿餐厅", cuisine="杭帮菜", rating=4.3, avg_price=80,
                       signature_dish="蛋黄子排", location="多家分店", must_try=False),
            Restaurant(name="外婆家", cuisine="杭帮菜", rating=4.1, avg_price=70,
                       signature_dish="麻婆豆腐", location="多家分店", must_try=False),
        ],
        "三亚": [
            Restaurant(name="第一市场海鲜加工", cuisine="海鲜", rating=4.2, avg_price=150,
                       signature_dish="清蒸石斑鱼", location="第一市场", must_try=True),
            Restaurant(name="阿浪海鲜", cuisine="海鲜", rating=4.4, avg_price=130,
                       signature_dish="椒盐皮皮虾", location="三亚湾", must_try=True),
            Restaurant(name="抱罗粉店", cuisine="海南小吃", rating=4.0, avg_price=20,
                       signature_dish="抱罗粉", location="解放路", must_try=True),
            Restaurant(name="清补凉摊", cuisine="海南甜品", rating=4.3, avg_price=15,
                       signature_dish="清补凉", location="各大夜市", must_try=True),
        ],
    }

    def execute(self, city: str, cuisine: str = "", must_try: bool = False) -> ToolResult:
        restaurants = self.RESTAURANT_DB.get(city, [])
        if not restaurants:
            return ToolResult(success=True, data=[])

        filtered = restaurants
        if cuisine:
            filtered = [r for r in filtered if cuisine in r.cuisine]
        if must_try:
            filtered = [r for r in filtered if r.must_try]

        return ToolResult(success=True, data=[r.to_dict() for r in filtered])


class _GetMustTryFoodTool(Tool):
    name = "get_must_try_food"
    description = "获取指定城市的必吃美食清单"
    parameters = [
        ToolParameter(name="city", type="string", description="城市名称"),
    ]

    def execute(self, city: str) -> ToolResult:
        search_tool = _SearchRestaurantsTool()
        result = search_tool.execute(city=city, must_try=True)
        if not result.success:
            return result

        must_try = [r for r in result.data if r.get("must_try")]
        return ToolResult(success=True, data=must_try)


class FoodAgent(Agent):
    def __init__(self, **kwargs):
        super().__init__(
            name="FoodAgent",
            description="美食推荐助手，推荐当地特色美食和必吃餐厅",
            system_prompt=(
                "你是旅行美食助手。根据用户的目的地，"
                "使用 search_restaurants 搜索餐厅，用 get_must_try_food 获取必吃清单。"
                "用中文回复，热情推荐当地美食。"
            ),
            **kwargs,
        )
        self.register_tool(_SearchRestaurantsTool())
        self.register_tool(_GetMustTryFoodTool())

    def get_restaurants_for_trip(self, city: str) -> list:
        result = self.tool_registry.execute("search_restaurants", city=city)
        if result.success and result.data:
            return [Restaurant(**r) for r in result.data]
        return []

    def get_must_try(self, city: str) -> list:
        result = self.tool_registry.execute("get_must_try_food", city=city)
        if result.success and result.data:
            return [Restaurant(**r) for r in result.data]
        return []
