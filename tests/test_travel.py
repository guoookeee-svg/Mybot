import pytest
from mybot.travel.models import (
    TravelPlan,
    DayItinerary,
    Attraction,
    Restaurant,
    Hotel,
    WeatherInfo,
    TravelPreference,
    TravelStyle,
)
from mybot.travel.planner import TravelPlanner
from mybot.travel.agents.weather import WeatherAgent
from mybot.travel.agents.hotel import HotelAgent
from mybot.travel.agents.food import FoodAgent
from mybot.travel.agents.itinerary import ItineraryAgent


class TestTravelModels:
    def test_travel_preference_days(self):
        pref = TravelPreference(
            destination="北京", start_date="2025-10-01", end_date="2025-10-03",
            budget=3000,
        )
        assert pref.num_days == 3

    def test_travel_preference_daily_budget(self):
        pref = TravelPreference(
            destination="北京", start_date="2025-10-01", end_date="2025-10-03",
            budget=3000,
        )
        assert pref.daily_budget == 1000.0

    def test_weather_info_str(self):
        w = WeatherInfo(
            location="北京", date="2025-10-01",
            temperature_high=28, temperature_low=18,
            condition="晴", humidity=35, wind="北风2级",
        )
        assert "北京" in str(w)
        assert "晴" in str(w)

    def test_attraction_str(self):
        a = Attraction(
            name="故宫", description="皇宫", category="历史",
            rating=4.9, visit_duration="4小时", ticket_price=60,
            best_time="上午", location="东城区",
        )
        assert "故宫" in str(a)
        assert "4.9" in str(a)

    def test_restaurant_str(self):
        r = Restaurant(
            name="全聚德", cuisine="烤鸭", rating=4.3,
            avg_price=180, signature_dish="烤鸭",
            location="前门", must_try=True,
        )
        assert "全聚德" in str(r)
        assert "必吃" in str(r)

    def test_hotel_str(self):
        h = Hotel(
            name="希尔顿", hotel_type="豪华型", rating=4.7,
            price_per_night=1200, location="王府井",
            amenities=["健身房", "泳池"], highlights="位置好",
        )
        assert "希尔顿" in str(h)
        assert "1200" in str(h)

    def test_travel_plan_str(self):
        pref = TravelPreference(
            destination="北京", start_date="2025-10-01", end_date="2025-10-03",
            budget=3000, style=TravelStyle.CULTURAL,
        )
        plan = TravelPlan(
            preference=pref, weather=[], hotel=None,
            itinerary=[], total_estimated_cost=2500,
            summary="测试总结",
        )
        result = str(plan)
        assert "北京" in result
        assert "3日" in result


class TestWeatherAgent:
    def test_get_weather(self):
        agent = WeatherAgent()
        results = agent.get_weather_for_trip("北京", ["2025-10-01"])
        assert len(results) == 1
        assert results[0].location == "北京"

    def test_get_weather_unknown_city(self):
        agent = WeatherAgent()
        results = agent.get_weather_for_trip("未知城市", ["2025-10-01"])
        assert len(results) == 1


class TestHotelAgent:
    def test_recommend_hotel(self):
        agent = HotelAgent()
        hotel = agent.recommend_for_trip("北京", budget_per_night=500)
        assert hotel.name is not None
        assert hotel.price_per_night <= 500 or hotel.hotel_type in ("舒适型", "经济型")

    def test_recommend_luxury(self):
        agent = HotelAgent()
        hotel = agent.recommend_for_trip("上海", budget_per_night=2000, style="豪华享受")
        assert hotel.name is not None


class TestFoodAgent:
    def test_get_restaurants(self):
        agent = FoodAgent()
        restaurants = agent.get_restaurants_for_trip("成都")
        assert len(restaurants) > 0
        assert any(r.must_try for r in restaurants)

    def test_get_must_try(self):
        agent = FoodAgent()
        must_try = agent.get_must_try("成都")
        assert len(must_try) > 0
        assert all(r.must_try for r in must_try)


class TestItineraryAgent:
    def test_get_attractions(self):
        agent = ItineraryAgent()
        attractions = agent.get_attractions("西安")
        assert len(attractions) > 0

    def test_get_attractions_by_category(self):
        agent = ItineraryAgent()
        attractions = agent.get_attractions("西安", category="历史")
        assert len(attractions) > 0
        assert all(a.category == "历史" for a in attractions)

    def test_plan_day(self):
        agent = ItineraryAgent()
        attractions = agent.plan_day("北京", "历史文化", max_attractions=2)
        assert len(attractions) <= 2


class TestTravelPlanner:
    def test_plan_beijing(self):
        planner = TravelPlanner()
        plan = planner.plan(
            destination="北京",
            start_date="2025-10-01",
            end_date="2025-10-03",
            budget=3000,
            style="文化体验",
        )
        assert plan.preference.destination == "北京"
        assert plan.preference.num_days == 3
        assert len(plan.itinerary) == 3
        assert plan.hotel is not None
        assert len(plan.weather) > 0
        assert plan.total_estimated_cost > 0
        assert plan.summary != ""

    def test_plan_chengdu_foodie(self):
        planner = TravelPlanner()
        plan = planner.plan(
            destination="成都",
            start_date="2025-10-10",
            end_date="2025-10-12",
            budget=2500,
            style="美食之旅",
        )
        assert plan.preference.style == TravelStyle.FOODIE
        assert len(plan.itinerary) == 3

    def test_plan_sanya_relaxed(self):
        planner = TravelPlanner()
        plan = planner.plan(
            destination="三亚",
            start_date="2025-12-20",
            end_date="2025-12-22",
            budget=5000,
            style="休闲放松",
        )
        assert plan.preference.destination == "三亚"
        assert len(plan.itinerary) == 3

    def test_plan_output_format(self):
        planner = TravelPlanner()
        plan = planner.plan(
            destination="杭州",
            start_date="2025-11-01",
            end_date="2025-11-03",
            budget=3000,
        )
        output = str(plan)
        assert "杭州" in output
        assert "3日" in output
        assert "天气预报" in output
        assert "推荐住宿" in output
        assert "行程安排" in output

    def test_plan_to_dict(self):
        planner = TravelPlanner()
        plan = planner.plan(
            destination="西安",
            start_date="2025-09-01",
            end_date="2025-09-03",
            budget=2000,
        )
        d = plan.to_dict()
        assert d["preference"]["destination"] == "西安"
        assert len(d["itinerary"]) == 3
        assert d["total_estimated_cost"] > 0
