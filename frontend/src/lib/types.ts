export type LLMStep = {
  title: string;
  explanation?: string | null;
  inputLatex?: string | null;
  outputLatex?: string | null;
};

export type PlotSeries = { name: string; x: number[]; y: Array<number | null> };

export type IntegrateResponse = {
  stepsAvailable: boolean;
  integrandLatex: string;
  resultLatex?: string | null;
  steps: LLMStep[];
  plots: PlotSeries[];
  meta: Record<string, unknown>;
};
