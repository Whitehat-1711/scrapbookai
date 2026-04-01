// Simple markdown to HTML renderer - handles headings, bold, tables, lists without external dependencies
export function renderMarkdown(markdown) {
  if (!markdown) return "";

  let html = markdown;

  // Escape HTML special characters first
  html = html
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Then unescape for our markdown syntax
  html = html.replace(/&lt;!-- (.*?) --&gt;/g, "<!-- $1 -->");

  // Headers
  html = html.replace(/^### (.*?)$/gm, "<h3>$1</h3>");
  html = html.replace(/^## (.*?)$/gm, "<h2>$1</h2>");
  html = html.replace(/^# (.*?)$/gm, "<h1>$1</h1>");

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__(.+?)__/g, "<strong>$1</strong>");

  // Italic
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/_(.+?)_/g, "<em>$1</em>");

  // Code blocks
  html = html.replace(/```(.*?)```/gs, "<pre><code>$1</code></pre>");

  // Inline code
  html = html.replace(/`(.+?)`/g, "<code>$1</code>");

  // Tables (simple markdown table parser)
  html = html.replace(
    /\|(.+)\n\|[\s:|-]+\n((?:\|.+\n?)*)/g,
    (match, header, rows) => {
      const headerCells = header
        .split("|")
        .filter((cell) => cell.trim())
        .map((cell) => `<th>${cell.trim()}</th>`)
        .join("");
      const rowHtml = rows
        .split("\n")
        .filter((row) => row.trim())
        .map((row) => {
          const cells = row
            .split("|")
            .filter((cell) => cell.trim())
            .map((cell) => `<td>${cell.trim()}</td>`)
            .join("");
          return `<tr>${cells}</tr>`;
        })
        .join("");
      return `<table><thead><tr>${headerCells}</tr></thead><tbody>${rowHtml}</tbody></table>`;
    }
  );

  // Blockquotes
  html = html.replace(/^> (.*?)$/gm, "<blockquote>$1</blockquote>");

  // Numbered lists
  html = html.replace(
    /((?:^\d+\. .+$\n?)+)/gm,
    (match) => {
      const items = match
        .split("\n")
        .filter((line) => line.trim())
        .map((line) => `<li>${line.replace(/^\d+\.\s+/, "")}</li>`)
        .join("");
      return `<ol>${items}</ol>`;
    }
  );

  // Bullet lists
  html = html.replace(
    /((?:^- .+$\n?)+)/gm,
    (match) => {
      const items = match
        .split("\n")
        .filter((line) => line.trim())
        .map((line) => `<li>${line.replace(/^-\s+/, "")}</li>`)
        .join("");
      return `<ul>${items}</ul>`;
    }
  );

  // Line breaks
  html = html.replace(/\n\n/g, "</p><p>");
  html = `<p>${html}</p>`;
  html = html.replace(/<\/p><p><h[1-6]/g, "<h");
  html = html.replace(/<\/h[1-6]><p>/g, "</h$1>");
  html = html.replace(/<p><blockquote>/g, "<blockquote>");
  html = html.replace(/<\/blockquote><\/p>/g, "</blockquote>");
  html = html.replace(/<p><ol>/g, "<ol>");
  html = html.replace(/<\/ol><\/p>/g, "</ol>");
  html = html.replace(/<p><ul>/g, "<ul>");
  html = html.replace(/<\/ul><\/p>/g, "</ul>");
  html = html.replace(/<p><pre>/g, "<pre>");
  html = html.replace(/<\/pre><\/p>/g, "</pre>");
  html = html.replace(/<p><table>/g, "<table>");
  html = html.replace(/<\/table><\/p>/g, "</table>");

  return html;
}

export default function MarkdownRenderer({ content }) {
  return (
    <div
      className="markdown-content"
      dangerouslySetInnerHTML={{ __html: renderMarkdown(content) }}
    />
  );
}
