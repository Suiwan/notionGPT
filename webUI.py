# -*- coding: utf-8 -*-
# @Author  : Zijian li
# @Time    : 2023/5/6 12:49

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from api.build_pinecone import init_pinecone
from api.qa import retrieve, complete, chat_complete,chain_of_thought,search_in_chain,chain_of_keyword
import json
from api.util import check_usage

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Define a message model to be used in the API
class Message(BaseModel):
    message: str


index = init_pinecone()
# index=0

@app.post('/api/chat')
async def chat(request: Request, message: Message):

    # Get the user's message from the request
    query = message.message
    print("query: ",query)
    final_answer = ""
    # get selected option from url
    option = request.query_params.get('option')
    print("selected option: ",option)
    # options: Common_Prompt, Chain_of_Thought, Search_in_Chain
    # # get prompt from query and pinecone
    if option == 'Common_Prompt':
        prompt = retrieve(query, index)
        print("prompt: ",prompt)
    elif option == 'Chain_of_Thought':
        prompt = chain_of_thought(query, index)
    elif option == "Search_in_Chain":
        final_answer = search_in_chain(query)
        print("final_answer: ",final_answer)
        # 将final_answer中的\n替换成<br>
        final_answer = final_answer.replace('\n', '<br>')
        return JSONResponse({'response': final_answer})
    else:
        prompt = chain_of_keyword(query,index)
    # get response
    response = chat_complete(prompt)['content']

    # convert unicode content to utf-8
    res_json = json.dumps(response, ensure_ascii=False)

    # 去掉res_json两侧的引号
    res_json = res_json[1:-1]
    # res_json = "这是回答"
    # 去掉res_json中多余的\n
    res_json = res_json.replace('\\n', '')

    return JSONResponse({'response': res_json})


@app.get("/")
async def home(request: Request):
    # check_usage()
    return templates.TemplateResponse("index.html", {"request": request})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=9090)
