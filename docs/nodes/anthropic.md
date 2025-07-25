# Workflow setup

## Curl command:
```bash
curl https://api.anthropic.com/v1/messages \
     --header "x-api-key: $ANTHROPIC_API_KEY" \
     --header "anthropic-version: 2023-06-01" \
     --header "content-type: application/json" \
     --data \
'{
    "model": "claude-opus-4-20250514",
    "max_tokens": 1024,
    "messages": [
        {"role": "user", "content": "Hello, world"}
    ]
}'

```
**Output:**
```json
{"id":"msg_01FwErskQLwz9RvaaHYxUA67","type":"message","role":"assistant","model":"claude-opus-4-20250514","content":[{"type":"text","text":"Hello! Welcome to our conversation. How are you doing today? Is there anything specific you'd like to talk about or any questions I can help you with?"}],"stop_reason":"end_turn","stop_sequence":null,"usage":{"input_tokens":10,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":35,"service_tier":"standard"}}     
```

## Create a connector

Name: Anthropic
Base URL: https://api.anthropic.com/v1
Method: POST
Headers:
```json
{
    "x-api-key": "your_anthropic_api_key",
    "anthropic-version": "2023-06-01",
    "content-type": "application/json"
}
```

## Create a node
Name: Anthropic Chat
Description: Anthropic's Claude Opus 4 chat model for conversational AI.
Connector: Anthropic
Path: /messages
Body Template:
```json
{
  "model": "$model",
  "max_tokens": "$max_tokens",
  "messages": [
    {
      "role": "$messages.0.role",
      "content": "$messages.0.content.0"
    }
  ]
}
```
Note: This template handles the case where content is sent as an array of strings and converts it to the proper Anthropic format. For multiple messages or more complex content, adjust the template accordingly.

Alternative simpler template (if content is already a string):
```json
{
  "model": "$model",
  "max_tokens": "$max_tokens",
  "messages": "$messages"
}
```
Input Schema:
```json
[
    {
        "name": "model",
        "type": "string",
        "description": "The model to use for the chat, e.g., 'claude-opus-4-20250514'",
        "default": "claude-opus-4-20250514"
    },
    {
        "name": "max_tokens",
        "type": "integer",
        "description": "Maximum number of tokens in the response",
        "default": 1024
    },
    {
        "name": "messages",
        "type": "array",
        "description": "List of messages in the conversation",
        "items": {
            "type": "object",
            "properties": {
                "role": {
                    "type": "string",
                    "description": "Role of the message sender (e.g., 'user', 'assistant')"
                },
                "content": {
                    "type": ["string", "array"],
                    "description": "Content of the message, can be text or an array of text segments"
                }
            }
        },
        "default": [{"role": "user", "content": "Hello, world"}]
    }
]
```

Output Schema:
```json
[
    {
        "name": "id",
        "type": "string",
        "description": "Unique identifier for the message"
    },
    {
        "name": "type",
        "type": "string",
        "description": "Type of the message, e.g., 'message'"
    },
    {
        "name": "role",
        "type": "string",
        "description": "Role of the message sender, e.g., 'assistant'"
    },
    {
        "name": "model",
        "type": "string",
        "description": "Model used for generating the response"
    },
    {
        "name": "content",
        "type": ["string", "array"],
        "description": "Content of the response message"
    },
    {
        "name": "stop_reason",
        "type": ["string", null],
        "description": "Reason for stopping the response generation"
    },
    {
        "name": "stop_sequence",
        "type": ["string", null],
        "description": "Sequence that indicates where the response stopped"
    },
    {
        "name": "usage",
        "type": {
            "input_tokens": {"type": "integer"},
            "cache_creation_input_tokens": {"type": "integer"},
            "cache_read_input_tokens": {"type": "integer"},
            "output_tokens": {"type": "integer"},
            "service_tier": {"type": ["string", null]}
        },
        "description": "Token usage statistics for the request"
    }
]
```
