import logging
import os
import openai
from pydantic import BaseModel
from openai import AzureOpenAI

# ENVIRONMENT VARIABLES
AOAI_CHAT_DEPLOYMENT = os.getenv("AOAI_CHAT_DEPLOYMENT")

print("API_VERSION=", os.getenv("AOAI_API_VERSION"))

class AzureOpenAIService:

    def __init__(self) -> None:
        self.openai = AzureOpenAI(
            api_key=os.getenv("AOAI_API_KEY"),
            api_version=os.getenv("AOAI_API_VERSION"),
            azure_endpoint=os.getenv("AOAI_ENDPOINT")
        )
        
    def getEmbedding(self, input) -> list:
        """ベクトル値を取得する。
        Args:
            input (_type_): ベクトル化する文字列

        Returns:
            list: ベクトル値
        """
                
        # printデバッグ追加
        print("AOAI_EMBEDDING_DEPLOYMENT=", os.getenv("AOAI_EMBEDDING_DEPLOYMENT"))
        
        try:
            response = self.openai.embeddings.create(
                input=input,
                model=os.getenv("AOAI_EMBEDDING_DEPLOYMENT")
            )
            return response.data[0].embedding
        except Exception as e:
            logging.error(f'❌Error at getEmbedding: {e}')
            raise e
