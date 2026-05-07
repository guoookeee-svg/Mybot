# MyBot - AI 智能体框架

> 一个轻量级、可扩展的 AI Agent 框架，支持工具调用、记忆管理、任务规划和多智能体协作。

## 项目概述

MyBot 是一个面向面试演示的 AI 智能体框架，展示了如何构建一个模块化的 Agent 系统。框架设计参考了 LangChain、AutoGPT 等主流 Agent 框架的核心思想，同时保持代码简洁易懂。

### 核心特性

- **智能体（Agent）**：支持系统提示词、工具调用、流式输出的智能体实体
- **工具系统（Tool System）**：通过装饰器快速注册函数为工具，支持自动参数推断
- **记忆系统（Memory）**：短期/长期记忆分离，支持内存和文件存储后端
- **LLM 客户端**：抽象接口支持 OpenAI 等多种后端，内置 Mock 客户端用于测试
- **任务规划器（Planner）**：任务依赖管理、拓扑排序执行、自动任务分解
- **多智能体编排器（Orchestrator）**：智能路由、广播、顺序执行、辩论、流水线等协作模式

---

## 项目结构

```
mybot/
├── __init__.py          # 包入口，导出公共 API
├── agent.py             # Agent 智能体核心实现
├── tool.py              # 工具系统（Tool、FunctionTool、ToolRegistry）
├── memory.py            # 记忆系统（Memory、StorageBackend）
├── llm.py               # LLM 客户端（OpenAIClient、MockLLMClient）
├── planner.py           # 任务规划器（Planner、Task）
├── session.py           # 会话管理（Session）
└── orchestrator.py      # 多智能体编排器（Orchestrator）

examples/
├── basic_agent.py       # 基础智能体示例
├── multi_agent_demo.py  # 多智能体协作示例
└── planner_demo.py      # 任务规划示例

tests/
├── test_tool.py         # 工具系统测试
├── test_memory.py       # 记忆系统测试
├── test_agent.py        # 智能体测试
├── test_planner.py      # 规划器测试
└── test_orchestrator.py # 编排器测试
```

---

## 快速开始

### 安装

```bash
pip install -e .
```

### 基础示例

```python
from mybot import Agent, tool

# 定义工具
@tool(name="calculator", description="执行数学计算")
def calculator(expression: str) -> str:
    return str(eval(expression))

# 创建智能体
agent = Agent(
    name="MathAssistant",
    description="数学助手",
    system_prompt="你是一个数学助手，使用工具进行计算。"
)

# 注册工具
agent.register_tool(calculator)

# 运行
result = agent.run("计算 15 * 23 + 7")
print(result["response"])
```

### 多智能体协作示例

```python
from mybot import Agent, Orchestrator

# 创建多个智能体
weather_agent = Agent(name="WeatherBot", description="天气助手")
translator_agent = Agent(name="TranslatorBot", description="翻译助手")

# 创建编排器
orchestrator = Orchestrator()
orchestrator.register_agent(weather_agent)
orchestrator.register_agent(translator_agent)

# 自动路由
result = orchestrator.route("北京今天天气怎么样？", strategy="auto")
print(f"路由到: {result['agent']}")
print(f"回复: {result['response']}")

# 多智能体辩论
result = orchestrator.multi_agent_collaboration(
    "AI 对社会有益吗？",
    agent_names=["WeatherBot", "TranslatorBot"],
    collaboration_mode="debate"
)
```

---

## 核心模块详解

### 1. 工具系统 (tool.py)

#### Tool 抽象基类

所有工具都继承自 `Tool` 基类，必须实现 `execute` 方法。

```python
from mybot.tool import Tool, ToolResult, ToolParameter

class MyTool(Tool):
    name = "my_tool"
    description = "我的自定义工具"
    parameters = [
        ToolParameter(name="input", type="string", description="输入参数")
    ]

    def execute(self, input: str) -> ToolResult:
        return ToolResult(success=True, data=f"处理结果: {input}")
```

#### @tool 装饰器

最便捷的方式是使用 `@tool` 装饰器将普通函数转换为工具：

```python
from mybot import tool

@tool(name="greet", description="打招呼")
def greet(name: str) -> str:
    return f"你好，{name}！"
```

装饰器会自动：
- 提取函数名作为工具名（可覆盖）
- 提取文档字符串作为描述
- 通过函数签名推断参数类型

