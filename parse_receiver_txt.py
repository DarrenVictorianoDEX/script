import re
import argparse
from argparse import RawTextHelpFormatter


def parse_text(text):
    """
    parse a vnv receiver text file and returns its content as dict.

    :param text_content: The content of the text file.
    :return: The content of the text file as a dictionary.
    """
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


def read_file(file_path):
    """
    Opens a text file and returns its content.

    :param filename: The name of the text file.
    :return: The content of the text file as a string.
    """
    try:
        with open(file_path, 'r') as file:
            return file.read()
    except FileNotFoundError:
        print(f"File '{file_path}' not found.")
        return None


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument('text_file', type=str, help="text file from vnv recevier tool")
    args = parser.parse_args()
    text_file = args.text_file
    file_content = read_file(text_file)
    parsed_data = parse_text(file_content)
    print(parsed_data)

if __name__ == "__main__":
    main()
