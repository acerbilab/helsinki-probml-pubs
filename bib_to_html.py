import re
import yaml
from pylatexenc.latex2text import LatexNodes2Text
import logging

logging.basicConfig(level=logging.INFO)

MAX_CHARS_LINE = 100
VENUE_CODES = [
    "Journal",
    "JAIR",
    "JMLR",
    "AAAI",
    "AISTATS",
    "ICLR",
    "The Web Conference",
    "ICRA",
    "COLT",
    "CVPR",
    "ICML",
    "IJCAI",
    "ACL",
    "UAI",
    "KDD",
    "ECCV",
    "ICCV",
    "EMNLP",
    "CoRL",
    "NeurIPS",
]
VENUE_CODES.reverse()


def split_string(input_string, n):
    """
    Splits a string into chunks, ensuring each chunk is at most `n` characters long,
    splitting at the nearest space before the `n`-th character.

    :param input_string: The string to split
    :param n: The maximum number of characters in each chunk
    :return: A list of chunks
    """
    if n <= 0:
        raise ValueError("`n` must be a positive integer.")

    words = input_string.split()
    chunks = []
    current_chunk = ""

    for word in words:
        # Check if adding the word would exceed the limit
        if len(current_chunk) + len(word) + 1 > n:
            # Append the current chunk to chunks and start a new chunk
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            # Add the word to the current chunk
            if current_chunk:
                current_chunk += " "
            current_chunk += word

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


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


def split_string(input_string, n):
    """
    Splits a string into chunks, ensuring each chunk is at most `n` characters long,
    splitting at the nearest space before the `n`-th character.

    :param input_string: The string to split
    :param n: The maximum number of characters in each chunk
    :return: A list of chunks
    """
    if n <= 0:
        raise ValueError("`n` must be a positive integer.")

    words = input_string.split()
    chunks = []
    current_chunk = ""

    for word in words:
        # Check if adding the word would exceed the limit
        if len(current_chunk) + len(word) + 1 > n:
            # Append the current chunk to chunks and start a new chunk
            chunks.append(current_chunk.strip())
            current_chunk = word
        else:
            # Add the word to the current chunk
            if current_chunk:
                current_chunk += " "
            current_chunk += word

    # Add the last chunk if it exists
    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def format_authors(entry):
    authors = entry.get("author", "Unknown Author")

    # Ensure authors is a string
    if not isinstance(authors, str):
        raise ValueError("The 'author' field must be a string.")

    # Decode LaTeX-style escape sequences to Unicode
    authors = LatexNodes2Text().latex_to_text(authors)

    authors_list = authors.split(" and ")  # Split the authors
    formatted_authors = []

    for author in authors_list:
        parts = author.split(", ")
        if len(parts) == 2:
            last_name, first_names = parts
            first_initials = "".join(
                f"{name.strip()[0]} " for name in first_names.split() if name.strip()
            )
            # Keep the last name as is to preserve special characters
            formatted_name = f"{last_name.strip()} {first_initials.strip()}"
            formatted_authors.append(formatted_name)
        else:
            # If the author name doesn't fit the expected "Last, First" format, keep it as is
            formatted_authors.append(author.strip())

    return ", ".join(formatted_authors)


def convert_bib_to_html(
    bib_file, venue_code_dict, output_file="publications.html", max_year=2020
):
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
        if publications_by_year[year] and int(year) >= max_year:
            per_year_content = ""

            for entry in publications_by_year[year]:
                venue_name = entry.get(
                    "booktitle", entry.get("journal", "Unknown Venue")
                )
                entry["venue_name"] = venue_name
                entry["venue_code"] = venue_code_dict.get(venue_name, "skip")

            # A mapping from venue names to their order
            venue_order = {venue: index for index, venue in enumerate(VENUE_CODES)}

            # Sort the list of dictionaries
            publications_by_year[year].sort(
                key=lambda x: venue_order.get(x["venue_code"], float("inf"))
            )
            # breakpoint()
            current_venue = None
            for entry in publications_by_year[year]:
                authors = format_authors(entry)
                title = entry.get("title", "Untitled")
                full_venue_name = entry.get("journal", entry["venue_name"])
                date = f"{entry.get('month', '')} {entry.get('year', '')}".strip()
                arxiv_link = entry.get("arxiv", None)
                code_link = entry.get("code", None)
                paper_link = entry.get("url", None)
                venue_code = entry["venue_code"]

                vc = list(venue_code_dict.values())
                max_code_len = len(max(vc, key=len))
                spaces = "&nbsp;" * (((max_code_len) * 3) + 1)

                if venue_code != "skip":
                    code_space = "&nbsp;" * (((max_code_len + 1) - len(venue_code)) * 2)
                    if max_code_len - len(venue_code) > 0:
                        code_space = code_space + "&nbsp;"

                    if len(title) > MAX_CHARS_LINE:
                        title_chunks = split_string(title, MAX_CHARS_LINE)
                        title_line1 = title_chunks[0]
                        title_line2 = title_chunks[1]
                    else:
                        title_line1 = title

                    per_year_content += (
                        f"<div style='margin-bottom: 5px;'>\n"
                        f"    <code>[{venue_code}]</code><strong>{code_space}{title_line1}</strong><br>\n"
                    )

                    if len(title) > MAX_CHARS_LINE:
                        per_year_content += (
                            f"    {spaces} <strong>{title_line2}</strong><br>\n"
                        )

                    if len(authors) > MAX_CHARS_LINE:
                        authors_chunks = split_string(authors, MAX_CHARS_LINE)
                        authors_line1 = authors_chunks[0]
                        authors_line2 = authors_chunks[1]
                    else:
                        authors_line1 = authors

                    per_year_content += f"    {spaces} {authors_line1}<br>\n"

                    if len(authors) > MAX_CHARS_LINE:
                        per_year_content += f"    {spaces} {authors_line2}<br>\n"

                    per_year_content += (
                        f"    {spaces} <em>{full_venue_name}</em> {date}<br>\n"
                    )

                    first_item = True
                    if paper_link:
                        if first_item:
                            per_year_content += spaces + "&nbsp;"
                        else:
                            per_year_content += " | "
                        per_year_content += (
                            f"<a href='{paper_link}' target='_blank'>LINK</a>\n"
                        )
                        first_item = False

                    if arxiv_link:
                        if first_item:
                            per_year_content += spaces + "&nbsp;"
                        else:
                            per_year_content += " | "
                        per_year_content += (
                            f"<a href='{arxiv_link}' target='_blank'>ARXIV</a>\n"
                        )
                        first_item = False

                    if code_link:
                        if first_item:
                            per_year_content += spaces + "&nbsp;"
                        else:
                            per_year_content += " | "
                        per_year_content += (
                            f"    <a href='{code_link}' target='_blank'>CODE</a>\n"
                        )
                        first_item = False

                    per_year_content += "</div>\n"

                    # breakpoint()

                else:
                    logging.warning(
                        f"skipped {full_venue_name} - {title} - {authors} \n"
                    )

            if per_year_content != "":
                html_content += (
                    f"<div style='margin-bottom: 10px;'> <h2>{year}</h2></div>\n"
                )
                html_content += per_year_content

    html_content += """</body>\n</html>"""

    with open(output_file, "w") as file:
        file.write(html_content)

    logging.info(f"HTML publication list saved to {output_file}")


if __name__ == "__main__":
    with open("venue_code.yaml", "r") as file:
        venue_code_dict = yaml.safe_load(file)

    convert_bib_to_html("all_publications.bib", venue_code_dict)
