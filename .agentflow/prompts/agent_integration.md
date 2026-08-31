I want to integrate an agentic chatbot into this application. What an agentic chatbot is supposed to do is, based upon the user's query about the data and the database, analyze, figure out how to solve the problem, and write a SQL query or post query to be able to get the information, do calculations, etc., and give the user his or her required output. The agentic chatbot can and must have multiple different tools to do this, and also the agentic chatbot cannot do any write queries. It can only do read queries and calculations. It can have access to any sort of calculation tools, SQL read tools, etc., but it cannot write into the database.

The agentic chatbot should also not be dangerous or have malicious intent. If any user were to ask the agentic chatbot to do something malicious, it must block him off and cut him off right there and then.

The Agentic Chatbot will use the Google AI Studio provider and will be equipped with system prompts and some skills to be able to calculate or do its work properly. It is not a simple agent. It is definitely a graph architecture, like a graph agentic architecture.

For now, the agent will only be tested upon single queries. There is no need to maintain context for now. Later that might come up, but for now it's not important, so don't worry about it. The first thing that I'm just checking for is if it is able to answer the user's questions based upon running SQL calculations, whatever tools that you want to provide it.

You don't know the syntax for LangChain, so I provided a documentation file/GitHub repo which contains the documentation. It's large documentation, so I suggest traversing through the folder structure to look at how it is made or implemented. Based upon your requirements, look into the markdown files for the documentation, because if you were to load everything into your memory, it would fill up your context window by probably 30,000–50,000 tokens, I assume. Or you can deploy sub-agents whenever you require research and report back to the main agent when you are building this agent, so you can deploy sub-agents if you'd like.

After the agent is integrated, inform me, and every major step you must also inform me. Whenever creating the feature branch, you need to inform me when you need to approve an architecture. I want you to also come up and do some research about the architecture. Provide me a good architectural design, show it to me in a Mermaid graph, provide me three designs, and I'll approve the one that I like. And that you can integrate in the agent. You can then produce APIs for the agent, and then connect it to the front end and run the local host. Keep running the FastAPI in the background!


Link to the documentation repo folder "https://github.com/rajshauryadeveloper-coder/agent-coding-context-documentation/tree/ec07ee8b50d46cc7377fd945bc7a1e0a972d4c2e/langchain-docs"

here is the gemini api key = <SET_VIA_ENV_GEMINI_API_KEY>


Here is the model were using inside a snippet from ai studio 
```
# To run this code you need to install the following dependencies:
# pip install google-genai

import os
from google import genai
from google.genai import types


def generate():
    client = genai.Client(
        api_key=os.environ.get("GEMINI_API_KEY"),
    )

    model = "gemma-4-31b-it"
    contents = [
        types.Content(
            role="user",
            parts=[
                types.Part.from_text(text=""" """),
            ],
        ),
    ]
    tools = [
        types.Tool(googleSearch=types.GoogleSearch(
        )),
    ]
    generate_content_config = types.GenerateContentConfig(
        temperature=0.5,
        thinking_config=types.ThinkingConfig(
            thinking_level="HIGH",
        ),
        audio_transcription_config=types.AudioTranscriptionConfig(
        ),
        tools=tools,
    )

    for chunk in client.models.generate_content_stream(
        model=model,
        contents=contents,
        config=generate_content_config,
    ):
        if text := chunk.text:
            print(text, end="")

if __name__ == "__main__":
    generate()


```