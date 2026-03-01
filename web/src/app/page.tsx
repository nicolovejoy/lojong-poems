import Link from "next/link";
import { getAllPoems } from "@/lib/poems";

export default function Home() {
  const poems = getAllPoems();

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <h1 className="font-serif text-3xl mb-2">am i an ai</h1>
      <p className="text-stone-500 mb-10">
        Found poetry from news stories, guided by Buddhist mind-training
        slogans.
      </p>

      <ul className="space-y-6">
        {poems.map((poem) => (
          <li key={poem.slug}>
            <Link
              href={`/poems/${poem.slug}`}
              className="group block"
            >
              <h2 className="font-serif text-xl group-hover:text-stone-600 transition-colors">
                {poem.title}
              </h2>
              {poem.subtitle && (
                <p className="text-sm text-stone-500 mt-1">{poem.subtitle}</p>
              )}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}
