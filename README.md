# NotionGPT
NotionGPT, a practical tool built on top of ChatGPT large language model, make it your note-taking assistant!

# 简介
NotionGPT，一款ChatGPT大模型下游的实用工具，能够根据你的Notion笔记内容进行问题回答。

# 实现步骤
1. 通过官方API获取Notion笔记数据 (https://developers.notion.com/reference/intro)
2. 使用SnowNLP进行中文分句(https://github.com/isnowfy/snownlp)
3. 调用OPENAI的Emeddling API 进行句子Embedding (https://platform.openai.com/docs/api-reference/embeddings)
4. 使用Pinecone进行向量存储与查询
5. 构造prompt
6. 调用OPENAI的QA API 进行问题回答

# Tech Stack
Notion API:   get_database_content & page_content

SnowNLP: chinese sentence segmentation

Pinecone: vectorDB- personal knowledge DB- upsert & query

OpenAI: sentence embedding & prompt QA

FastAPI:  Frontend web UI


# Usage
Notion： data_base_id & auth_token

Pinecone: pinecone api key & pinecone env_name (proxy needed)

OpenAI: openai api key

Fill in code and start using

