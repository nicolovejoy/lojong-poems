import Link from "next/link";

export default function Header() {
  return (
    <header className="border-b border-stone-200 py-4">
      <div className="max-w-2xl mx-auto px-6 flex items-center justify-between">
        <Link href="/" className="text-lg font-medium tracking-tight text-stone-900">
          am i an ai
        </Link>
        <nav className="text-sm text-stone-500">
          <Link href="/" className="hover:text-stone-900 transition-colors">
            poems
          </Link>
        </nav>
      </div>
    </header>
  );
}
