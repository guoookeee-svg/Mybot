from mybot import Agent, Orchestrator, tool


@tool(name="get_weather", description="Get weather information for a location")
def get_weather(location: str) -> str:
    weather_data = {
        "beijing": "Sunny, 25°C",
        "shanghai": "Cloudy, 22°C",
        "shenzhen": "Rainy, 28°C",
    }
    return weather_data.get(location.lower(), f"Weather data for {location} not available")


@tool(name="translate", description="Translate text to English")
def translate(text: str) -> str:
    translations = {
        "你好": "Hello",
        "谢谢": "Thank you",
        "再见": "Goodbye",
    }
    return translations.get(text, f"Translation for '{text}' not available")


def main():
    weather_agent = Agent(
        name="WeatherBot",
        description="Provides weather information",
        system_prompt="You are a weather assistant. Use the get_weather tool when asked about weather.",
    )
    weather_agent.register_tool(get_weather)

    translator_agent = Agent(
        name="TranslatorBot",
        description="Translates text to English",
        system_prompt="You are a translation assistant. Use the translate tool when asked to translate.",
    )
    translator_agent.register_tool(translate)

    general_agent = Agent(
        name="GeneralBot",
        description="General purpose assistant",
        system_prompt="You are a general purpose assistant.",
    )

    orchestrator = Orchestrator()
    orchestrator.register_agent(weather_agent)
    orchestrator.register_agent(translator_agent)
    orchestrator.register_agent(general_agent)

    print("=== Multi-Agent Orchestrator Demo ===\n")

    print("1. Auto-routing (weather query):")
    result = orchestrator.route("What's the weather in Beijing?", strategy="auto")
    print(f"   Routed to: {result['agent']}")
    print(f"   Response: {result['response']}\n")

    print("2. Broadcast strategy:")
    result = orchestrator.route("Hello everyone!", strategy="broadcast")
    for r in result["results"]:
        print(f"   {r['agent']}: {r['response']}")
    print()

    print("3. Multi-agent collaboration (debate):")
    result = orchestrator.multi_agent_collaboration(
        "Is AI beneficial for society?",
        agent_names=["GeneralBot", "WeatherBot"],
        collaboration_mode="debate",
    )
    print(f"   Perspectives:")
    for p in result["perspectives"]:
        print(f"     {p['agent']}: {p['response']}")
    print(f"   Synthesis: {result['synthesis']}\n")

    print("4. Pipeline mode:")
    result = orchestrator.multi_agent_collaboration(
        "Process this request",
        agent_names=["GeneralBot", "TranslatorBot"],
        collaboration_mode="pipeline",
    )
    for step in result["steps"]:
        print(f"   {step['agent']}: {step['output']}")
    print(f"   Final: {result['final_output']}")


if __name__ == "__main__":
    main()
