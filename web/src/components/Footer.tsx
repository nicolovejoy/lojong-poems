const BUILD_TIME = new Date().toLocaleDateString("en-GB", {
  day: "2-digit",
  month: "2-digit",
  year: "numeric",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

export default function Footer() {
  return (
    <footer className="border-t border-stone-200 py-8 mt-16">
      <div className="max-w-2xl mx-auto px-6 flex items-center justify-between text-sm text-stone-400">
        <span>Found poetry from news, guided by Lojong slogans</span>
        <span>{BUILD_TIME}</span>
      </div>
    </footer>
  );
}
