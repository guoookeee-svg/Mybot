from mybot.travel.planner import TravelPlanner


def main():
    planner = TravelPlanner()

    print("=" * 60)
    print("🌍 MyBot AI 智能旅行规划助手")
    print("=" * 60)

    print("\n📋 方案一：北京3日文化之旅\n")
    plan1 = planner.plan(
        destination="北京",
        start_date="2025-10-01",
        end_date="2025-10-03",
        budget=3000,
        style="文化体验",
        num_travelers=1,
    )
    print(plan1)

    print("\n\n" + "=" * 60)
    print("📋 方案二：成都3日美食之旅\n")
    plan2 = planner.plan(
        destination="成都",
        start_date="2025-10-10",
        end_date="2025-10-12",
        budget=2500,
        style="美食之旅",
        num_travelers=2,
    )
    print(plan2)

    print("\n\n" + "=" * 60)
    print("📋 方案三：三亚3日休闲之旅\n")
    plan3 = planner.plan(
        destination="三亚",
        start_date="2025-12-20",
        end_date="2025-12-22",
        budget=5000,
        style="休闲放松",
        num_travelers=2,
    )
    print(plan3)

    print("\n\n" + "=" * 60)
    print("📊 方案对比:\n")
    for name, plan in [("北京文化之旅", plan1), ("成都美食之旅", plan2), ("三亚休闲之旅", plan3)]:
        print(f"  {name}: {plan.preference.num_days}天 | "
              f"预算¥{plan.preference.budget} | "
              f"预估¥{plan.total_estimated_cost:.0f} | "
              f"住宿: {plan.hotel.name if plan.hotel else 'N/A'}")


if __name__ == "__main__":
    main()
