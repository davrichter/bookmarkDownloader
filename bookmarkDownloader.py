import json
import os
import re
import sys

import requests
import unicodedata


def download_files(data, destination_directory):
    for i in data:
        if i["type"] == "text/x-moz-place-container":
            try:
                directory = i["title"]
                os.mkdir(destination_directory + "/" + directory)

            # Can happen if the directory doesn't have a name
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
                page = requests.get(i["uri"], timeout=5, allow_redirects=True)

                print(page.headers.get("content-type"))

                if i["uri"].split(".")[-1] == "pdf":
                    file_extension = ".pdf"
                else:
                    file_extension = ".html"

                filename = destination_directory + "/" + slugify(i["title"]) + file_extension

                print(f"Downloading {filename}...")

                file = open(filename, "wb")
                file.write(page.content)

            except requests.exceptions.InvalidSchema as e:
                print(f"""{i["uri"]} \n {e}""")

            except requests.exceptions.ReadTimeout as e:
                print(e)

            except requests.exceptions.ConnectTimeout as e:
                print(e)

            except UnicodeDecodeError as e:
                print(e)

            except UnicodeEncodeError as e:
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
    """
    sys.argv[1] is the path of the exported bookmarks file
    sys.argv[2] is the path of the destination folder for the files
    """
    f = open(sys.argv[1], encoding="utf8")

    download_files(json.load(f)["children"], sys.argv[2])
