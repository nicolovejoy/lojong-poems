import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "About",
  description: "Found poetry from news stories, guided by Buddhist mind-training slogans.",
};

export default function AboutPage() {
  return (
    <article className="max-w-2xl mx-auto px-6 py-12">
      <h1 className="font-serif text-3xl mb-8">About</h1>

      <div className="space-y-6 text-stone-700 leading-relaxed">
        <p>
          Every poem on this site was composed from real sentences found in news
          articles. Some were assembled by a human. Some were assembled by an AI.
          The language is always the journalist&rsquo;s &mdash; only the
          arrangement is ours.
        </p>

        <p>
          Soon, when you read a poem, we&rsquo;ll ask you a simple question:{" "}
          <em>was this written by an AI?</em>
        </p>

        <p>
          There&rsquo;s no trick. No gotcha. We&rsquo;re genuinely curious
          whether the difference is legible &mdash; whether something in the
          selection, the ordering, the silences, gives it away. Or doesn&rsquo;t.
        </p>

        <p>
          After you vote, you&rsquo;ll see how other readers answered. That&rsquo;s
          the whole game.
        </p>

        <p className="text-stone-400 text-sm pt-4">
          This is an ongoing experiment. If you have thoughts about the poems,
          the project, or what we&rsquo;re getting wrong, we&rsquo;d like to
          hear them. Feedback tools are coming &mdash; for now, the site is
          listening.
        </p>
      </div>
    </article>
  );
}
