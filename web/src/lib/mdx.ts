import { unified } from "unified";
import remarkParse from "remark-parse";
import remarkGfm from "remark-gfm";
import remarkRehype from "remark-rehype";
import rehypeReact from "rehype-react";
import { createElement, Fragment } from "react";
import type { ReactElement } from "react";
import { jsx, jsxs } from "react/jsx-runtime";

export async function renderPoem(markdown: string): Promise<ReactElement> {
  const result = await unified()
    .use(remarkParse)
    .use(remarkGfm)
    .use(remarkRehype)
    .use(rehypeReact, {
      Fragment,
      jsx,
      jsxs,
      createElement,
      components: {
        del: (props: React.ComponentProps<"del">) =>
          createElement(
            "span",
            { className: "poem-intervention" },
            createElement(
              "del",
              { className: "text-stone-400 decoration-stone-400" },
              props.children
            ),
          ),
      },
    })
    .process(markdown);

  return result.result as ReactElement;
}
