from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


class TravelStyle(Enum):
    RELAXED = "休闲放松"
    ADVENTURE = "探险刺激"
    CULTURAL = "文化体验"
    FOODIE = "美食之旅"
    BUDGET = "经济实惠"
    LUXURY = "豪华享受"


@dataclass
class WeatherInfo:
    location: str
    date: str
    temperature_high: float
    temperature_low: float
    condition: str
    humidity: float
    wind: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "location": self.location,
            "date": self.date,
            "temperature_high": self.temperature_high,
            "temperature_low": self.temperature_low,
            "condition": self.condition,
            "humidity": self.humidity,
            "wind": self.wind,
        }

    def __str__(self) -> str:
        return f"{self.location} {self.date}: {self.condition} {self.temperature_low}~{self.temperature_high}°C"


@dataclass
class Attraction:
    name: str
    description: str
    category: str
    rating: float
    visit_duration: str
    ticket_price: float
    best_time: str
    location: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "rating": self.rating,
            "visit_duration": self.visit_duration,
            "ticket_price": self.ticket_price,
            "best_time": self.best_time,
            "location": self.location,
        }

    def __str__(self) -> str:
        return f"【{self.name}】{self.category} | 评分{self.rating} | 游览{self.visit_duration} | 门票¥{self.ticket_price} | {self.description}"


@dataclass
class Restaurant:
    name: str
    cuisine: str
    rating: float
    avg_price: float
    signature_dish: str
    location: str
    must_try: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "cuisine": self.cuisine,
            "rating": self.rating,
            "avg_price": self.avg_price,
            "signature_dish": self.signature_dish,
            "location": self.location,
            "must_try": self.must_try,
        }

    def __str__(self) -> str:
        tag = " ★必吃" if self.must_try else ""
        return f"【{self.name}】{self.cuisine}{tag} | 评分{self.rating} | 人均¥{self.avg_price} | 招牌: {self.signature_dish}"


@dataclass
class Hotel:
    name: str
    hotel_type: str
    rating: float
    price_per_night: float
    location: str
    amenities: List[str]
    highlights: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "hotel_type": self.hotel_type,
            "rating": self.rating,
            "price_per_night": self.price_per_night,
            "location": self.location,
            "amenities": self.amenities,
            "highlights": self.highlights,
        }

    def __str__(self) -> str:
        amenities_str = "、".join(self.amenities[:4])
        return f"【{self.name}】{self.hotel_type} | 评分{self.rating} | ¥{self.price_per_night}/晚 | {amenities_str} | {self.highlights}"


@dataclass
class DayItinerary:
    day: int
    date: str
    theme: str
    attractions: List[Attraction]
    restaurants: List[Restaurant]
    tips: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "day": self.day,
            "date": self.date,
            "theme": self.theme,
            "attractions": [a.to_dict() for a in self.attractions],
            "restaurants": [r.to_dict() for r in self.restaurants],
            "tips": self.tips,
        }

    def __str__(self) -> str:
        lines = [f"📍 第{self.day}天 ({self.date}) - {self.theme}"]
        for a in self.attractions:
            lines.append(f"  🏛️ {a}")
        for r in self.restaurants:
            lines.append(f"  🍜 {r}")
        if self.tips:
            lines.append(f"  💡 贴士: {self.tips}")
        return "\n".join(lines)


@dataclass
class TravelPreference:
    destination: str
    start_date: str
    end_date: str
    budget: float
    style: TravelStyle = TravelStyle.RELAXED
    num_travelers: int = 1
    special_requests: List[str] = field(default_factory=list)

    @property
    def num_days(self) -> int:
        from datetime import datetime
        try:
            start = datetime.strptime(self.start_date, "%Y-%m-%d")
            end = datetime.strptime(self.end_date, "%Y-%m-%d")
            return (end - start).days + 1
        except ValueError:
            return 3

    @property
    def daily_budget(self) -> float:
        days = self.num_days
        return self.budget / days if days > 0 else self.budget

    def to_dict(self) -> Dict[str, Any]:
        return {
            "destination": self.destination,
            "start_date": self.start_date,
            "end_date": self.end_date,
            "budget": self.budget,
            "style": self.style.value,
            "num_travelers": self.num_travelers,
            "special_requests": self.special_requests,
            "num_days": self.num_days,
            "daily_budget": self.daily_budget,
        }


@dataclass
class TravelPlan:
    preference: TravelPreference
    weather: List[WeatherInfo]
    hotel: Optional[Hotel]
    itinerary: List[DayItinerary]
    total_estimated_cost: float = 0.0
    summary: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "preference": self.preference.to_dict(),
            "weather": [w.to_dict() for w in self.weather],
            "hotel": self.hotel.to_dict() if self.hotel else None,
            "itinerary": [d.to_dict() for d in self.itinerary],
            "total_estimated_cost": self.total_estimated_cost,
            "summary": self.summary,
        }

    def __str__(self) -> str:
        lines = []
        lines.append("=" * 60)
        lines.append(f"🌍 {self.preference.destination} {self.preference.num_days}日旅行方案")
        lines.append(f"📅 {self.preference.start_date} ~ {self.preference.end_date}")
        lines.append(f"💰 预算: ¥{self.preference.budget} (日均¥{self.preference.daily_budget:.0f})")
        lines.append(f"🎯 风格: {self.preference.style.value}")
        lines.append("=" * 60)

        if self.weather:
            lines.append("\n🌤️ 天气预报:")
            for w in self.weather:
                lines.append(f"  {w}")

        if self.hotel:
            lines.append(f"\n🏨 推荐住宿:\n  {self.hotel}")

        if self.itinerary:
            lines.append("\n📋 行程安排:")
            for day in self.itinerary:
                lines.append(f"\n{day}")

        if self.total_estimated_cost > 0:
            lines.append(f"\n💰 预估总费用: ¥{self.total_estimated_cost:.0f}")

        if self.summary:
            lines.append(f"\n📝 总结: {self.summary}")

        return "\n".join(lines)
