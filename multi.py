import asyncio
import json
from datetime import datetime
from typing import Literal, Optional

import openai
from openai import AsyncOpenAI
from pydantic import BaseModel, Field

MODEL = "gpt-3.5-turbo"


# Schema definitions with validation
class RouterResponse(BaseModel):
    """Route user requests to appropriate agent"""

    selected_agent: Literal["CODE", "RESEARCH"] = Field(
        ..., description="Agent to handle the request"
    )
    confidence: float = Field(description="Confidence level in the routing decision")


class CodeResponse(BaseModel):
    """Code generation response"""

    code: str
    language: str = Field(description="python")


class ResearchResponse(BaseModel):
    """Research explanation response"""

    explanation: str = Field(description="explain using only 10 words")
    needs_code_example: Optional[bool]


class SystemResponse(BaseModel):
    """Standardized response format for all system outputs"""

    query: str
    type: Literal["code", "research", "error"]
    status: Literal["success", "error"]
    router: RouterResponse
    data: dict
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())


# Agents
class RouterAgent:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

        self.system_prompt = "You are a routing agent. Route requests to:\n"
        "- CODE: for programming tasks\n"
        "- RESEARCH: for explanations and questions"

        self.tool = openai.pydantic_function_tool(RouterResponse, name="route_request")

    async def route(self, query: str) -> RouterResponse:
        print("calling ROUTE AGENT", query)
        response = await self.client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": query},
            ],
            tools=[self.tool],
            tool_choice={
                "type": "function",
                "function": {"name": "route_request"},
            },
        )

        js = response.choices[0].message.tool_calls[0].function.arguments
        args = json.loads(js)
        return RouterResponse(**args)


class CodeAgent:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

        self.tool = openai.pydantic_function_tool(CodeResponse, name="generate_code")

    async def process(self, query: str) -> CodeResponse:
        response = await self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": query}],
            tools=[self.tool],
        )

        resp = CodeResponse.model_validate_json(
            response.choices[0].message.tool_calls[0].function.arguments
        )
        print("code agent response", resp)

        js = response.choices[0].message.tool_calls[0].function.arguments
        args = json.loads(js)
        return CodeResponse(**args)


class ResearchAgent:
    def __init__(self, client: AsyncOpenAI):
        self.client = client

        self.tool = openai.pydantic_function_tool(
            ResearchResponse, name="explain_topic"
        )
        print("Calling ssss")

    async def process(self, query: str) -> ResearchResponse:
        print("RESEARCH sss", query)
        response = await self.client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": query}],
            tools=[self.tool],
        )
        return ResearchResponse.model_validate_json(
            response.choices[0].message.tool_calls[0].function.arguments
        )


class MultiAgentSystem:
    def __init__(self, api_key: str):
        client = AsyncOpenAI()  # Using AsyncOpenAI
        self.router = RouterAgent(client)
        self.code_agent = CodeAgent(client)
        self.research_agent = ResearchAgent(client)

    async def process_query(self, query: str) -> dict:
        route_response = None
        try:
            print("Multi Agent Call", query)
            route_response = await self.router.route(query)
            print("response", route_response)
            print(
                f"Router selected: {route_response.selected_agent} "
                f"(confidence: {route_response.confidence})"
            )

            # Process with appropriate agent
            if route_response.selected_agent == "CODE":
                response = await self.code_agent.process(query)
                return {
                    "type": "code",
                    "router": route_response.model_dump(),  # Include router response
                    "response": response.model_dump(),
                }
            else:
                response = await self.research_agent.process(query)
                print("RESPNSE inside multi agent", response)

                if response.needs_code_example:
                    code_response = await self.code_agent.process(
                        f"Write a simple example of {query}"
                    )
                    response.needs_code_example = False
                    return {
                        "type": "research",
                        "router": route_response.model_dump(),  # Include router response
                        "response": response.model_dump(),
                        "code_example": code_response.model_dump(),
                    }

                return {
                    "type": "research",
                    "router": route_response.model_dump(),  # Include router response
                    "response": response.model_dump(),
                }

        except Exception as e:
            return {
                "type": "error",
                "router": route_response.model_dump() if route_response else None,
                "error": str(e),
            }


async def main():
    system = MultiAgentSystem("your-api-key")

    queries = [
        "Write a hello world program in Python",
        "Explain what a hello world program is",
    ]

    responses = []
    for query in queries:
        result = await system.process_query(query)

        response = SystemResponse(
            query=query,
            type=result["type"],
            status="error" if result["type"] == "error" else "success",
            router=RouterResponse(
                **result["router"]
            ),  # Create RouterResponse from dict
            data=result,
            timestamp=datetime.now().isoformat(),
        )
        responses.append(response.model_dump())

    # Output JSON that can be consumed by other systems
    print(json.dumps({"responses": responses}, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
