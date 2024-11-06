### Simple example of using  plain routing 
# 1) Routing Agent
# 2) Code Agent
# 3) Research Agent
# 
# The response if in json in case we need other systems to use it.


```{
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
