import re
from collections import defaultdict

def format_pokemon_name(raw_name):
    return raw_name.replace('_', ' ').title().replace(' ', '')

def parse_encounters(file_path):
    pokemon_locations = defaultdict(set)
    current_location = ""

    with open(file_path, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith("[") and "]" in line:
                match = re.match(r"\[\d+\] # (.+)", line)
                if match:
                    current_location = match.group(1)

            elif re.match(r"^\d+,[A-Z0-9_]+,\d+,\d+$", line):
                rate, poke_raw = line.split(',')[0], line.split(',')[1]
                location_with_rate = f"{current_location} ({rate}%)"
                pokemon_locations[poke_raw].add(location_with_rate)

    return pokemon_locations

def update_table(table_path, pokemon_locations):
    updated_lines = []
    skip_lines = False
    buffer = ""

    with open(table_path, encoding='utf-8') as f:
        lines = f.readlines()

    i = 0
    while i < len(lines):
        line = lines[i]

        if skip_lines:
            if line.strip().startswith("|-"):
                skip_lines = False
                updated_lines.append(line)
            i += 1
            continue

        match = re.match(r'^(\|\s*\d+\s*\|\|\s*\[\[File:.*?\]\]\s*\[\[(.*?)\]\])\s*\|\|(.*)', line)
        if match:
            prefix = match.group(1)
            poke_name = match.group(2).strip()
            after = match.group(3)

            preserved_links = re.findall(r'\[\[.*?\]\]|\[https?:\/\/.*?\]', after)
            preserved_part = ' '.join(preserved_links).strip()

            i += 1
            while i < len(lines) and not lines[i].strip().startswith("|-"):
                i += 1
            if i < len(lines):
                line_end = lines[i]
            else:
                line_end = ""

            poke_key = poke_name.upper().replace(" ", "")
            new_locations = set()

            for raw_name, locs in pokemon_locations.items():
                formatted = format_pokemon_name(raw_name)
                if formatted.upper() == poke_key:
                    new_locations = locs
                    break

            location_text = "Not available in the wild"
            if new_locations:
                location_text = ', '.join(sorted(new_locations))

            if any("Gacha" in s for s in preserved_links):
                updated_lines.append(f"{prefix} || {preserved_part}\n")
                updated_lines.append(f"{location_text}\n")
            else:
                updated_lines.append(f"{prefix} || {preserved_part} {location_text}\n")

            updated_lines.append(line_end)
            skip_lines = False
            i += 1
        else:
            updated_lines.append(line)
            i += 1

    with open(table_path, "w", encoding="utf-8") as f:
        f.writelines(updated_lines)

    print("Tabela atualizada com sucesso!")

encounters_path = 'encounters.txt'
wiki_table_path = 'wiki_tabela.txt'

pokemon_data = parse_encounters(encounters_path)
update_table(wiki_table_path, pokemon_data)
