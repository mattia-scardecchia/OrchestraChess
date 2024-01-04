from tqdm import tqdm


with open('output.pgn', 'w') as output_file:
    with open('/Users/mattia/Downloads/lichess_db_standard_rated_2020-01.pgn', 'r') as file:
        for i, line in enumerate(tqdm(file)):
            if "[" not in line:
                output_file.write(line)
            else:
                if "Elo" in line:
                    output_file.write(line)
                if "TimeControl" in line:
                    output_file.write(line)
                if "1." in line:
                    output_file.write(line)
