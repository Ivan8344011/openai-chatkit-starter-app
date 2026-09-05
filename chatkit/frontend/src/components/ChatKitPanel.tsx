import { ChatKit, useChatKit } from "@openai/chatkit-react";
import { CHATKIT_API_DOMAIN_KEY, CHATKIT_API_URL } from "../lib/config";
import { useEffect, useState } from "react";
export function ChatKitPanel() {
const [colorScheme, setColorScheme] = useState<"light" | "dark">(
  window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light"
);
  useEffect(() => {
  const mediaQuery = window.matchMedia("(prefers-color-scheme: dark)");

  const handleChange = (event: MediaQueryListEvent) => {
    setColorScheme(event.matches ? "dark" : "light");
  };

  mediaQuery.addEventListener("change", handleChange);

  return () => {
    mediaQuery.removeEventListener("change", handleChange);
  };
}, []);
  const chatkit = useChatKit({
    
    api: { url: CHATKIT_API_URL, domainKey: CHATKIT_API_DOMAIN_KEY },
    theme: {
  colorScheme: colorScheme,
},
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