#### ToolRegistry

工具注册中心管理所有可用工具：

```python
from mybot.tool import ToolRegistry

registry = ToolRegistry()
registry.register(greet)

# 执行工具
result = registry.execute("greet", name="张三")
print(result.data)  # 你好，张三！

# 获取 OpenAI 格式的工具描述
schemas = registry.to_openai_schemas()
```

### 2. 记忆系统 (memory.py)

#### Memory 类

```python
from mybot import Memory

memory = Memory()

# 添加记忆
memory.add("用户说: 你好", role="user")
memory.add("助手回复: 您好！", role="assistant")

# 获取历史
history = memory.get_history(limit=10)

# 搜索记忆
results = memory.search("你好")

# 转换为消息格式
messages = memory.to_messages()
```

#### 存储后端

支持两种存储后端：

- **InMemoryStorage**：内存存储，适合短期会话
- **FileStorage**：文件存储，数据持久化到 JSON 文件

```python
from mybot.memory import Memory, FileStorage

storage = FileStorage("memory.json")
memory = Memory(storage=storage)
```

### 3. LLM 客户端 (llm.py)

#### OpenAIClient

```python
from mybot import OpenAIClient

llm = OpenAIClient(
    api_key="your-api-key",
    model="gpt-4o-mini"
)

# 完整响应
response = llm.complete("你好")
print(response["content"])

# 流式输出
for chunk in llm.stream("你好"):
    print(chunk, end="")
```

#### MockLLMClient

用于测试的模拟客户端：

```python
from mybot import MockLLMClient

llm = MockLLMClient([
    "这是第一个响应",
    "这是第二个响应"
])
```

### 4. 智能体 (agent.py)

#### Agent 类

智能体是框架的核心，整合 LLM、工具、记忆等组件：

```python
from mybot import Agent

agent = Agent(
    name="MyAgent",
    description="我的智能体",
    system_prompt="你是一个有用的助手。",
    llm_client=llm
)

# 注册工具
agent.register_tool(calculator)
agent.register_tool(greet)

# 运行（自动处理工具调用）
result = agent.run("计算 1+1 并问候张三")
print(result["response"])
print(result["tool_calls"])  # 工具调用历史

# 流式输出
for chunk in agent.stream("讲个故事"):
    print(chunk, end="")

# 任务规划与执行
result = agent.plan_and_execute("写一篇关于 AI 的文章")
```

#### 会话管理

```python
# 创建会话
session = agent.create_session()

# 在指定会话中运行
result = agent.run("你好", session_id=session.session_id)

# 获取会话信息
print(session.to_dict())
```

### 5. 任务规划器 (planner.py)

#### Planner 类

```python
from mybot import Planner

planner = Planner()

# 创建任务
task1 = planner.create_task(name="research", description="研究主题")
task2 = planner.create_task(
    name="write",
    description="撰写内容",
    dependencies=[task1.task_id]
)

# 查看可执行任务
ready = planner.get_ready_tasks()

# 执行单个任务
planner.execute_task(task1.task_id, executor=lambda t: "研究结果")

# 执行所有可执行任务
planner.execute_all(executor=lambda t: f"完成 {t.name}")

# 查看执行历史
history = planner.get_execution_history()
```

### 6. 多智能体编排器 (orchestrator.py)

#### Orchestrator 类

```python
from mybot import Orchestrator

orchestrator = Orchestrator()
orchestrator.register_agent(agent1)
orchestrator.register_agent(agent2)

# 自动路由（根据描述和工具匹配）
result = orchestrator.route("查询天气", strategy="auto")

# 广播模式（所有智能体都处理）
result = orchestrator.route("大家好", strategy="broadcast")

# 顺序模式（智能体链式处理）
result = orchestrator.route("处理数据", strategy="sequential")

# 多智能体辩论
result = orchestrator.multi_agent_collaboration(
    "AI 是否有害？",
    agent_names=["Agent1", "Agent2"],
    collaboration_mode="debate"
)

# 流水线模式
result = orchestrator.multi_agent_collaboration(
    "原始数据",
    agent_names=["Processor", "Analyzer"],
    collaboration_mode="pipeline"
)
```

---

## 架构设计

### 设计原则

1. **单一职责**：每个模块只负责一个功能领域
2. **依赖注入**：通过构造函数注入依赖，便于测试和替换
3. **接口抽象**：使用抽象基类定义接口，支持多种实现
4. **组合优于继承**：通过组合构建复杂功能

