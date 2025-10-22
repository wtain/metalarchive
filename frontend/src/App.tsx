import React from "react";

interface AppProps {
  children: React.ReactNode;
}

export default function App({ children }: AppProps) {
  return (
    <div className="min-h-screen flex flex-col">
      <nav className="bg-blue-600 text-white p-4 flex gap-6">
        <a href="/" className="font-semibold hover:underline">Subscribers</a>
        <a href="/reactions" className="font-semibold hover:underline">Reactions</a>
      </nav>
      <main className="flex-1 p-6">{children}</main>
    </div>
  );
}
