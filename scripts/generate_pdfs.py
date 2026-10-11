import os
import subprocess
import markdown

CHROME_BIN = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
DOCS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "docs"))

CSS_STYLE = """
@page {
  size: A4;
  margin: 18mm 18mm 20mm 18mm;
  @bottom-right {
    content: counter(page);
  }
}

body {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
  color: #1e293b;
  line-height: 1.6;
  font-size: 10.5pt;
}

h1, h2, h3, h4, h5 {
  color: #0f172a;
  font-weight: 700;
  margin-top: 1.4em;
  margin-bottom: 0.6em;
  page-break-after: avoid;
}

h1 {
  font-size: 20pt;
  color: #3730a3;
  border-bottom: 2.5px solid #4f46e5;
  padding-bottom: 0.3em;
  margin-top: 0;
}

h2 {
  font-size: 14pt;
  color: #1e1b4b;
  border-bottom: 1.5px solid #e2e8f0;
  padding-bottom: 0.2em;
}

h3 {
  font-size: 12pt;
  color: #312e81;
}

h4 {
  font-size: 11pt;
  color: #4338ca;
}

p {
  margin-bottom: 0.8em;
  text-align: justify;
}

blockquote {
  border-left: 4px solid #4f46e5;
  background-color: #f8fafc;
  padding: 0.6em 1em;
  margin: 1em 0;
  color: #334155;
  font-style: italic;
  border-radius: 0 6px 6px 0;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 1.2em 0;
  font-size: 9.5pt;
  page-break-inside: avoid;
}

th, td {
  border: 1px solid #cbd5e1;
  padding: 6px 10px;
  text-align: left;
}

th {
  background-color: #f1f5f9;
  color: #0f172a;
  font-weight: 600;
}

tr:nth-child(even) td {
  background-color: #f8fafc;
}

code {
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
  background-color: #f1f5f9;
  color: #4338ca;
  padding: 0.15em 0.35em;
  border-radius: 4px;
  font-size: 9pt;
}

pre {
  background-color: #0f172a;
  color: #f8fafc;
  padding: 1em;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 8.5pt;
  line-height: 1.4;
  page-break-inside: avoid;
}

pre code {
  background-color: transparent;
  color: inherit;
  padding: 0;
}

ul, ol {
  margin-bottom: 0.8em;
  padding-left: 1.8em;
}

li {
  margin-bottom: 0.3em;
}

hr {
  border: 0;
  border-top: 1px solid #cbd5e1;
  margin: 1.5em 0;
}

.footer-print {
  margin-top: 3em;
  padding-top: 1em;
  border-top: 1px solid #cbd5e1;
  font-size: 8pt;
  color: #64748b;
  text-align: center;
}
"""

def convert_md_to_pdf(md_filename, pdf_filename):
    md_path = os.path.join(DOCS_DIR, md_filename)
    pdf_path = os.path.join(DOCS_DIR, pdf_filename)
    html_temp_path = os.path.join(DOCS_DIR, md_filename.replace('.md', '_temp.html'))

    print(f"Conversion de {md_filename} vers {pdf_filename}...")

    with open(md_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    html_body = markdown.markdown(
        md_content,
        extensions=['tables', 'fenced_code', 'codehilite', 'toc', 'nl2br']
    )

    full_html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>{md_filename}</title>
  <style>
{CSS_STYLE}
  </style>
</head>
<body>
{html_body}
<div class="footer-print">
  CantineMaster &copy; 2026 — Document pédagogique officiel pour le cours de Test et Validation des Logiciels
</div>
</body>
</html>"""

    with open(html_temp_path, 'w', encoding='utf-8') as f:
        f.write(full_html)

    # Exécution de Chrome headless pour générer le PDF
    cmd = [
        CHROME_BIN,
        "--headless",
        "--disable-gpu",
        "--no-pdf-header-footer",
        f"--print-to-pdf={pdf_path}",
        html_temp_path
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(html_temp_path):
        os.remove(html_temp_path)

    if result.returncode == 0 and os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        print(f"✓ Succès : {pdf_filename} généré ({size_kb:.1f} KB)")
        return True
    else:
        print(f"✗ Erreur lors de la génération de {pdf_filename}:", result.stderr)
        return False

def main():
    docs = [
        ("SPECIFICATIONS_FONCTIONNELLES.md", "SPECIFICATIONS_FONCTIONNELLES.pdf"),
        ("SUJET_TP_TEST_VALIDATION.md", "SUJET_TP_TEST_VALIDATION.pdf"),
        ("CAHIER_DE_RECETTE_ETUDIANTS.md", "CAHIER_DE_RECETTE_ETUDIANTS.pdf"),
    ]

    for md_file, pdf_file in docs:
        convert_md_to_pdf(md_file, pdf_file)

if __name__ == '__main__':
    main()
