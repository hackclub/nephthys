from os import environ
from typing import Any
from typing import Literal
from typing import NotRequired
from typing import TypedDict

import httpx
import openai.resources
from openai import AsyncOpenAI

type StructuredGuidance = str | dict[str, Any] | list[Any]


class NoulCriteria(TypedDict):
    true: StructuredGuidance
    false: StructuredGuidance


class NoulQuestion(TypedDict):
    type: Literal["noul"]
    instructions: StructuredGuidance
    criteria: NotRequired[NoulCriteria]


class ChoiceQuestion(TypedDict):
    type: Literal["choice"]
    instructions: StructuredGuidance
    criteria: dict[str, StructuredGuidance | None]


class ScoreQuestion(TypedDict):
    type: Literal["score"]
    instructions: StructuredGuidance
    criteria: list[StructuredGuidance]


type DecisionQuestion = NoulQuestion | ChoiceQuestion | ScoreQuestion


class NoulAnswer(TypedDict):
    type: Literal["noul"]
    noul: float


class ChoiceAnswer(TypedDict):
    type: Literal["choice"]
    choice: str
    confidence: NotRequired[float]
    probabilities: NotRequired[dict[str, float]]


class ScoreAnswer(TypedDict):
    type: Literal["score"]
    score: float
    confidence: NotRequired[float]
    legend: NotRequired[dict[str, StructuredGuidance]]
    probabilities: NotRequired[dict[str, float]]


type DecisionAnswer = NoulAnswer | ChoiceAnswer | ScoreAnswer


class DecisionsUsage(TypedDict):
    input_tokens: int
    output_tokens: int
    cost: NotRequired[float]


class DecisionsResponse(TypedDict):
    model: str
    answers: dict[str, DecisionAnswer]
    usage: DecisionsUsage
    id: NotRequired[str]
    provider: NotRequired[str]


class AIClient:
    """Base AI client class

    All AI clients must be able to provide an OpenAI async chat interface"""

    def __init__(self, client: AsyncOpenAI):
        self.openai_client = client

    @property
    def chat(self) -> openai.resources.AsyncChat:
        return self.openai_client.chat


class OpenRouterClient(AIClient):
    def __init__(
        self,
        api_key: str,
        base_url: str = "https://openrouter.ai/api/v1",
        referrer_title: str | None = None,
        referrer_url: str | None = None,
    ):
        headers = {}
        if referrer_title:
            headers["X-OpenRouter-Title"] = referrer_title
        if referrer_url:
            headers["HTTP-Referer"] = referrer_url
        openai_client = AsyncOpenAI(
            api_key=api_key,
            base_url=base_url,
            default_headers=headers,
        )
        super().__init__(openai_client)
        self.base_url = base_url
        self.api_key = api_key
        self.referrer_url = referrer_url
        self.referrer_title = referrer_title
        self.http_client = httpx.AsyncClient(
            base_url=httpx.URL(base_url).copy_with(path="/"),
            headers={"Authorization": f"Bearer {api_key}", **headers},
        )

    async def decisions(
        self,
        model: str,
        state: str | dict | list,
        questions: dict[str, DecisionQuestion],
    ) -> DecisionsResponse:
        response = await self.http_client.post(
            "/api/alpha/decisions",
            json={"model": model, "state": state, "questions": questions},
        )
        response.raise_for_status()
        data: DecisionsResponse = response.json()
        return data


def get_ai_client_from_environment() -> AIClient | None:
    generic_api_key = environ.get("AI_API_KEY")
    generic_base_url = environ.get("AI_BASE_URL")
    hcai_api_key = environ.get("HACK_CLUB_AI_API_KEY")
    hcai_base_url = environ.get(
        "HACK_CLUB_AI_BASE_URL", "https://ai.hackclub.com/proxy/v1"
    )
    openrouter_api_key = environ.get("OPENROUTER_API_KEY")
    openrouter_base_url = environ.get(
        "OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"
    )
    if openrouter_api_key:
        return OpenRouterClient(
            api_key=openrouter_api_key, base_url=openrouter_base_url
        )
    if hcai_api_key:
        return AIClient(AsyncOpenAI(api_key=hcai_api_key, base_url=hcai_base_url))
    if generic_api_key:
        if not generic_base_url:
            raise ValueError("AI_BASE_URL must be set if AI_API_KEY is set")
        return AIClient(AsyncOpenAI(api_key=generic_api_key, base_url=generic_base_url))
    return None


ai_client: AIClient | None = get_ai_client_from_environment()
