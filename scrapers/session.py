import os
import sys
import hashlib
import pathlib
from typing import Tuple

import requests
from bs4 import BeautifulSoup


class ScrapingSession:

    CACHE_DIR = pathlib.Path(__file__).resolve().parent.parent / "cache" / "html"
    IMAGE_DIR = pathlib.Path(__file__).resolve().parent.parent / "images"

    def __init__(self, scraper_name, args):
        self.s = requests.Session()
        self.s.headers["User-Agent"] = "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:87.0) Gecko/20100101 Firefox/87.0"
        self.cached = args["cached"]
        self.scraper_name = scraper_name
        self.image_dir = self.IMAGE_DIR / self.scraper_name

    def log(self, *args, **kwargs):
        print(*args, **kwargs, file=sys.stderr)

    def get_html(self, url: str, encoding: str = None) -> str:
        if self.cached:
            url_hash = hashlib.md5(url.encode("ascii", errors="replace")).hexdigest()
            cache_file = self.CACHE_DIR.joinpath(f"{url_hash}.html")
            if cache_file.exists():
                return cache_file.read_text()

        for try_num in range(3):
            try:
                self.log("downloading", url)
                response = self.s.get(url, timeout=3)
                if encoding is None:
                    text = response.text
                else:
                    text = response.content.decode(encoding)
                break
            except requests.ConnectionError:
                if try_num == 2:
                    raise

        if self.cached:
            os.makedirs(self.CACHE_DIR, exist_ok=True)
            cache_file.write_text(text)

        return text

    def get_soup(self, url: str, encoding: str = None) -> BeautifulSoup:
        return BeautifulSoup(self.get_html(url, encoding=encoding), features="html.parser")

    def download_image(
            self,
            url: str,
            short_filename: bool = False,
    ) -> Tuple[str, bool]:
        img_ext = url.split("?")[0].split(".")[-1] or "unknown"
        url_hash = hashlib.md5(url.encode("ascii", errors="replace")).hexdigest()
        image_dir = self.image_dir / url_hash[:2]
        image_file = image_dir / f"{url_hash}.{img_ext}"

        downloaded = False
        if not image_file.exists():
            self.log("downloading image", url)
            response = self.s.get(url)

            os.makedirs(image_dir, exist_ok=True)

            image_file.write_bytes(response.content)
            downloaded = True

        if short_filename:
            image_file = pathlib.Path(str(image_file)[len(str(self.IMAGE_DIR))+1:])

        return image_file, downloaded
