
from langchain_core.tools import tool
from langchain_core.messages import ToolMessage
from langgraph.graph.message import add_messages
from langgraph.func import entrypoint, task
from langgraph.types import Command, interrupt
from langchain_openai import ChatOpenAI; model = ChatOpenAI(model="gpt-4o-mini")
from langgraph.checkpoint.memory import MemorySaver; checkpointer = MemorySaver()



#### TOOLS ####
@tool
def get_weather(location: str):
    """Call to get the weather from a specific location."""
    # This is a placeholder for the actual implementation
    if any([city in location.lower() for city in ["sf", "san francisco"]]):
        return "It's sunny!"
    elif "boston" in location.lower():
        return "It's rainy!"
    else:
        return f"I am not sure what the weather is in {location}"


@tool
def human_assistance(query: str) -> str:
    """Request assistance from a human."""
    human_response = interrupt({"query": query})
    return human_response["data"]

tools = [get_weather, human_assistance]
tools_by_name = {tool.name: tool for tool in tools}

#### TASKS ####
@task
def call_model(messages):
    """Call model with a sequence of messages."""
    response = model.bind_tools(tools).invoke(messages)
    return response

@task
def call_tool(tool_call):
    tool = tools_by_name[tool_call["name"]]
    observation = tool.invoke(tool_call)
    return ToolMessage(content=observation, tool_call_id=tool_call["id"])


#### ENTRYPOINT ####
@entrypoint(checkpointer=checkpointer)
def agent(messages, previous):
    if previous is not None:
        messages = add_messages(previous, messages)

    llm_response = call_model(messages).result()
    while True:
        if not llm_response.tool_calls:
            break

        # Execute tools
        tool_result_futures = [
            call_tool(tool_call) for tool_call in llm_response.tool_calls
        ]
        tool_results = [fut.result() for fut in tool_result_futures]

        # Append to message list
        messages = add_messages(messages, [llm_response, *tool_results])

        # Call model again
        llm_response = call_model(messages).result()

    # Generate final response
    messages = add_messages(messages, llm_response)
    return entrypoint.final(value=llm_response, save=messages)


def _print_step(step: dict) -> None:
    for task_name, result in step.items():
        if task_name == "agent":
            continue # just stream from tasks
        if task_name == "__interrupt__":
            print(f"{result[0].value['query']}")
        else:
            result.pretty_print()


config = {"configurable": {"thread_id": "1"}}

user_message = {
    "role": "user",
    "content": (
        "Can you reach out for human assistance: what should I feed my cat? "
        "Separately, can you check the weather in San Francisco?"
    ),
}

for step in agent.stream([user_message], config):
    _print_step(step)
    if "__interrupt__" in step:
        human_input = input("Please provide feedback: ")
        for step in agent.stream(Command(resume={"data": human_input}), config):
            _print_step(step)

