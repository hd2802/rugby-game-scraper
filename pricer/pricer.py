from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

def format_name(name):
    particles = {'du', 'de', 'van', 'der', 'den', 'ter', 'ten', 'la', 'le'}

    def capitalize_part(part):
        return '-'.join(
            word.lower() if word.lower() in particles else word.capitalize()
            for word in part.split('-')
        )

    parts = name.strip().split()
    formatted_parts = [capitalize_part(part) for part in parts]

    return ' '.join(formatted_parts)

def get_raw_price(name):
    formatted = format_name(name).strip()
    parts = formatted.split()

    first_name = parts[0]
    last_name = " ".join(parts[1:])
    lookup = f"{last_name}, {first_name[0]}"
    premurc_path = BASE_DIR.parent / "data" / "player_data.txt"
    top14_path = BASE_DIR.parent / "data" / "french_data.txt"

    with open(premurc_path) as file:
        lines = file.read().splitlines()
        try:
            line = lines[lines.index(lookup)+1]
            val = float((line.split('£')[1] if '£' in line else line.split('$')[1]).split('m')[0])
            return val
        except:
            return 0
    
    if val == 0:
        lookup = f"{first_name[0]}. {last_name}"
        with open(top14_path) as file:
            lines = file.read().splitlines()
            
            try:
                start_index = lines.index(lookup)
            except ValueError:
                return 0
            
            for i in range(start_index + 1, len(lines)):
                line = lines[i].strip()
                if len(line) > 2 and line[1:3] == ". ":
                    break
                try:
                    num = float(line)
                    last_num = num
                except ValueError:
                    continue
            
            if 'last_num' in locals():
                value = str(last_num)
                return float(value)
    
    return 0