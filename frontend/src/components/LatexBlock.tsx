import katex from "katex";
import "katex/dist/katex.min.css";

type Props = {
  latex: string;
  displayMode?: boolean;
};

export function LatexBlock({ latex, displayMode = true }: Props) {
  const html = katex.renderToString(latex, {
    throwOnError: false,
    displayMode,
    strict: "ignore",
  });
  return <div className="latex-block" dangerouslySetInnerHTML={{ __html: html }} />;
}
