import traceback

from image_scraper.models import ScraperModel, MetaModel, ImageModel
from scrapers import ScrapingSession


def main(args: dict):

    if not args["gallery"] and not args["search"]:
        print("Need to specify --gallery or --search")
        exit(-1)

    session = ScrapingSession("imagefap", args)

    if args["gallery"]:
        for gallery in args["gallery"]:
            GalleryScraper(session, gallery, args).scrape()

    else:
        for page in range(args["pages"]):
            search_and_scrape_galleries(session, page, args)


class GalleryScraper:

    def __init__(self, session: ScrapingSession, number_or_url: str, args: dict):
        number = None
        try:
            number = int(number_or_url)
        except ValueError:
            pass

        if number is None:
            try:
                index = number_or_url.index("imagefap.com/pictures/")
                number = int(number_or_url[index+22:].split("/")[0])
            except:
                pass

        if number is None:
            try:
                index = number_or_url.index("?gid=")
                number = int(number_or_url[index+5:].split("/")[0])
            except:
                pass

        if number is None:
            raise ValueError(f"Do not understand gallery number/url '{number_or_url}'")

        self.number = number
        self.session = session
        self.args = args
        self.scraper_model = ScraperModel.get("imagefap", create=True)

    def scrape(self):
        gallery_url = f"https://www.imagefap.com/pictures/{self.number}/?view=2"
        soup = self.session.get_soup(gallery_url)

        title = soup.find("title").text
        if title.endswith("Porn Pics & Porn GIFs"):
            title = title[:-21].strip()

        try:
            meta_model = MetaModel.objects.get(
                scraper=self.scraper_model,
                type="gallery",
                meta_id=self.number,
            )
        except MetaModel.DoesNotExist:
            meta_model = MetaModel.objects.create(
                scraper=self.scraper_model,
                type="gallery",
                meta_id=self.number,
                data={
                    "gallery_id": self.number,
                    "gallery_title": title,
                    "gallery_url": f"https://www.imagefap.com/pictures/{self.number}/",
                }
            )

        image_urls = []
        for a in soup.find_all("a"):
            img = a.find("img")
            if img and img.attrs.get("src") and "images/thumb/" in img.attrs["src"]:
                image_urls.append((
                    a.attrs.get("href"),
                    img.attrs["src"],
                ))

        for url, thumb_url in image_urls:
            filename, downloaded = self.session.download_image(thumb_url, short_filename=True)
            if not ImageModel.objects.filter(thumb_filename=filename).exists():
                ImageModel.objects.create(
                    scraper=self.scraper_model,
                    meta_data=meta_model,
                    thumb_filename=filename,
                    thumb_url=thumb_url,
                    # Note! This is a url to a html-page, not the actual image
                    url="https://www.imagefap.com" + url,
                )

        self.session.log(f"{len(image_urls)} thumb images")


def search_and_scrape_galleries(session: ScrapingSession, page: int, args: dict):
    per_page = 150

    url = f"https://www.imagefap.com/gallery.php?search={args['search']}&page={page}&perpage={per_page}"
    soup = session.get_soup(url)

    for a in soup.find_all("a", {"class": "gal_title"}):
        if "gallery.php?gid=" in a.attrs["href"]:
            try:
                GalleryScraper(session, a.attrs["href"], args).scrape()
            except KeyboardInterrupt:
                raise
            except:
                print(
                    "ERROR in gallery", a.attrs["href"],
                    traceback.format_exc(),
                )
