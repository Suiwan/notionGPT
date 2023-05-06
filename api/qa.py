import openai

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


def chat_complete(prompt):
    # query gpt-3.5-turbo， 这个模型更便宜
    res = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.2,
        max_tokens=200,
    )
    return res['choices'][0].message
