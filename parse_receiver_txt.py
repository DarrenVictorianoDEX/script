import re

def parse_text(text):
    data_dict = {}
    current_key = None

    for line in text.split('\n'):
        if "last record -" in line:
            current_key = line.split(' ')[0]
            data_dict[current_key] = {}
        elif "bitfield: " in line and current_key:
            match = re.match(r'(\w+): bitfield: (.+)$', line)
            if match:
                key, value = match.groups()
                flags = {}
                for item in value.strip().split(', '):
                    flag_key, flag_val = item.split(': ', 1)
                    flags[flag_key] = eval(flag_val) if ':' in flag_val else flag_val
                data_dict[current_key][key] = flags
        elif current_key and ': ' in line:
            field, value = line.split(': ', 1)
            data_dict[current_key][field] = value

    return data_dict