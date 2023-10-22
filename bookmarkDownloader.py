import json
import random
import string
import sys
import os
import requests


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
            print("Hello")
            try:
                page = requests.get(i["uri"], timeout=5)

                file_extension = ""
                if i["uri"].split(".")[-1] == "pdf":
                    file_extension = ".pdf"
                else:
                    file_extension = ".html"

                try:
                    f = open(i["title"] + file_extension, "w", encoding="utf8")

                # if there are characters the filesystem can't handle this will happen
                except OSError:
                    f = open(destination_directory + ''.join(
                        random.choice(string.ascii_lowercase) for i in range(6)) + ".html",
                             "w", encoding="utf8")

                f.write(page.content.decode())

            except requests.exceptions.InvalidSchema as e:
                print(f"""{i["uri"]} \n {e}""")

            except requests.exceptions.ReadTimeout as e:
                print(e)

            except requests.exceptions.ConnectTimeout as e:
                print(e)

            except UnicodeDecodeError as e:
                print(e)


if __name__ == "__main__":
    download_bookmarks(sys.argv[1], sys.argv[2])
