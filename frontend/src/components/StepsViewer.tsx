"use client";

import styles from "./StepsViewer.module.css";
import { MathDisplay } from "./MathDisplay";

import type { LLMStep } from "@/lib/types";

export function StepsViewer({ steps }: { steps: LLMStep[] }) {
  if (!steps.length) {
    return (
      <p className={styles.unavailable}>
        Steps are not available for this integral. The answer could not be
        verified, or the Groq API could not be reached.
      </p>
    );
  }

  return (
    <ol className={styles.stepList}>
      {steps.map((step, i) => (
        <li key={i} className={styles.step}>
          <div className={styles.stepHeader}>
            <span className={styles.stepNumber}>{i + 1}</span>
            <span className={styles.stepTitle}>{step.title}</span>
          </div>
          {step.explanation ? (
            <p className={styles.stepExplanation}>{step.explanation}</p>
          ) : null}
          {step.inputLatex ? (
            <div className={styles.mathBlock}>
              <div className={styles.mathLabel}>Before</div>
              <div className={styles.mathInline}>
                <MathDisplay latex={step.inputLatex} block />
              </div>
            </div>
          ) : null}
          {step.outputLatex ? (
            <div className={styles.mathBlock}>
              <div className={styles.mathLabel}>After</div>
              <div className={styles.mathInline}>
                <MathDisplay latex={step.outputLatex} block />
              </div>
            </div>
          ) : null}
        </li>
      ))}
    </ol>
  );
}
