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
from queue import Queue
import param
from typing import Any, AsyncIterator, Dict, List, Literal, Union, cast
from langchain.callbacks.base import AsyncCallbackHandler
from langchain.schema.agent import AgentAction, AgentFinish
from langchain.schema.output import LLMResult


class CustomAsyncCallbackHandler(AsyncCallbackHandler):
    """
    Streaming callback handler that returns an async iterator. This supports
    both streaming llm and agent executors.

    :param is_agent: Whether this is an agent executor.
    """

    queue: asyncio.Queue[str]
    done: asyncio.Event

    @property
    def always_verbose(self) -> bool:
        return True

    def __init__(self, is_agent: bool = True) -> None:
        self.queue = asyncio.Queue()
        self.done = asyncio.Event()
        self.is_agent = is_agent

    async def on_llm_start(
        self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        print("================== LLM Start! ==========================")
        self.done.clear()

    async def on_llm_new_token(self, token: str, **kwargs: Any) -> None:
        if token is not None and token != "":
            self.queue.put_nowait(token)

    async def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """
        Do not close the queue here, as it may be used by the agent.
        """
        if not self.is_agent:
            self.done.set()
        else:
            print("================== LLM finished! ==========================")
            print(response)
            generation_info = response.generations[-1][-1].generation_info
            if generation_info is not None:
                print(
                    "================== LLM finish reason! =========================="
                )
                # Figured out through trial and error
                if generation_info.get("finish_reason") == "stop":
                    self.done.set()

    async def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        if not self.is_agent:
            self.done.set()

    # async def on_agent_action(self, action: AgentAction, **kwargs: Any) -> None:
    #     """Run on agent action."""
    #     print("================== AGent Start! ==========================")
    #     self.done.clear()

    # async def on_agent_finish(self, finish: AgentFinish, **kwargs: Any) -> None:
    #    """Run on agent end."""
    #    self.done.set()

    # async def on_chain_start(
    #    self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    # ) -> None:
    #    self.done.clear()

    # async def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
    #    """Run when chain ends running."""
    #   self.done.set()

    async def aiter(self) -> AsyncIterator[str]:
        """
        Returns an async iterator that yields tokens from the LLM.
        """
        while not self.queue.empty() or not self.done.is_set():
            # Wait for the next token in the queue or for the done event to be set
            done, other = await asyncio.wait(
                [
                    asyncio.ensure_future(self.queue.get()),
                    asyncio.ensure_future(self.done.wait()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )

            # Cancel the other task
            if other:
                other.pop().cancel()

            # Extract the value of the first completed task
            token_or_done = cast(Union[str, Literal[True]], done.pop().result())

            # If the extracted value is the boolean True, the done event was set
            if token_or_done is True:
                break

            # Otherwise, the extracted value is a token, which we yield
            yield token_or_done


class cbfs (param.Parameterized):
    def __init__(self, tools, chat_history, **params):
        super(cbfs,self).__init__(**params)
        retrieve_from_db = json.loads(chat_history)
        retrieved_messages = messages_from_dict(retrieve_from_db)
        self.functions = [format_tool_to_openai_function(f) for f in tools]
        self.model = ChatOpenAI(temperature=0.2, streaming=True, callbacks=[CustomAsyncCallbackHandler()], verbose=True).bind(functions = self.functions)
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
            print(i + '.')
        await task
    
    def send_mess(self, query:str, stream_it):
        self.qa.callbacks = [stream_it]
        return self.qa.invoke({"input": query})
        