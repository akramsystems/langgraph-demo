from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START
from langgraph.func import entrypoint, task
from langgraph.types import Command, interrupt
from langgraph.checkpoint.memory import MemorySaver
llm = ChatOpenAI(model="gpt-4o-mini")




@task
def step_1(input_query):
    """Append bar."""
    return f"{input_query} bar"

@task
def human_feedback(input_query):
    """Append user input."""
    # the feedback is what ever the resume value was in our input_query
    # in this case the resume value was "BAZ" because we passed it in
    # "Command(resume="BAZ") other words blah blah blah" as the input_query
    feedback = interrupt(f"Please provide feedback: {input_query}")
    return f"{input_query} {feedback}"

@task
def step_3(input_query):
    """Append qux."""
    return f"{input_query} qux"

checkpointer = MemorySaver()

@entrypoint(checkpointer=checkpointer)
def graph(input_query):
    breakpoint()
    result_1 = step_1(input_query).result()
    breakpoint()
    result_2 = human_feedback(result_1).result()
    breakpoint()
    result_3 = step_3(result_2).result()
    breakpoint()
    return result_3

config = {"configurable": {"thread_id": "1"}}

for event in graph.stream(Command(resume="BAZ"), config):
    print(event)
    print("-"*100)
