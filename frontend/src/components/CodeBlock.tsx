import { useState } from "react";

export function CodeBlock({
  label,
  language,
  content,
}: {
  label: string;
  language: string;
  content: string;
}) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      window.setTimeout(() => setCopied(false), 1200);
    } catch {
      setCopied(false);
    }
  };

  return (
    <div className="panel-strong overflow-hidden rounded-[1.75rem]">
      <div className="flex items-center justify-between gap-4 border-b border-black/10 px-5 py-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-[color:var(--muted)]">
            {label}
          </p>
          <p className="mt-1 text-sm font-semibold text-ink">{language}</p>
        </div>
        <button
          type="button"
          onClick={handleCopy}
          className="rounded-full bg-ink px-4 py-2 text-sm font-semibold text-white"
        >
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <pre className="max-h-[28rem] overflow-auto px-5 py-5 text-sm leading-7 text-[color:var(--muted)]">
        <code>{content}</code>
      </pre>
    </div>
  );
}
