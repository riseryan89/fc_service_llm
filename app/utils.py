from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory


store = {}


class InMemoryHistory(BaseChatMessageHistory, BaseModel):
    messages: list[BaseMessage] = Field(default_factory=list)

    def add_messages(self, messages: list[BaseMessage]) -> None:
        self.messages.extend(messages)

    def clear(self) -> None:
        self.messages = []


def get_by_session_id(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryHistory()
    return store[session_id]


def chat_with_openai(msg: str):
    api_key = ""

    llm = ChatOpenAI(
        temperature=0,
        openai_api_key=api_key,
        model_name="gpt-4o-mini",
        max_tokens=256,
        streaming=True
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", """
        당신은 JavaScript 전문가이자 챗봇입니다. 다음 규칙을 따라 답변해주세요:

        1. 앞으로 나올 모든 사용자 질문이 JavaScript와 직접적으로 관련이 있다면, 정확하고 자세한 답변을 제공하세요.
        2. 앞으로 나올 모든 사용자 질문이 JavaScript와 관련이 없지만 프로그래밍과 관련이 있다면, JavaScript와의 차이점을 간단히 설명하고 JavaScript에서 유사한 개념이나 기능을 소개해주세요. 단, 다른 프로그래밍 언어에 대해서는 대답하지 마세요.
        3. 앞으로 나올 모든 사용자 질문이 프로그래밍과 전혀 관련이 없다면, 정중하게 이 챗봇의 목적을 설명하고 JavaScript 관련 질문을 유도해주세요.
        4. 앞으로 나올 모든 사용자 질문의 의도가 불분명하다면, 추가적인 정보를 요청하세요.
        5. 어떤 경우에도 부적절하거나 비윤리적인 내용은 답변하지 마세요
        
        답변 형식:
        1. 개념 설명 (2-3문장)
        2. 코드 예제 (주석 포함, 최대 10줄)
        3. 주의사항 (1-2개)
        """),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])

    conversion = RunnableWithMessageHistory(
        prompt | llm,
        get_by_session_id,
        input_messages_key="input",
        history_messages_key="history"
    )

    for chunk in conversion.stream(
        {"input": msg},
        config={"configurable": {"session_id": "q1"}}
    ):
        yield chunk.content
