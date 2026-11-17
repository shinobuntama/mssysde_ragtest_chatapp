import streamlit as st
from streamlit_chat import message
# from dotenv import load_dotenv
import os

# 一時的にインポート

from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AOAI_API_KEY"),
    api_version=os.getenv("AOAI_API_VERSION"),
    azure_endpoint=os.getenv("AOAI_ENDPOINT")
)

print(client)

# load_dotenv("C:/Users/藤上忍/Documents/rag/chatapp/.env")

print(os.getenv("AOAI_CHAT_DEPLOYMENT"))
print(os.getenv("AOAI_ENDPOINT"))

from openai_service import AzureOpenAIService
from cosmos_service import CosmosService

# ENVIRONMENT VARIABLES
AOAI_CHAT_DEPLOYMENT = os.getenv("AOAI_CHAT_DEPLOYMENT")
VECTOR_SCORE_THRESHOLD = float(os.getenv("VECTOR_SCORE_THRESHOLD"))

# PROMPT SETUP
system_prompt_chat = """あなたはAIアシスタントです。問い合わせに対し「# 検索結果」の内容をもとに回答してください。

# 制約条件
- 検索結果がない場合は、一般的な情報から回答できる場合は回答してください。回答できない場合は不明瞭な回答をしてはいけません。
- 構造的に回答する必要がある場合は、Markdownで構造的に回答してください。
- チャット履歴の「参考情報」は無視してください。
- 「参考情報」はシステムが自動で付与しています。あなたの回答に含めてはいけません。
"""

# Client
aoai_service = AzureOpenAIService()
cosmos_service = CosmosService()

st.set_page_config(layout="wide")
st.title("🚀RAG テストサイトver2.4 VC="+ str(VECTOR_SCORE_THRESHOLD) )

# SESSION MANAGEMENT
if "chat_messages" not in st.session_state:
    st.session_state["chat_messages"] = []

# SIDEBAR SETUP
clear_button = st.sidebar.button("Clear Conversation", key="clear")
if clear_button:
    st.session_state["chat_messages"] = []


user_message = st.chat_input("質問を入力してください")

# AIからの回答
assistant_text = ""

# 過去のチャットメッセージを表示
for text_info in st.session_state["chat_messages"]:
    with st.chat_message(text_info["role"], avatar=text_info["role"]):
        st.write(text_info["content"])

# ユーザーの入力がある場合
if user_message:
    # ユーザーの入力を表示
    with st.chat_message("user", avatar="user"):
        st.markdown(user_message)

    # ユーザーの入力をchat_messagesに追加
    st.session_state["chat_messages"].append(
        {"role": "user", "content": user_message})

    # CosmosDBでベクトル検索
    search_items = cosmos_service.get_items_by_vector(
        aoai_service.getEmbedding(
            input=user_message
        ),
        VECTOR_SCORE_THRESHOLD
    )

    # AIからの回答を生成する処理をここに追加する
    # システムメッセージに検索結果を追加
    system_message = system_prompt_chat + "\n\n# 検索結果"   # OpenAIリクエスト用のメッセージ

    # 画面に表示する検索結果
    display_searched_file_name = "\n\n---\n #### 参考情報"
    
    for index, result in enumerate(search_items):
        # ループ番号を付与してファイルの内容をシステムメッセージに追加
        system_message += f'\n\n--- {index + 1} ---\n{result["content"]}'
        # 画面に表示する検索結果を追加
        display_searched_file_name += f'\n{index + 1}. {result["file_name"]}  (page{result["page_number"]})  : {result["SimilarityScore"]}'
#        display_searched_file_name += f'\n{index + 1}. {result["file_name"]}  (page{result["page_number"]})'
    print(f"system_message: {system_message}")

    # OpenAIリクエスト用のメッセージ
    messages = [
        {"role": "system", "content": system_message},
        *st.session_state["chat_messages"],
    ]
    
    print("DEPLOYMENT=", AOAI_CHAT_DEPLOYMENT)
    print("ENDPOINT=", os.getenv("AOAI_ENDPOINT"))
    print("MESSAGES=", messages)
    print("type=", type(messages))

    client = AzureOpenAI(
        api_key=os.getenv("AOAI_API_KEY"),
        api_version=os.getenv("AOAI_API_VERSION"),
        azure_endpoint=os.getenv("AOAI_ENDPOINT")
    )
    
    # print("API_KEY=", repr(os.getenv("AOAI_API_KEY")))
    # print("ENDPOINT=", repr(os.getenv("AOAI_ENDPOINT")))
    print("API_VERSION=", repr(os.getenv("AOAI_API_VERSION")))
    print("DEPLOYMENT=", repr(AOAI_CHAT_DEPLOYMENT))

#    response = client.chat.completions.create(
#        model="gpt-4.1-mini-1",
#        messages=[
#            {
#                "role": "user",
#                "content": "こんにちは"
#            }
#        ]
#    )
#    print(response.choices[0].message.content)
    
    response = client.chat.completions.create(
        model=AOAI_CHAT_DEPLOYMENT,
        messages=messages
    )
    
    print(response.choices[0].message.content)
    
    # OpenAI Chat APIで回答を取得
    #response = aoai_service.openai.chat.completions.create(
    #    model=AOAI_CHAT_DEPLOYMENT,
    #    messages=messages,
    #    stream=True,
    #)    

    with st.chat_message("assistant", avatar="assistant"):
        place_assistant = st.empty()
        
        #for chunk in response:
        #    if chunk.choices:
        #        content = chunk.choices[0].delta.content
        #        if content:
        #            assistant_text += content
        #            place_assistant.write(assistant_text)
        #        else:
        #            content = None                    
        
        assistant_text = response.choices[0].message.content
        # 参考情報を表示すると、関係ない文書が出るので削除⇒もどし
        st.write(assistant_text + display_searched_file_name)
#        st.write(assistant_text)
        
    # AIの回答をchat_messagesに追加
    st.session_state["chat_messages"].append(
        {"role": "assistant", "content": assistant_text}
    )
