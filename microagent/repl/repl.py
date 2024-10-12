import json
from typing import Dict, Any

from swarm import Swarm

def process_and_print_streaming_response(response):
    content = ""
    last_sender = ""

    for chunk in response:
        if "sender" in chunk:
            last_sender = chunk["sender"]

        if "content" in chunk and chunk["content"] is not None:
            if not content and last_sender:
                print(f"\033[94m{last_sender}:\033[0m", end=" ", flush=True)
                last_sender = ""
            print(chunk["content"], end="", flush=True)
            content += chunk["content"]

        if "tool_calls" in chunk and chunk["tool_calls"] is not None:
            for tool_call in chunk["tool_calls"]:
                f = tool_call["function"]
                name = f["name"]
                if not name:
                    continue
                print(f"\033[94m{last_sender}: \033[95m{name}\033[0m()")

        if "delim" in chunk and chunk["delim"] == "end" and content:
            print()  # End of response message
            content = ""

        if "response" in chunk:
            return chunk["response"]

def pretty_print_messages(messages: List[Dict[str, Any]]) -> None:
    for message in messages:
        if message["role"] != "assistant":
            continue

        print(f"\033[94m{message['sender']}\033[0m:", end=" ")

        if message["content"]:
            print(message["content"])

        tool_calls = message.get("tool_calls") or []
        if len(tool_calls) > 1:
            print()
        for tool_call in tool_calls:
            f = tool_call["function"]
            name, args = f["name"], f["arguments"]
            arg_str = json.dumps(json.loads(args)).replace(":", "=")
            print(f"\033[95m{name}\033[0m({arg_str[1:-1]})")

def run_demo_loop(
    starting_agent, context_variables=None, stream=False, debug=False, llm_type='openai'
) -> None:
    client = Swarm(llm_type=llm_type)
    print(f"Starting Swarm CLI 🐝 using {llm_type.capitalize()} LLM")

    messages = []
    agent = starting_agent

    while True:
        user_input = input("\033[90mUser\033[0m: ")
        messages.append({"role": "user", "content": user_input})

        response = client.run(
            agent=agent,
            messages=messages,
            context_variables=context_variables or {},
            stream=stream,
            debug=debug,
        )

        if stream:
            response = process_and_print_streaming_response(response)
        else:
            pretty_print_messages(response.messages)

        messages.extend(response.messages)
        agent = response.agent

if __name__ == "__main__":
    from swarm.agents import get_default_agent
    
    llm_type = input("Enter LLM type (openai/anthropic/groq/gemini): ").lower()
    agent = get_default_agent()
    run_demo_loop(agent, stream=True, debug=True, llm_type=llm_type)