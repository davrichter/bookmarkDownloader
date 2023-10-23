import json
import os
import re
import sys

import requests
import unicodedata


def download_bookmarks(bookmarks_path, destination_directory):
    f = open(bookmarks_path, encoding="utf8")

    data = json.load(f)

    data = data["children"]
    for i in data:
        print(i)
        print("\n\n----------------\n\n")

    download_files(data, destination_directory)


def download_files(data, destination_directory):
    for i in data:
        if i["type"] == "text/x-moz-place-container":
            directory = ""
            try:
                directory = i["title"]
                os.mkdir(destination_directory + "/" + directory)
            except FileExistsError:
                directory = i["guid"]
                os.mkdir(destination_directory + "/" + directory)

            print(destination_directory + "/" + directory)
            try:
                download_files(i["children"], destination_directory + "/" + directory)

            # Directory is empty
            except KeyError as e:
                print(e)

        elif i["type"] == "text/x-moz-place":
            try:
                page = requests.get(i["uri"], timeout=5)

                file_extension = ""
                if i["uri"].split(".")[-1] == "pdf":
                    file_extension = ".pdf"
                else:
                    file_extension = ".html"

                filename = destination_directory + "/" + slugify(i["title"]) + file_extension

                print(f"Downloading {filename}...")

                f = open(filename, "w", encoding="utf8")

                f.write(page.content.decode())

            except requests.exceptions.InvalidSchema as e:
                print(f"""{i["uri"]} \n {e}""")

            except requests.exceptions.ReadTimeout as e:
                print(e)

            except requests.exceptions.ConnectTimeout as e:
                print(e)

            except UnicodeDecodeError as e:
                print(e)


def slugify(value, allow_unicode=False):
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize("NFKC", value)
    else:
        value = (
            unicodedata.normalize("NFKD", value)
            .encode("ascii", "ignore")
            .decode("ascii")
        )
    value = re.sub(r"[^\w\s-]", "", value.lower())
    return re.sub(r"[-\s]+", "-", value).strip("-_")


if __name__ == "__main__":
    download_bookmarks(sys.argv[1], sys.argv[2])
