import { ChatKitPanel } from "./components/ChatKitPanel";

export default function App() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-end bg-slate-100 dark:bg-slate-950">
      <div className="mx-auto w-full max-w-5xl">
        <header className="mb-4 text-center">
  <h1 className="mt-1 text-3xl font-semibold text-slate-900 dark:text-white">
    Charles
  </h1>
  <p className="mt-1 text-lg text-slate-600 dark:text-slate-300">
    Your everyday AI assistant.
  </p>
</header>
        <ChatKitPanel />
      </div>
    </main>
  );
}
