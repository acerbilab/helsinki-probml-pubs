import re
import yaml


def parse_bib_file(bib_file):
    """Parse a .bib file into structured data."""
    with open(bib_file, "r") as file:
        content = file.read()

    # Match each BibTeX entry
    entries = re.findall(r"@(\w+)\{(.*?),\s*(.*?)\n\}", content, re.DOTALL)
    parsed_entries = []

    for entry in entries:
        entry_type, entry_key, fields_block = entry

        # Improved regex for fields that handles nested braces and escaped characters
        fields = re.findall(
            r'(\w+)\s*=\s*({(?:[^{}]|{[^{}]*})*}|"(?:[^"\\]|\\.)*")',
            fields_block,
            re.DOTALL,
        )

        parsed_entry = {
            "ENTRYTYPE": entry_type,
            "ID": entry_key,
        }

        # Process each field
        for field, value in fields:
            # Remove enclosing braces or quotes
            if value.startswith("{") and value.endswith("}"):
                value = value[1:-1]
            elif value.startswith('"') and value.endswith('"'):
                value = value[1:-1]

            # Add the field to the parsed entry
            parsed_entry[field] = value

        parsed_entries.append(parsed_entry)

    return parsed_entries


def convert_bib_to_html(bib_file, venue_code, output_file="publications.html"):
    """Convert a .bib file to an HTML file grouped by year."""
    bib_data = parse_bib_file(bib_file)

    html_content = """<!DOCTYPE html>
<html>
<head>
    <title>Publications</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        h1 { text-align: left; }
        .tag { background-color: #4285f4; color: white; padding: 4px 8px; border-radius: 4px; }
        .title { font-weight: bold; }
        .authors, .venue, .links { margin-left: 40px; }
        .venue { font-style: italic; }
        .links a { margin-right: 10px; text-decoration: none; color: blue; }
    </style>
</head>
<body>
"""

    publications_by_year = {}
    for entry in bib_data:
        year = entry.get("year", "Unknown")
        publications_by_year.setdefault(year, []).append(entry)

    for year in sorted(publications_by_year.keys(), reverse=True):
        if publications_by_year[year]:
            per_year_content = ""
            for entry in publications_by_year[year]:
                authors = entry.get("author", "Unknown Author").replace(" and ", ", ")
                title = entry.get("title", "Untitled")
                venue_name = entry.get(
                    "booktitle", entry.get("journal", "Unknown Venue")
                )
                full_venue_name = entry.get("journal", venue_name)
                date = f"{entry.get('month', '')} {entry.get('year', '')}".strip()
                arxiv_link = entry.get("arxiv", "#")
                code = venue_code.get(venue_name, "skip")

                if code != "skip":
                    per_year_content += (
                        f"<div style='margin-bottom: 5px;'>\n"
                        f"    <code>[{code}]</code><strong>&nbsp; {title}</strong><br>\n"
                        f"    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; {format_authors(authors)}<br>\n"
                        f"    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <em>{full_venue_name} {date}</em><br>\n"
                        f"    &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; <a href='{arxiv_link}' target='_blank'>[ARXIV]</a>\n"
                        f"    <a href='#{entry['ID']}'>[BIB]</a>\n"
                        f"</div>\n"
                    )

            if per_year_content != "":
                html_content += (
                    f"<div style='margin-bottom: 10px;'> <h2>{year}</h2></div>\n"
                )
                html_content += per_year_content

    html_content += """</body>\n</html>"""

    with open(output_file, "w") as file:
        file.write(html_content)

    print(f"HTML publication list saved to {output_file}")


def format_authors(authors, max_length=100):
    words = authors.split(", ")  # Split authors by commas
    current_line = ""
    formatted_lines = []

    for word in words:
        if len(current_line) + len(word) + 2 <= max_length:  # +2 for the ", " separator
            current_line += (", " if current_line else "") + word
        else:
            formatted_lines.append(current_line)
            current_line = word
    if current_line:
        formatted_lines.append(current_line)

    # Add &nbsp; indentation for subsequent lines
    return "<br>&nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; &nbsp; ".join(formatted_lines)


if __name__ == "__main__":
    with open("venue_code.yaml", "r") as file:
        venue_code = yaml.safe_load(file)

    convert_bib_to_html("all_publications.bib", venue_code)
