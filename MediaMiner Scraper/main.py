import sys
import requests
from bs4 import BeautifulSoup
import typing
from ebooklib import epub
from typing import List


class MediaMinerScraper:
	def __init__(self, URL: str) -> None:
		self.SITEDOMAIN = "https://www.mediaminer.org"
		self.BOOK = epub.EpubBook()
		self.EPUB_CHAPTERS = []
		self.URL = URL
		self.scraper = requests.Session()
		webPage = self.scraper.get(self.URL)
		self.soup = BeautifulSoup(webPage.text, "lxml")
		self.content = self.soup.find("div", {"id": "content"})
		self.main_content = self.content.find("div", {"role": "main", "class": "d-flex flex-row"})
		# The ACTUAL main content (that's in an article tag)
		self.main_article = self.main_content.find_all("div", {"class": "col-md-8"})[0].article

	@staticmethod
	def python_dict_to_HTML_anchor_tag(data: typing.Dict[str, str]) -> str:
		return f'<a href="{data["link"]}">{data["name"]}</a>'

	def get_story_title(self) -> str:
		return self.main_article.find("h1", {"id": "post-title"}).get_text(strip=True).split("❯")[-1]

	def get_story_author(self) -> typing.Dict[str, str]:
		author_name = self.main_article.find("div", {"class": "post-meta clearfix"}).find_all("a")[0].get_text(
			strip=True)
		author_url = self.main_article.find("div", {"class": "post-meta clearfix"}).find_all("a")[0]['href']
		return {"name": author_name, "link": f"{self.SITEDOMAIN}{author_url}"}

	def get_story_metadata(self) -> typing.Dict[str, str]:
		rating = self.main_article.find("div", {"id": "post-rating"}).get_text(strip=True)
		summary = self.main_article.find("div", {"class": "post-meta clearfix"}).find_all("br")[0].next_sibling.strip()
		list_of_stats = self.main_article.find("div", {"class": "post-meta clearfix"}).contents[9:]
		list_of_stats_in_html = []
		for i in list_of_stats:
			if '<a href="/fanfic/' in str(i):
				list_of_stats_in_html.append(str(i).replace('<a href="/fanfic/', f'<a href="{self.SITEDOMAIN}/fanfic/'))
			elif "|" in str(i).strip():
				list_of_stats_in_html.append(str(i).replace("|", "<br/>"))
			else:
				list_of_stats_in_html.append(str(i))
		if str(list_of_stats_in_html[0]) in ["<br/>", "\n"]:
			del list_of_stats_in_html[0]
		return {"rating": rating, "summary": summary,
				"stats_in_html": f"<p>{''.join(list_of_stats_in_html)}</p>"}

	def make_intro_chapter(self) -> None:
		# intro chapter
		intro_chapter = epub.EpubHtml(title='Introduction', file_name='intro.xhtml', lang='en')
		stats = self.get_story_metadata()
		intro_chapter.set_content(f"""
		<html>
			<body>
				<h1>{self.get_story_title()}</h1>
				<h2>By {self.python_dict_to_HTML_anchor_tag(self.get_story_author())}</h2>
				<div>
					<h3>Rating:</h3>
					<p style='font-weight: normal;'>{stats["rating"]}</p>
					<h3>Summary:</h3>
					<p>{stats["summary"]}</p>
					<h3>Stats:</h3>
					<p>{stats["stats_in_html"]}</p>
				</div>
			</body>
		</html>
		""")
		self.BOOK.add_item(intro_chapter)
		self.EPUB_CHAPTERS.append(intro_chapter)

	def get_chapters_list(self) -> List[str]:
		# For some reason, the chapters list is just a bunch of `anchor` tags in a `paragraph`.
		blockquote = self.main_article.find("blockquote").find_all("p")[-1].find_all("a")
		return [f"<a href='{self.SITEDOMAIN + i['href']}'>{i.get_text(strip=True)}</a>" for i in blockquote]

	def get_chapter(self):
		chapters_list = self.get_chapters_list()
		for chapter in chapters_list:
			chapter_url = BeautifulSoup(chapter, "lxml").find("a")["href"]
			chapter_name = BeautifulSoup(chapter, "lxml").find("a").get_text(strip=True)
			chapter_page = self.scraper.get(chapter_url)
			chapter_soup = BeautifulSoup(chapter_page.text, "lxml")
			chapter_content = chapter_soup.find("div", {"id": "content"})
			chapter_main_content = chapter_content.find("div", {"role": "main", "class": "d-flex flex-row"})
			chapter_main_article = chapter_main_content.find_all("div", {"class": "col-md-8"})[0].article
			chapter_summary = chapter_main_article.find("div", {"class": "post-meta clearfix"}).find_all("br")[
				0].next_sibling
			if chapter_summary.get_text(strip=True).startswith("Anime/Manga:"):
				chapter_summary = None
				chapter_summary_text = ""
			else:
				chapter_summary_text = f"""
				<div style='margin:15px'>
					<h4>Summary:</h4>
					<p>{chapter_summary}</p>
				</div>
				"""
			chapter_text = chapter_main_article.find("div", {"id": "fanfic-text"})
			chapter_text_string = str(chapter_text).replace(
				'style=" padding: 0.00mm 0.00mm 0.00mm 0.00mm;"',
				'style=" line-height: 1.5; margin: 8px 0; padding: 4px 0;"'
			)
			chapter_text = BeautifulSoup(chapter_text_string, "lxml")
			epub_chapter = epub.EpubHtml(
				title=chapter_name,
				file_name=f'{MediaMinerScraper.clean_filename(chapter_name)}.xhtml',
				lang='en'
			)
			epub_chapter.content = f"""
				<html>
					<head>
						<link rel="stylesheet" href="style/style.css">
					</head>
					<body>
						<h2 style='text-align:center'>{chapter_name}</h2>
						<p>{chapter_summary_text}{chapter_text}</p>
					</body>
				</html>
			"""
			self.BOOK.add_item(epub_chapter)
			self.EPUB_CHAPTERS.append(epub_chapter)

	@staticmethod
	def clean_filename(filename: str) -> str:
		return ''.join([c for c in filename if c not in " %:/,.\\[]<>*?"])

	def makeEpub(self):
		self.BOOK.set_identifier(self.URL)
		self.BOOK.set_title(self.get_story_title())
		self.BOOK.set_language('en')
		self.BOOK.add_author(self.get_story_author()["name"])
		self.BOOK.add_metadata('DC', 'description', self.get_story_metadata()["summary"])
		self.BOOK.add_metadata('DC', 'rating', self.get_story_metadata()["rating"])
		self.BOOK.add_metadata('DC', 'source', self.URL)

	def run(self):
		self.makeEpub()
		self.make_intro_chapter()
		self.get_chapter()
		self.BOOK.toc = tuple(['nav', *self.EPUB_CHAPTERS])
		self.BOOK.add_item(epub.EpubNcx())
		self.BOOK.add_item(epub.EpubNav())
		self.BOOK.spine = ['nav', *self.EPUB_CHAPTERS]
		epub.write_epub(f'{self.get_story_title()}.epub', self.BOOK, {})


if __name__ == '__main__':
	mmscraper = MediaMinerScraper(sys.argv[1])
	mmscraper.run()
