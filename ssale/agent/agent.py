from langchain.agents.format_scratchpad import format_to_openai_functions
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.tools.render import format_tool_to_openai_function
from langchain.agents.output_parsers import OpenAIFunctionsAgentOutputParser
from langchain.prompts import MessagesPlaceholder
from langchain.schema.runnable import RunnablePassthrough
from langchain.agents import AgentExecutor
from langchain.memory import ConversationBufferMemory
from langchain.memory import ChatMessageHistory
from langchain.schema import messages_from_dict, messages_to_dict
from langchain.callbacks.streaming_aiter import AsyncIteratorCallbackHandler
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from typing import Any
import json
import asyncio
from langchain.schema import LLMResult
from queue import Queue
import param
from typing import AsyncIterable

class AsyncCallbackHandler(AsyncIteratorCallbackHandler):
    content: str = ""
    final_answer: bool = False
    
    def __init__(self) -> None:
        super().__init__()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        self.content += token
        # if we passed the final answer, we put tokens in queue
        if self.final_answer:
            if '"action_input": "' in self.content:
                if token not in ['"', "}"]:
                    self.queue.put_nowait(token)
        elif "Final Answer" in self.content:
            self.final_answer = True
            self.content = ""
    
    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        if self.final_answer:
            self.content = ""
            self.final_answer = False
            self.done.set()
        else:
            self.content = ""


class cbfs (param.Parameterized):
    def __init__(self, tools, chat_history, **params):
        super(cbfs,self).__init__(**params)
        retrieve_from_db = json.loads(chat_history)
        retrieved_messages = messages_from_dict(retrieve_from_db)
        self.functions = [format_tool_to_openai_function(f) for f in tools]
        self.model = ChatOpenAI(temperature=0.2, streaming=True, callbacks=[]).bind(functions = self.functions)
        self.memory = ConversationBufferMemory(return_messages=True,memory_key="chat_history", chat_memory=ChatMessageHistory(messages=retrieved_messages))
        self.prompt = ChatPromptTemplate.from_messages([
    ("system", "You are helpful but sassy assistant"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad")
])      
        self.chain = RunnablePassthrough.assign(
            agent_scratchpad = lambda x: format_to_openai_functions(x['intermediate_steps'])
        ) | self.prompt |self.model |OpenAIFunctionsAgentOutputParser()

        self.qa = AgentExecutor(agent=self.chain, 
                                tools=tools, verbose=True,
                                memory=self.memory, 
                                return_intermediate_steps=False, 
                                max_iterations=3, 
                                early_stopping_method="generate",
                                )
    
    def covchain(self, query):
        if not query:
            return
        result = self.qa.invoke({"input": query})
        self.answer = result['output'] 
        return self.answer
    
    def take_history(self):
        extracted_messages = self.qa.memory.chat_memory.messages
        ingest_to_db = messages_to_dict(extracted_messages)
        return json.dumps(ingest_to_db)
    
    def clear_history(self,count=0):
        self.qa.memory.chat_memory = []
        return 
    
    async def run_call(self, query:str, stream_it):
        response = self.qa.acall({"input": query}, callbacks=[stream_it])
        return response

    async def send_message(self, query: str, stream_it):
        self.qa.callbacks=[stream_it]
        print(self.qa.callbacks)
        task = asyncio.create_task(self.qa.acall({"input": query}, callbacks=[stream_it]))
        async for i in stream_it.aiter():
            yield i
        await task
    
    def send_mess(self, query:str, stream_it):
        self.qa.callbacks = [stream_it]
        return self.qa.invoke({"input": query})
        