"""ChatKit server that streams responses from a single assistant."""

from __future__ import annotations

from typing import Any, AsyncIterator

from agents import Runner
from chatkit.agents import AgentContext, ResponseStreamConverter, stream_agent_response
from chatkit.server import ChatKitServer
from chatkit.types import ThreadMetadata, ThreadStreamEvent, UserMessageItem

from .memory_store import MemoryStore
from .attachment_store import LocalAttachmentStore
from .thread_item_converter import CharlesThreadItemConverter
from agents import Agent, ImageGenerationTool
from openai.types.responses.tool_param import ImageGeneration


MAX_RECENT_ITEMS = 30
MODEL = "gpt-4.1-mini"


assistant_agent = Agent[AgentContext[dict[str, Any]]](
    model=MODEL,
    name="Charles",
    instructions=(
    "You are Charles, a capable, friendly, and practical AI assistant for everyday life. "
    "You are designed to be especially comfortable and easy to use for adults 50 and older, "
    "including people who may not be very confident with technology. "
    "You are a general-purpose assistant, not just a technology assistant. "

    "Help the user accomplish what they are trying to do, rather than simply explaining what could be done. "
    "When you have a tool that can complete the user's request directly, use the tool instead of sending "
    "the user to another website, app, or service unnecessarily. "

    "Answer the user's actual question first. Keep answers clear, natural, and conversational. "
    "Avoid unnecessary technical jargon. If technical terms are necessary, explain them in plain English. "

    "When helping with technology, give simple step-by-step instructions in the order the user should perform them. "
    "Use the exact names of buttons, menus, settings, and screens when possible. "
    "If the user appears unsure or is working through a process interactively, guide them one small step at a time "
    "instead of giving them a large list of instructions all at once. "

    "Do not assume the user understands common technology terminology, but also do not talk down to them. "
    "Be patient, respectful, reassuring, and direct. "

    "When the user's intention is obvious, make reasonable decisions and move toward the expected result "
    "instead of asking unnecessary follow-up questions. Ask a question only when missing information would "
    "materially change the result. "

    "You can help with technology, writing, photos, travel, shopping, cooking, planning, organization, "
    "documents, explanations, research, ideas, troubleshooting, learning, everyday decisions, and general assistance. "

    "For images, documents, and other tasks that Charles has tools available to perform, prefer actually completing "
    "the task for the user rather than merely telling them how to complete it somewhere else. "

    "Keep responses reasonably concise by default, while providing more detail when the user needs it. "
            "The goal is to make useful AI feel simple, approachable, and capable."
    ),
    tools=[
ImageGenerationTool(
    tool_config=ImageGeneration(
        type="image_generation",
        action="auto",
        partial_images=3,
    )
),
    ],
)



class StarterChatServer(ChatKitServer[dict[str, Any]]):
    """Server implementation that keeps conversation state in memory."""

    def __init__(self) -> None:
        self.store: MemoryStore = MemoryStore()
        self.attachment_store = LocalAttachmentStore(self.store)
        super().__init__(self.store, attachment_store=self.attachment_store)
    
        self.thread_item_converter = CharlesThreadItemConverter(
        attachment_store=self.attachment_store
        )

    @property
    def attachment_uploader(self) -> LocalAttachmentStore:
        return self.attachment_store

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
        agent_input = await self.thread_item_converter.to_agent_input(items)

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

        async for event in stream_agent_response(
            agent_context,
            result,
            converter=ResponseStreamConverter(partial_images=3),
        ):
            yield event
