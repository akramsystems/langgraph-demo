from dotenv import load_dotenv; load_dotenv()

from langgraph.types import Command
from graph import build_graph, stream_graph_updates


graph = build_graph()


def run_chatbot():
    
    user_input = (
        "Can you look up when LangGraph was released? "
        "When you have the answer, use the human_assistance tool for review."
    )
    config = {"configurable": {"thread_id": "1"}}

    events = graph.stream(
        {"messages": [{"role": "user", "content": user_input}]},
        config,
        stream_mode="values",
    )
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()
        
    human_command = Command(
        resume={
            "name": "LangGraph",
            "birthday": "Jan 17, 2024",
        },
    )

    events = graph.stream(human_command, config, stream_mode="values")
    for event in events:
        if "messages" in event:
            event["messages"][-1].pretty_print()


    return
    # while True:
    #     try:
    #         user_input = input("User: ")
    #         if user_input.lower() in ["exit", "quit", "q"]:
    #             print("Exiting...")
    #             break
    #         stream_graph_updates(user_input, graph, config)
    #     except Exception as e:
    #         # fallback if input is not available
    #         user_input = "Remember my name?"
    #         stream_graph_updates(user_input, graph, config)
    #         break





if __name__ == "__main__":
    # VISUALIZE THE GRAPH
    img_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(img_data)
    img_data = graph.get_graph().draw_ascii()
    print(img_data)
    run_chatbot()
    
