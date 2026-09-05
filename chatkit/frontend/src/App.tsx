import { ChatKitPanel } from "./components/ChatKitPanel";

export default function App() {
  return (
    <main className="h-dvh overflow-hidden bg-white dark:bg-slate-950">
            <div className="mx-auto flex h-full w-full max-w-md flex-col">
        <header className="shrink-0 px-4 pb-3 pt-4 text-center">
  <h1 className="mt-1 text-3xl font-semibold text-slate-900 dark:text-white">
    Charles
  </h1>
  <p className="mt-1 text-lg text-slate-600 dark:text-slate-300">
    Your everyday AI assistant.
  </p>
</header>
<div className="min-h-0 flex-1">
  <ChatKitPanel />
</div>
       
      </div>
    </main>
  );
}
