from mybot import (
    WeatherAgent,
    HotelAgent,
    FoodAgent,
    ItineraryAgent,
    Orchestrator,
    MockLLMClient,
)


def main():
    print("=" * 60)
    print("🤖 MyBot 多智能体协作旅行规划演示")
    print("=" * 60)

    weather_agent = WeatherAgent()
    hotel_agent = HotelAgent()
    food_agent = FoodAgent()
    itinerary_agent = ItineraryAgent()

    orchestrator = Orchestrator()
    orchestrator.register_agent(weather_agent)
    orchestrator.register_agent(hotel_agent)
    orchestrator.register_agent(food_agent)
    orchestrator.register_agent(itinerary_agent)

    print("\n1️⃣ 自动路由 - 天气查询:")
    result = orchestrator.route("北京明天天气怎么样？", strategy="auto")
    print(f"   路由到: {result['agent']}")
    print(f"   回复: {result['response'][:100]}...")

    print("\n2️⃣ 自动路由 - 美食推荐:")
    result = orchestrator.route("成都有什么必吃的美食？", strategy="auto")
    print(f"   路由到: {result['agent']}")
    print(f"   回复: {result['response'][:100]}...")

    print("\n3️⃣ 广播模式 - 所有Agent回应:")
    result = orchestrator.route("你好！", strategy="broadcast")
    for r in result["results"]:
        print(f"   {r['agent']}: {r['response'][:60]}...")

    print("\n4️⃣ 多Agent协作 - 辩论模式:")
    result = orchestrator.multi_agent_collaboration(
        "去北京旅行最值得体验什么？",
        agent_names=["ItineraryAgent", "FoodAgent"],
        collaboration_mode="debate",
    )
    print("   各方观点:")
    for p in result["perspectives"]:
        print(f"     {p['agent']}: {p['response'][:80]}...")

    print("\n5️⃣ 多Agent协作 - 流水线模式:")
    result = orchestrator.multi_agent_collaboration(
        "帮我规划杭州旅行",
        agent_names=["WeatherAgent", "ItineraryAgent", "FoodAgent"],
        collaboration_mode="pipeline",
    )
    print("   处理流水线:")
    for step in result["steps"]:
        print(f"     {step['agent']}: {step['output'][:80]}...")
    print(f"   最终结果: {result['final_output'][:100]}...")

    print("\n6️⃣ 直接调用专业Agent:")
    weather = weather_agent.get_weather_for_trip("西安", ["2025-10-01", "2025-10-02", "2025-10-03"])
    print("   西安3日天气:")
    for w in weather:
        print(f"     {w}")

    hotel = hotel_agent.recommend_for_trip("西安", budget_per_night=400, style="舒适型")
    print(f"\n   西安推荐酒店: {hotel}")

    must_try = food_agent.get_must_try("西安")
    print(f"\n   西安必吃美食:")
    for r in must_try[:3]:
        print(f"     {r}")

    attractions = itinerary_agent.get_attractions("西安", category="历史")
    print(f"\n   西安历史景点:")
    for a in attractions[:3]:
        print(f"     {a}")


if __name__ == "__main__":
    main()
