import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_DOMAIN_KEY, CHATKIT_API_URL } from "../lib/config";

export function ChatKitPanel() {
  const chatkit = useChatKit({
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    composer: {
      placeholder: "Ask Charles anything...",
      // File uploads are disabled for the demo backend.
      attachments: { enabled: false },
    },
  });

  return (
    <div className="relative flex h-full min-h-0 w-full flex-col overflow-hidden bg-white dark:bg-slate-950">
      <ChatKit control={chatkit.control} className="block h-full w-full" />
    </div>
  );
}
