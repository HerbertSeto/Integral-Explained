"use client";

import { useEffect, useRef } from "react";
import katex from "katex";
import "katex/dist/katex.min.css";

export function MathDisplay({
  latex,
  block = false,
  className,
}: {
  latex: string | null | undefined;
  block?: boolean;
  className?: string;
}) {
  const ref = useRef<HTMLSpanElement>(null);

  useEffect(() => {
    if (!ref.current || !latex) return;
    try {
      katex.render(latex, ref.current, {
        throwOnError: false,
        displayMode: block,
        output: "html",
      });
    } catch {
      if (ref.current) ref.current.textContent = latex;
    }
  }, [latex, block]);

  if (!latex) return <span className={className}>—</span>;
  return <span ref={ref} className={className} />;
}