### 核心交互流程

```
用户输入
    ↓
Agent.run()
    ↓
Memory.add(user_message)
    ↓
LLMClient.complete(messages, tools)
    ↓
是否需要工具调用?
    ├── 否 → 直接返回响应
    └── 是 → ToolRegistry.execute(tool_name)
              ↓
              Memory.add(tool_result)
              ↓
              再次调用 LLM（最多 5 轮）
```

### 类图

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Agent     │────▶│   Memory    │────▶│  Storage    │
│             │     │             │     │  (Backend)  │
│ - name      │     │ - entries   │     │             │
│ - system    │     │ - max_size  │     │ - save()    │
│ - tools     │     └─────────────┘     │ - load()    │
│ - planner   │                         └─────────────┘
└──────┬──────┘
       │
       ▼
┌─────────────┐     ┌─────────────┐
│  LLMClient  │◀────│  ToolRegistry│
│  (Abstract) │     │              │
│             │     │ - register() │
│ - complete()│     │ - execute()  │
│ - stream()  │     │ - schemas()  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       ▼                   ▼
┌─────────────┐     ┌─────────────┐
│ OpenAIClient│     │    Tool     │
│             │     │  (Abstract) │
└─────────────┘     │             │
                    │ - execute() │
                    └──────┬──────┘
                           │
                    ┌──────┴──────┐
                    │ FunctionTool │
                    │  (@tool)     │
                    └─────────────┘
```

---

## 测试

### 运行测试

```bash
pytest tests/ -v
```

### 测试覆盖

| 模块 | 测试文件 | 测试点 |
|------|----------|--------|
| 工具系统 | test_tool.py | 工具注册、执行、参数验证、Schema 生成 |
| 记忆系统 | test_memory.py | 添加、检索、搜索、清空、文件存储 |
| 智能体 | test_agent.py | 创建、运行、工具调用、会话、历史 |
| 规划器 | test_planner.py | 任务创建、依赖、执行、历史 |
| 编排器 | test_orchestrator.py | 注册、路由、广播、协作 |

---

## 扩展指南

### 添加自定义 LLM 后端

```python
from mybot.llm import LLMClient

class ClaudeClient(LLMClient):
    def complete(self, messages, system=None, tools=None, temperature=0.7, max_tokens=None):
        # 实现 Claude API 调用
        pass

    def stream(self, messages, system=None, tools=None, temperature=0.7, max_tokens=None):
        # 实现流式输出
        pass
```

### 添加自定义存储后端

```python
from mybot.memory import StorageBackend, MemoryEntry

class RedisStorage(StorageBackend):
    def save(self, entry: MemoryEntry) -> None:
        # 保存到 Redis
        pass

    def load(self, limit=None):
        # 从 Redis 加载
        pass

    def search(self, query, limit=5):
        # Redis 搜索
        pass

    def clear(self):
        # 清空 Redis
        pass
```

### 添加自定义工具

```python
from mybot import Tool, ToolResult, ToolParameter

class DatabaseTool(Tool):
    name = "query_db"
    description = "查询数据库"
    parameters = [
        ToolParameter(name="sql", type="string", description="SQL 语句", required=True)
    ]

    def execute(self, sql: str) -> ToolResult:
        try:
            result = db.execute(sql)
            return ToolResult(success=True, data=result)
        except Exception as e:
            return ToolResult(success=False, error=str(e))
```

---

## 技术栈

- **Python 3.9+**
- **pytest**：测试框架
- **dataclasses**：数据模型
- **typing**：类型提示
- **可选**：openai（OpenAI 客户端）

---

## 面试要点

### 考察能力

1. **架构设计能力**：模块化、可扩展的框架设计
2. **抽象能力**：接口抽象、依赖注入
3. **Python 高级特性**：装饰器、生成器、类型系统
4. **LLM 应用开发**：工具调用、提示工程、流式输出
5. **软件工程**：测试覆盖、项目结构、文档

### 亮点特性

- **ReAct 模式**：推理 + 行动的循环执行
- **工具自动发现**：通过装饰器自动注册
- **多智能体协作**：辩论、流水线等模式
- **记忆持久化**：支持多种存储后端
- **类型安全**：全面的类型注解

---

## 许可证

MIT License

---

## 作者

Developer (dev@example.com)
