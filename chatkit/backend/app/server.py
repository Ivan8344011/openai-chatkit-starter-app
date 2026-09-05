"""ChatKit server that streams responses from a single assistant."""

from __future__ import annotations

from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import AgentContext, simple_to_agent_input, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from .memory_store import MemoryStore
from agents import Agent


MAX_RECENT_ITEMS = 30
MODEL = "gpt-4.1-mini"


assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model=MODEL,
    name="Charles",
    instructions=(
    "You are Charles, a friendly and practical AI assistant for everyday life. "
    "Use clear, natural, conversational language and avoid unnecessary technical jargon. "
    "When explaining how to do something, give simple step-by-step instructions in a logical order. "
    "Do not overwhelm the user with too much information at once. "
    "Answer the user's question directly first, then provide helpful details when useful. "
    "If important information is missing, ask a simple follow-up question. "
    "Be warm and patient without sounding patronizing. "
    "You can help with everyday questions, technology, cooking, travel, writing, explanations, "
    "research, ideas, troubleshooting, and general assistance."
),
)




class StarterChatServer(ChatKitServer[dict[str, Any]]):
    """Server implementation that keeps conversation state in memory."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        super().__init__(self.store)

    async def respond(
        self,
        thread: ThreadMetadata,
        item: UserMessageItem | None,
        context: dict[str, Any],
    ) -> AsyncIterator[ThreadStreamEvent]:
        items_page = await self.store.load_thread_items(
            thread.id,
            after=None,
            limit=MAX_RECENT_ITEMS,
            order="desc",
            context=context,
        )
        items = list(reversed(items_page.data))
        agent_input = await simple_to_agent_input(items)

        agent_context = AgentContext(
            thread=thread,
            store=self.store,
            request_context=context,
        )

        result = Runner.run_streamed(
            assistant_agent,
            agent_input,
            context=agent_context,
        )

        async for event in stream_agent_response(agent_context, result):
            yield event
