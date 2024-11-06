# Simple example of using  plain routing 
### 1) Routing Agent
### 2) Code Agent
### 3) Research Agent
# 
# The response is in json in case we need other systems to use it.


```
Router Agent uses pydantic schema as tool to comply with expected response

class RouterResponse(BaseModel):
    """Route user requests to appropriate agent"""

    selected_agent: Literal["CODE", "RESEARCH"] = Field(
        ..., description="Agent to handle the request"
    )
    confidence: float = Field(description="Confidence level in the routing decision")

# AgentRoute tool: self.tool = openai.pydantic_function_tool(RouterResponse, name="route_request")
# We also force agent to use that function:
# tool_choice={
                "type": "function",
                "function": {"name": "route_request"},
            },

# Furthermore the other agents (code and research) also use their own schema
class CodeResponse(BaseModel):
    """Code generation response"""

    code: str
    language: str = Field(description="python")


class ResearchResponse(BaseModel):
    """Research explanation response"""

    explanation: str = Field(description="explain using only 10 words")
    needs_code_example: Optional[bool]

# This ensure proper contract between Agents, Routing Agent and user or another systems consumeing from this mini service
# -----------------------------------------------------------------------------------------------------------------------

{
  "responses": [
    {
      "query": "Write a hello world program in Python",
      "type": "code",
      "status": "success",
      "router": {
        "selected_agent": "CODE",
        "confidence": 1.0
      },
      "data": {
        "type": "code",
        "router": {
          "selected_agent": "CODE",
          "confidence": 1.0
        },
        "response": {
          "code": "print('Hello, World!')",
          "language": "python"
        }
      },
      "timestamp": "2024-11-06T14:35:43.587520"
    },
    {
      "query": "Explain what a hello world program is",
      "type": "research",
      "status": "success",
      "router": {
        "selected_agent": "RESEARCH",
        "confidence": 0.9
      },
      "data": {
        "type": "research",
        "router": {
          "selected_agent": "RESEARCH",
          "confidence": 0.9
        },
        "response": {
          "explanation": "A basic program that displays 'Hello, World!' message.",
          "needs_code_example": false
        },
        "code_example": {
          "code": "print('Hello, World!')",
          "language": "python"
        }
      },
      "timestamp": "2024-11-06T14:35:46.481269"
    }
  ]
}
```
