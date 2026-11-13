from openai import AzureOpenAI
from dotenv import load_dotenv
import os

#load_dotenv()
load_dotenv("C:/Users/藤上忍/Documents/rag/chatapp/.env")

print("API_KEY=", repr(os.getenv("AOAI_API_KEY")))
print("ENDPOINT=", repr(os.getenv("AOAI_ENDPOINT")))
print("API_VERSION=", repr(os.getenv("AOAI_API_VERSION")))

print("start")

client = AzureOpenAI(
    api_key=os.getenv("AOAI_API_KEY"),
    api_version="2024-10-21",
    azure_endpoint="https://sfujikami-6631-resource.services.ai.azure.com"
)

response = client.chat.completions.create(
    model="gpt-4.1-mini-1",
    messages=[
        {"role": "user", "content": "こんにちは"}
    ]
)

print(response.choices[0].message.content)