import json
import re
import time

import openai

from api.util import get_embedding

delay = 20  # avoid rate limit error
limit = 3750


def retrieve(query, index):
    res = openai.Embedding.create(
        input=[query],
        engine="text-embedding-ada-002"
    )

    # retrieve from Pinecone
    xq = res['data'][0]['embedding']

    # get relevant contexts
    res = index.query(xq, top_k=5, include_metadata=True)
    contexts = [
        x['metadata']['original_text'] for x in res['matches']
    ]

    # todo: show knowledge on UI

    # build our prompt with the retrieved contexts included
    prompt_start = (
            "请你基于以下信息回答我的问题.如果你对以下信息有深刻了解，你也可以进行补充，但是主体内容需要基于以下的信息.\n\n" +
            "信息:\n"
    )
    prompt_end = (
        f"\n\n问题: {query}\n回答:"
    )
    # append contexts until hitting limit
    for i in range(1, len(contexts)):
        if len("\n\n---\n\n".join(contexts[:i])) >= limit:
            prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts[:i - 1]) +
                    prompt_end
            )
            break
        elif i == len(contexts) - 1:
            prompt = (
                    prompt_start +
                    "\n\n---\n\n".join(contexts) +
                    prompt_end
            )
    return prompt


def chain_of_thought(query, index):
    res = openai.Embedding.create(
        input=[query],
        engine="text-embedding-ada-002"
    )

    # <>做标识
    # total embedding
    xq = res['data'][0]['embedding']

    # get relevant contexts
    res = index.query(xq, top_k=5, include_metadata=True)
    contexts = [
        x['metadata']['original_text'] for x in res['matches']
    ]

    # build our prompt with the retrieved contexts included
    prompt_start = (
            "Please answer my question based on your query about the question and the information I provide (which I will put inside angle brackets:<>) and follow the format like the examples provided below and explain how you think step by step.(Notice: your final answer should be in Chinese but still follow the format of explain)"
            "like: step1:.... step2:....\n\n" +
            "information:\n" + "<" + "\n\n---\n\n".join(contexts) + ">\n"
    )
    content = "example:[Question]: STEM教育与工程教育的相同之处是什么？\n" \
              "[Answer]:let's think step by step.\n" \
              "step1.  STEM课程的要素是：- 真实的，可以激发学生兴趣的问题/与工程有关的挑战,- 学生可以与问题建立联系- 允许学生使用多种可接受的，有创意的方式来解决问题- 整合并应用重要的科学和数学相应年级中的内容,- 将工程设计过程作为解决问题的方法- 使用以学生为中心的实践教学和学习方法\n" \
              "step2. 工程教育的要素是：- 定义问题：- 背景研究- 想象- 计划- 创造- 测试与评估- 重新设计- 交流\n" \
              "step3. 因此二者的相同点在于：问题和背景都与工程有关，都需要学生想象和创造性解决问题，需要遵循工程设计过程作为解决问题的方法……"
    prompt_end = (
        f"\n\n[Question]: {query}\n[Answer]:"
    )
    prompt = prompt_start + content + prompt_end
    # prevent prompt from exceeding limit
    if len(prompt) > limit:
        prompt = prompt[:limit]

    return prompt


def get_pinecone_information(keyword,query,index):
    time.sleep(1)
    xq = get_embedding(query)
    # search
    res = index.query(xq, top_k=5, include_metadata=True)
    contexts = [
        x['metadata']['original_text'] for x in res['matches']
    ]
    # create information
    information = ""
    for i in range(len(contexts)):
        information += f"[Info of Keyword <{keyword}> {i+1}]: {contexts}\n"
    return information

def get_keywords_of_query(query):
    # query = "知识图谱和语义网之间的区别是什么"
    prompt = f"<{query}>这句话的关键词有哪些？请以[keyword 1]、[keyword 2]、[keyword 3]的格式回答，例如：[keyword 1]: 知识图谱，[keyword 2]: 语义网\n注意：你回答的关键词最好是以名词为主，例如：知识图谱，语义网，而不是：构建，有关等等"
    res = chat_complete(prompt)
    comp_json = json.dumps(res, ensure_ascii=False)
    content = re.findall(r'"content": "(.*?)"', comp_json)
    text = content[0]
    # get the keywords
    keywords = re.findall(r'\[keyword \d+\]:\s(.*?)(?:，|$)', text)
    print(keywords)
    return keywords


