from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from mybot.travel.agents.weather import WeatherAgent
from mybot.travel.agents.hotel import HotelAgent
from mybot.travel.agents.food import FoodAgent
from mybot.travel.agents.itinerary import ItineraryAgent
from mybot.travel.models import (
    Attraction,
    DayItinerary,
    Hotel,
    Restaurant,
    TravelPlan,
    TravelPreference,
    TravelStyle,
    WeatherInfo,
)


class TravelPlanner:
    def __init__(self):
        self.weather_agent = WeatherAgent()
        self.hotel_agent = HotelAgent()
        self.food_agent = FoodAgent()
        self.itinerary_agent = ItineraryAgent()

    def plan(
        self,
        destination: str,
        start_date: str,
        end_date: str,
        budget: float,
        style: str = "休闲放松",
        num_travelers: int = 1,
        special_requests: Optional[List[str]] = None,
    ) -> TravelPlan:
        style_map = {s.value: s for s in TravelStyle}
        travel_style = style_map.get(style, TravelStyle.RELAXED)

        preference = TravelPreference(
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            style=travel_style,
            num_travelers=num_travelers,
            special_requests=special_requests or [],
        )

        dates = self._get_date_range(start_date, end_date)

        weather_list = self.weather_agent.get_weather_for_trip(destination, dates)

        hotel_budget = preference.daily_budget * 0.35
        hotel = self.hotel_agent.recommend_for_trip(
            city=destination,
            budget_per_night=hotel_budget,
            style=travel_style.value,
        )

        all_restaurants = self.food_agent.get_restaurants_for_trip(destination)
        must_try = self.food_agent.get_must_try(destination)

        all_attractions = self.itinerary_agent.get_attractions(destination)

        day_themes = self._assign_day_themes(preference.num_days, travel_style)

        itinerary = self._build_itinerary(
            dates=dates,
            day_themes=day_themes,
            destination=destination,
            all_attractions=all_attractions,
            all_restaurants=all_restaurants,
            must_try=must_try,
            preference=preference,
        )

        total_cost = self._estimate_cost(hotel, itinerary, preference)

        summary = self._generate_summary(preference, weather_list, hotel, itinerary, total_cost)

        return TravelPlan(
            preference=preference,
            weather=weather_list,
            hotel=hotel,
            itinerary=itinerary,
            total_estimated_cost=total_cost,
            summary=summary,
        )

    def _get_date_range(self, start_date: str, end_date: str) -> List[str]:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days + 1
            return [(start + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(days)]
        except ValueError:
            return [start_date]

    def _assign_day_themes(self, num_days: int, style: TravelStyle) -> List[str]:
        if style == TravelStyle.CULTURAL:
            base_themes = ["历史文化", "文化体验", "历史古迹"]
        elif style == TravelStyle.ADVENTURE:
            base_themes = ["自然探险", "户外运动", "探险挑战"]
        elif style == TravelStyle.FOODIE:
            base_themes = ["美食探索", "特色小吃", "美食打卡"]
        elif style == TravelStyle.LUXURY:
            base_themes = ["精品体验", "高端休闲", "奢华享受"]
        else:
            base_themes = ["经典打卡", "深度体验", "休闲漫步"]

        themes = []
        for i in range(num_days):
            themes.append(base_themes[i % len(base_themes)])
        return themes

    def _build_itinerary(
        self,
        dates: List[str],
        day_themes: List[str],
        destination: str,
        all_attractions: List[Attraction],
        all_restaurants: List[Restaurant],
        must_try: List[Restaurant],
        preference: TravelPreference,
    ) -> List[DayItinerary]:
        itinerary = []
        used_attractions = set()
        used_restaurants = set()
        must_try_assigned = 0

        for i, (date, theme) in enumerate(zip(dates, day_themes)):
            day_attractions = self._pick_attractions(
                all_attractions, theme, used_attractions, max_count=3
            )
            used_attractions.update(a.name for a in day_attractions)

            day_restaurants = self._pick_restaurants(
                all_restaurants, must_try, used_restaurants,
                must_try_quota=len(dates) - must_try_assigned,
                max_count=2,
            )
            used_restaurants.update(r.name for r in day_restaurants)
            must_try_assigned += sum(1 for r in day_restaurants if r.must_try)

            tips = self._generate_day_tips(date, day_attractions, preference)

            itinerary.append(DayItinerary(
                day=i + 1,
                date=date,
                theme=theme,
                attractions=day_attractions,
                restaurants=day_restaurants,
                tips=tips,
            ))

        return itinerary

    def _pick_attractions(
        self,
        all_attractions: List[Attraction],
        theme: str,
        used: set,
        max_count: int = 3,
    ) -> List[Attraction]:
        available = [a for a in all_attractions if a.name not in used]
        if not available:
            available = all_attractions

        if "历史" in theme:
            preferred = [a for a in available if a.category == "历史"]
        elif "自然" in theme or "探险" in theme:
            preferred = [a for a in available if a.category in ("自然", "历史")]
        elif "文化" in theme or "体验" in theme:
            preferred = [a for a in available if a.category in ("文化", "历史")]
        elif "美食" in theme:
            preferred = [a for a in available if a.category in ("文化", "娱乐")]
        else:
            preferred = available

        if not preferred:
            preferred = available

        preferred.sort(key=lambda a: a.rating, reverse=True)
        return preferred[:max_count]

    def _pick_restaurants(
        self,
        all_restaurants: List[Restaurant],
        must_try: List[Restaurant],
        used: set,
        must_try_quota: int = 1,
        max_count: int = 2,
    ) -> List[Restaurant]:
        selected = []

        if must_try and must_try_quota > 0:
            for r in must_try:
                if r.name not in used:
                    selected.append(r)
                    break

        remaining_slots = max_count - len(selected)
        if remaining_slots > 0:
            available = [r for r in all_restaurants if r.name not in used and r.name not in {s.name for s in selected}]
            available.sort(key=lambda r: r.rating, reverse=True)
            selected.extend(available[:remaining_slots])

        return selected

    def _generate_day_tips(self, date: str, attractions: List[Attraction], preference: TravelPreference) -> str:
        tips = []
        if attractions:
            first = attractions[0]
            tips.append(f"建议{first.best_time}到达{first.name}")
        if preference.style == TravelStyle.BUDGET:
            free_count = sum(1 for a in attractions if a.ticket_price == 0)
            if free_count > 0:
                tips.append(f"当天有{free_count}个免费景点")
        if preference.num_travelers > 2:
            tips.append("多人出行建议提前预约团队票")
        return "；".join(tips)

    def _estimate_cost(self, hotel: Hotel, itinerary: List[DayItinerary], preference: TravelPreference) -> float:
        hotel_cost = hotel.price_per_night * preference.num_days

        ticket_cost = 0
        food_cost = 0
        for day in itinerary:
            for a in day.attractions:
                ticket_cost += a.ticket_price
            for r in day.restaurants:
                food_cost += r.avg_price

        ticket_cost *= preference.num_travelers
        food_cost *= preference.num_travelers

        transport_estimate = preference.num_days * 50 * preference.num_travelers

        return hotel_cost + ticket_cost + food_cost + transport_estimate

    def _generate_summary(
        self,
        preference: TravelPreference,
        weather: List[WeatherInfo],
        hotel: Hotel,
        itinerary: List[DayItinerary],
        total_cost: float,
    ) -> str:
        lines = []
        lines.append(f"为您规划了{preference.destination}{preference.num_days}日{preference.style.value}之旅。")

        if weather:
            avg_temp = sum((w.temperature_high + w.temperature_low) / 2 for w in weather) / len(weather)
            rainy_days = sum(1 for w in weather if "雨" in w.condition)
            if rainy_days > 0:
                lines.append(f"期间有{rainy_days}天可能下雨，请带好雨具。")
            lines.append(f"平均气温约{avg_temp:.0f}°C。")

        total_attractions = sum(len(d.attractions) for d in itinerary)
        total_restaurants = sum(len(d.restaurants) for d in itinerary)
        lines.append(f"共安排{total_attractions}个景点、{total_restaurants}家餐厅。")

        if total_cost > preference.budget:
            lines.append(f"预估费用¥{total_cost:.0f}略超预算，可适当调整住宿或减少付费景点。")
        else:
            lines.append(f"预估费用¥{total_cost:.0f}，在预算范围内。")

        return "".join(lines)
