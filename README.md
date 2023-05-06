# NotionGPT
NotionGPT, a practical tool built on top of ChatGPT large language model, make it your note-taking assistant!

# 简介
NotionGPT，一款一款ChatGPT大模型下游的实用工具，能够根据你的Notion笔记内容进行问题回答。

# 实现步骤
1. 通过官方API获取Notion笔记数据 (https://developers.notion.com/reference/intro)
2. 使用SnowNLP进行中文分句(https://github.com/isnowfy/snownlp)
3. 调用OPENAI的Emeddling API 进行句子Embedding (https://platform.openai.com/docs/api-reference/embeddings)
4. 使用Pinecone进行向量存储与查询
5. 构造prompt
6. 调用OPENAI的QA API 进行问题回答

# Stack
FastApi+Pinecone+0penai

# 使用
后面再写