def chain_of_keyword(query,index):
    keywords = get_keywords_of_query(query)
    prompt = f"Answer the Question by referring your query to the search engine based on what you already know and the [Query]-[Infos] pairs of chain of keyword that I provided for you\n (Notice: you should finish your answer in chinese)"
    CoK = ""
    for i in range(len(keywords)):
        q = f"What is {keywords[i]}?"
        CoK += f"[Query {i+1}]: {q}\n"
        information = get_pinecone_information(keywords[i],q,index)
        CoK += f"[Infos {i+1}]: {information}\n"
    prompt += "Chain of Keyword:\n" + CoK + f"[Question]: {query}\n[Answer] :"
    return prompt

def answer_question(query):
    prompt = retrieve(query)
    res = chat_complete(prompt, delay=delay)
    comp_json = json.dumps(res, ensure_ascii=False)
    content = re.findall(r'"content": "(.*?)"', comp_json)
    answer = content[0]
    return answer


# todo search in chain retrieve
# a veeeeeery simple implementation of search in chain. not as good as the one in the paper
def search_in_chain(query):
    import json
    import re
    from tqdm.auto import tqdm
    limit = 5
    prompt = f"""Construct an reasoning chain for this multi-hop question [Question]: {query}
    You should generate a query to the search engine based on what you already know at each step of the reasoning chain, starting with [Query].
    If you know the answer for [Query], generate it starting with [Answer].
    You can try to generate the final answer for the [Question] by referring the [Query]-[Answer] pairs, starting with [Final Content].
    If you don't know the answer, generate a query to search engine based on what you already know and do not know, starting with [Unsolved Query]. When you have finished the Unsolved Query, stop the reasoning chain and reply I will give you some information to help you finish the reasoning chain.
    Note:you should finish the reasoning chain in chinese
    For example:
    [Question]: Where do greyhound buses leave from in the birthplace of Spirit If...'s performer?
    [Query 1]: Who is the performer of Spirit If... ?
    If you don't know the answer:
    [Unsolved Query]: Who is the performer of Spirit If... ?
    If you know the answer:
    [Answer 1]: The performer of Spirit If… is Kevin Drew.
    [Query 2]: Where was Kevin Drew born?
    If you don't know the answer:
    [Unsolved Query]: Where was Kevin Drew born?
    If you know the answer:
    [Answer 2]: Toronto.
    [Query 3]: Where do greyhound buses in Toronto leave from?
    If you don't know the answer:
    [Unsolved Query]: Where do greyhound buses in Toronto leave from?
    If you know the answer:
    [Answer 3]: Toronto Coach Terminal.
    [Final Content]: The performer of Spirit If… is Kevin Drew [1]. Kevin Drew was born in Toronto [2]. Greyhound buses in Toronto leave from Toronto
    Coach Terminal [3]. So the final answer is Toronto Coach Terminal.
    Notice: You should follow the format of the example above strictly."""
    final_answer = ""
    for _ in tqdm(range(limit)):
        res = chat_complete(prompt, delay)
        comp_json = json.dumps(res, ensure_ascii=False)
        content = re.findall(r'"content": "(.*?)"', comp_json)
        print(content[0])
        content_text = content[0]
        # 如果content中包括[Unresolved Query]，则需要pinecone查相关的信息
        if "[Unsolved Query]" in content_text:
            # get the unsolved query
            pattern = r'\[Unsolved Query\]: (.*?)\\n'
            unsolved_queries = re.findall(pattern, content_text)
            print("unsolved query", unsolved_queries)
            for i in range(len(unsolved_queries)):
                # print(f"[Unsolved Query]: {unsolved_queries[i]}")
                unsolved_query = unsolved_queries[i]
                # 在unresolved query的下一行接上[Answer]:answer
                prompt += f"According to the Reference, the answer for {unsolved_query} should be {answer_question(unsolved_query)}, you can give your answer and continue constructing the reasoning chain for [Question] ”`"
        else:
            final_answer = content_text
            break
    return final_answer


def complete(prompt):
    print("completing prompt...")
    # query text-davinci-003
    res = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        temperature=0.2,
        max_tokens=400,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0,
        stop=None
    )
    print("done!")
    return res['choices'][0]['text'].strip()


def chat_complete(prompt, delay=0):
    # query gpt-3.5-turbo， 这个模型更便宜
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
    )
    time.sleep(delay)
    return res['choices'][0].message
