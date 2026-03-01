import fs from "fs";
import path from "path";

export interface PoemMeta {
  slug: string;
  title: string;
  source: string;
  slogan: string;
  intervention: string;
}

export interface Poem extends PoemMeta {
  body: string; // markdown body (above the ---)
  subtitle: string; // italic line below the title
}

const POEMS_DIR = path.join(process.cwd(), "..", "data", "poems");

function parsePoem(filename: string, raw: string): Poem {
  const slug = filename.replace(/\.md$/, "");

  // Split on the metadata separator (--- on its own line)
  const parts = raw.split(/\n---\n/);
  const body = parts[0].trim();
  const metaBlock = parts[1] || "";

  // Parse metadata from bold markdown keys
  const meta: Record<string, string> = {};
  for (const line of metaBlock.split("\n")) {
    const match = line.match(/^\*\*(.+?):\*\*\s*(.+)$/);
    if (match) {
      meta[match[1].toLowerCase()] = match[2].trim();
    }
  }

  // Extract title (first # heading) and subtitle (first *italic* line)
  const lines = body.split("\n");
  const titleLine = lines.find((l) => l.startsWith("# "));
  const title = titleLine ? titleLine.replace(/^#\s+/, "") : slug;
  const subtitleLine = lines.find(
    (l) => l.startsWith("*") && l.endsWith("*") && !l.startsWith("**")
  );
  const subtitle = subtitleLine
    ? subtitleLine.replace(/^\*/, "").replace(/\*$/, "")
    : "";

  // Body for rendering: everything after title and subtitle
  const titleIdx = lines.indexOf(titleLine || "");
  const subtitleIdx = subtitleLine ? lines.indexOf(subtitleLine) : -1;
  const startIdx = Math.max(titleIdx, subtitleIdx) + 1;
  const poemBody = lines.slice(startIdx).join("\n").trim();

  return {
    slug,
    title,
    subtitle,
    body: poemBody,
    source: meta.source || "",
    slogan: meta.slogan || "",
    intervention: meta.intervention || "",
  };
}

export function getAllPoems(): Poem[] {
  const files = fs
    .readdirSync(POEMS_DIR)
    .filter((f) => f.endsWith(".md"))
    .sort();
  return files.map((f) => {
    const raw = fs.readFileSync(path.join(POEMS_DIR, f), "utf-8");
    return parsePoem(f, raw);
  });
}

export function getPoemBySlug(slug: string): Poem | undefined {
  const filepath = path.join(POEMS_DIR, `${slug}.md`);
  if (!fs.existsSync(filepath)) return undefined;
  const raw = fs.readFileSync(filepath, "utf-8");
  return parsePoem(`${slug}.md`, raw);
}
