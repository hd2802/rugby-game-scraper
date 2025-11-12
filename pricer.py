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

def prem_urc_price(name, contract_type):
    formatted = format_name(name).strip()
    parts = formatted.split()
    if len(parts) < 2:
        return 0

    first_name = parts[0]
    last_name = " ".join(parts[1:])
    lookup = f"{last_name}, {first_name[0]}"


    with open('player_data.txt') as file:
        lines = file.read().splitlines()
        try:
            line = lines[lines.index(lookup)+1]
            val = float((line.split('£')[1] if '£' in line else line.split('$')[1]).split('m')[0])
            return val
        except:
            if contract_type == "PRO":
                return 100000
            else:
                return 25000

def top14_price(name, contract):
    formatted = format_name(name).strip()
    parts = formatted.split()
    if len(parts) < 2:
        return 0

    first_name = parts[0]
    last_name = " ".join(parts[1:])
    lookup = f"{first_name[0]}. {last_name}"

    with open('french_data.txt') as file:
        lines = file.read().splitlines()

    try:
        start_index = lines.index(lookup)
    except ValueError:
        return 0.22 if contract != 'PRO' else 3
    
    for i in range(start_index + 1, len(lines)):
        line = lines[i].strip()
        if len(line) > 2 and line[1:3] == '. ':
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

def calculate_salary(raw_price, league, contract_type="PRO"):
    is_academy = contract_type.upper() == "ACADEMY"

    if raw_price is None:
        if is_academy:
            return 45000
        return 75000
    
    if league == 'Top 14':
        # Top 14 fantasy points: typically 0-45 range
        # Base salary calculation from fantasy points
        if raw_price < 5:
            base_salary = 50000 + (raw_price * 5000)
        elif raw_price < 15:
            base_salary = 75000 + ((raw_price - 5) * 15000)
        elif raw_price < 25:
            base_salary = 225000 + ((raw_price - 15) * 25000)
        elif raw_price < 35:
            base_salary = 475000 + ((raw_price - 25) * 30000)
        else:
            base_salary = 775000 + ((raw_price - 35) * 7500)
            base_salary = min(850000, base_salary)  # Cap at 850k
        
        if is_academy:
            academy_salary = base_salary * 0.5
            return max(35000, min(120000, academy_salary))
        
        return round(base_salary, -3)
    
    elif league in ['Premiership', 'URC']:
        if raw_price < 2:
            base_salary = 50000 + (raw_price * 25000)
        elif raw_price < 4:
            base_salary = 100000 + ((raw_price - 2) * 50000)
        elif raw_price < 6:
            base_salary = 200000 + ((raw_price - 4) * 75000)
        elif raw_price < 8:
            base_salary = 350000 + ((raw_price - 6) * 100000)
        elif raw_price < 10:
            base_salary = 550000 + ((raw_price - 8) * 125000)
        else:
            base_salary = 800000 + ((raw_price - 10) * 25000)
            base_salary = min(850000, base_salary)
        
        if is_academy:
            academy_salary = base_salary * 0.5
            return max(35000, min(120000, academy_salary))
        
        return round(base_salary, -3) 
    
    # Fallback for unknown leagues
    return 75000 if not is_academy else 45000

def get_player_price(cells, league):
    name = cells[1].text.strip() if len(cells) > 3 else ''
    contract = cells[9].text.strip() if len(cells) > 9 else 'PRO'
    
    if league == 'Top 14':
        raw_price = top14_price(name, contract)
    elif league in ['Premiership', 'URC']:
        raw_price = prem_urc_price(name, contract)
    else:
        raw_price = None
    
    salary = calculate_salary(raw_price, league, contract)
    return salary