from endpoints import fetch_cookies, fetch_story_content_zip, fetch_library
from epub_generator import EPUBGenerator
from parser import fetch_image, fetch_tree_images, clean_tree
from asyncio import run
from pathlib import Path
from os import environ, remove
from dotenv import load_dotenv
from zipfile import ZipFile
from json import load, dump
from re import sub

load_dotenv()


def ascii_only(string: str):
    string = string.replace(" ", "_")
    return sub(
        r"[^qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM1234567890\-\_)(`~.><\[\]{}]",
        "",
        string,
    )


async def main(
    username: str, password: str, output_directory: Path, download_images: bool
):
    print("Logging in")
    try:
        cookies = await fetch_cookies(username, password)
    except ValueError as exception:
        if "No cookies." in str(exception):
            print("Username or password incorrect.")
            exit()
        else:
            raise(exception)

    print("Fetching library")
    stories = await fetch_library(username, cookies)
    download_history_path = Path(output_directory / "download_history")
    if download_history_path.exists():
        file = open(download_history_path, "r")
        download_history = load(file)
    else:
        download_history_path.parent.mkdir(parents=True, exist_ok=True)
        file = open(download_history_path, "x")
        download_history = {}

    print("Downloading missing/outdated stories")

    try:
        for metadata in stories:

            if (
                metadata["title"] in download_history
                and download_history[metadata["title"]] == metadata["modifyDate"]
            ):
                continue

            print(f"Downloading: {metadata['title']}")

            cover_data = await fetch_image(
                metadata["cover"].replace("-256-", "-512-")
            )  # Increase resolution
            if not cover_data:
                raise HTTPException(status_code=422)

            story_zip = await fetch_story_content_zip(metadata["id"], cookies)
            archive = ZipFile(story_zip, "r")

            part_trees: list[BeautifulSoup] = []

            for part in metadata["parts"]:

                if "deleted" in part and part["deleted"]:
                    continue

                part_trees.append(
                    clean_tree(
                        part["title"],
                        part["id"],
                        archive.read(str(part["id"])).decode("utf-8"),
                    )
                )

            images = (
                [await fetch_tree_images(tree) for tree in part_trees]
                if download_images
                else []
            )

            book = EPUBGenerator(metadata, part_trees, cover_data, images)
            book.compile()

            output_path = (
                output_directory
                / ascii_only(metadata["user"]["username"])
                / ascii_only((metadata["title"] + ".epub"))
            )

            output_path.parent.mkdir(parents=True, exist_ok=True)

            if output_path.exists():
                remove(output_path)
            output = open(output_path, "xb")
            output.write(book.dump().getvalue())
            output.close()

            download_history[metadata["title"]] = metadata["modifyDate"]
    finally:
        with open(download_history_path, "w") as file:
            dump(download_history, file)


if __name__ == "__main__":
    run(
        main(
            environ.get("USERNAME"),
            environ.get("PASSWORD"),
            Path(environ.get("OUTPUT_DIRECTORY")),
            environ.get("DOWNLOAD_IMAGES"),
        )
    )
