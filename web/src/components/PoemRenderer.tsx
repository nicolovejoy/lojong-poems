import { renderPoem } from "@/lib/mdx";

interface PoemRendererProps {
  markdown: string;
}

export default async function PoemRenderer({ markdown }: PoemRendererProps) {
  const content = await renderPoem(markdown);

  return (
    <div className="poem font-serif text-lg leading-relaxed space-y-4 text-stone-800">
      {content}
    </div>
  );
}
