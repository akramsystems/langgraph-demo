import json

from langchain_core.messages import ToolMessage
from langchain_core.tools import BaseTool

class BasicToolNode:
    """A node that runs the tools requests in the last AI Message"""

    def __init__(self, tools: list[BaseTool]):
        self.tools_by_name = {tool.name: tool for tool in tools}

    def __call__(self, inputs: dict) -> dict:
        
        if messages := inputs.get("messages", []):
            message = messages[-1]
        else:
            raise ValueError("No messages found in the inputs")
        
        outputs = []

        for tool_call in message.tool_calls:
            tool_result = self.tools_by_name[tool_call["name"]].invoke(
                tool_call["args"]
            )
            outputs.append(ToolMessage(
                content=json.dumps(tool_result),
                name=tool_call["name"],
                tool_call_id=tool_call["id"],
            ))

        return {"messages": outputs}
    
