def read_file(file):
    """ Read file """
    with open(file, "r", encoding="UTF-8") as file1:
        for line in file1:
            return line.strip()
