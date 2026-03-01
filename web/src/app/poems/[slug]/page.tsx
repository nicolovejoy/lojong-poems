import { notFound } from "next/navigation";
import { getAllPoems, getPoemBySlug } from "@/lib/poems";
import PoemRenderer from "@/components/PoemRenderer";
import type { Metadata } from "next";

interface PoemPageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  return getAllPoems().map((poem) => ({ slug: poem.slug }));
}

export async function generateMetadata({
  params,
}: PoemPageProps): Promise<Metadata> {
  const { slug } = await params;
  const poem = getPoemBySlug(slug);
  if (!poem) return {};
  return {
    title: poem.title,
    description: `Found poem — ${poem.slogan}`,
  };
}

export default async function PoemPage({ params }: PoemPageProps) {
  const { slug } = await params;
  const poem = getPoemBySlug(slug);
  if (!poem) notFound();

  return (
    <article className="max-w-2xl mx-auto px-6 py-12">
      <header className="mb-10">
        <h1 className="font-serif text-3xl mb-2">{poem.title}</h1>
        {poem.subtitle && (
          <p className="text-sm text-stone-500 italic">{poem.subtitle}</p>
        )}
      </header>

      <PoemRenderer markdown={poem.body} />

      <footer className="mt-12 pt-6 border-t border-stone-200 text-sm text-stone-400 space-y-1">
        {poem.source && <p>{poem.source}</p>}
        {poem.intervention && (
          <p>
            <span className="text-stone-500">Intervention:</span>{" "}
            {poem.intervention}
          </p>
        )}
      </footer>
    </article>
  );
}
