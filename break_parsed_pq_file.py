import argparse
from argparse import RawTextHelpFormatter

parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
parser.add_argument('file_path', type=str, help="required file path of a parsed parquet file in txt format")
args = parser.parse_args()

if __name__ == "__main__":
    file_path = args.file_path

    with open(file_path) as file:
        x = file.read()
        x = x.split("\n\n")
        if x[-1] == "":
            x = x[:-1]
        count = 1
        for i in range(0,len(x)):
            filename = f'parsed_file_post{count}.txt'
            f = open(filename, "w+")
            f.write(x[i])
            f.close()
            count += 1
            print(f'created file: {filename}')
        print(f'{len(x)} posts found.')