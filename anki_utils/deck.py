import csv


def load_deck(deck_csv_path: str) -> tuple[list[dict], list[str]]:
    """
    Load a deck from a CSV file.

    The CSV file is expected to have tab-separated values. The function reads the file,
    extracts metadata comments (lines starting with '#') at the beginning of the file,
    and then processes the remaining lines as deck entries.

    Each deck entry can have either one field (vi) or four to five fields:
    
    - id: Identifier (optional)
    - vi: Vietnamese text
    - en: English translation
    - examples: Example sentences
    - wiktdata: Additional data (optional)

    Parameters
    ----------
    deck_csv_path : str
        The path to the CSV file containing the deck.

    Returns
    -------
    tuple of list of dict and list of str
        A tuple containing two elements:
        - A list of dictionaries representing the deck entries.
        - A list of metadata comment strings.
    """
    deck: list[dict] = []
    metadata: list[str] = []

    with open(deck_csv_path, "r") as csv_file:
        # Extract the metadata comment strings at the beginning of the file
        for line in csv_file:
            if line.startswith("#"):
                metadata.append(line)
            else:
                break

        reader = csv.reader(csv_file, delimiter="\t")
        for row in reader:
            assert (
                len(row) == 1 or len(row) >= 4
            ), "The deck should have one (vi), four or five fields: id, vi, en, examples, [wiktdata]. (Make sure you export with id)"
            if len(row) == 1:
                row_dict = {
                    "id": "",
                    "vi": row[0],
                    "en": "",
                    "examples": "",
                }
            else:
                row_dict = {
                    "id": row[0],
                    "vi": row[1],
                    "en": row[2],
                    "examples": row[3],
                }
            if len(row) == 5:
                row_dict["wiktdata"] = row[4]
            deck.append(row_dict)

    return deck, metadata


def write_deck(deck: list[dict], metadata: list[str], out_path: str):
    """
    Writes a deck of notes and metadata to a specified file in CSV format.

    Parameters
    ----------
    deck : list of dict
        A list of dictionaries where each dictionary represents a note.
        Each dictionary should have the keys: "id", "vi", "en", "examples", "wiktdata".
    metadata : list of str
        A list of strings representing metadata lines to be written at the beginning of the file.
    out_path : str
        The file path where the CSV file will be written.

    Writes
    ------
    None
        A CSV file at the specified out_path with the provided deck and metadata.
        The CSV file will use tab as the delimiter and will not quote any fields.
    """
    with open(out_path, "w", newline="", encoding="utf-8") as csv_file:
        fieldnames = ["id", "vi", "en", "examples", "wiktdata"]
        writer = csv.DictWriter(
            csv_file,
            fieldnames=fieldnames,
            delimiter="\t",
            quoting=csv.QUOTE_NONE,
            quotechar=None,
            escapechar=None,
        )

        for metadata_line in metadata:
            csv_file.write(metadata_line)

        for note_dict in deck:
            writer.writerow(note_dict)

    print(f"Writing deck to {out_path}")
