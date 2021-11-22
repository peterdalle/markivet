import re
import datetime
import json
import glob
from dateutil import parser


class NewsArticle:
    """Represents a single news article."""

    def __init__(self):
        self.id = None
        self.title = None
        self.section = None
        self.newspaper = None
        self.date = None
        self.date_raw = None
        self.page = None
        self.edition = None
        self.lead = None
        self.body = None
        self.imagetext = None
        self.url = None

    def to_dict(self) -> dict:
        article_dict = {
            "title": self.title,
            "section": self.section,
            "newspaper": self.newspaper,
            "date": self.date,
            "date_raw": self.date_raw,
            "page": self.page,
            "edition": self.edition,
            "url": self.url,
            "lead": self.lead,
            "body": self.body,
            "imagetext": self.imagetext,
        }
        if self.id:
            article_dict = self._add_id(article_dict)
        return article_dict

    def _add_id(self, article_dict):
        id_dict = {"id": self.id}
        id_dict.update(article_dict)
        return id_dict

    @property
    def is_missing(self) -> bool:
        if False in [self.title, self.section, self.newspaper, self.page, self.edition]:
            return True
        if not self.lead and not self.body:
            return True
        return False

    def print_summary(self):
        print(f"""    Title:  {self.title}
Newspaper:  {self.newspaper}
  Section:  {self.section}
     Date:  {self.date}
 Date raw:  {self.date_raw}
     Page:  {self.page}
  Edition:  {self.edition}
     Lead:  {self._preview_text(self.lead)}
     Body:  {self._preview_text(self.body)}
      URL:  {self.url}""")

    def _preview_text(self, text: str) -> str:
        if len(text) > 15:
            text = text.replace(r"\n", " ").replace(r"\l", " ")
            return f"{text[:10]} ... ({len(text)} chars)"
        return text

    def __str__(self) -> str:
        chars = len(self.lead) + len(self.body)
        return f"<{self.newspaper}> {self.title} ({chars} chars)"

    def __repr__(self) -> str:
        return self.__str__()


class ArticleParser:
    """Parser for a single article text string. In other words, takes
    a text string of the article and spits out a NewsArticle object.

    Assumes that the default settings were used during the TXT
    export at Retriever Mediearkivet (including table of contents)."""
    
    def parse(self, content: str) -> NewsArticle:
        if not content:
            raise ValueError("Argument 'content' is empty.")
        if content == "":
            return NewsArticle()
        content = self._remove_crap_from_article(content)
        metadata, lead, body = self._split_into_three_parts(content)
        news = self._parse_metadata(metadata)
        news.lead = lead
        news.body = body
        news.url = self._find_url(content)
        return news

    def _remove_crap_from_article(self, article: str) -> str:
        l = []
        for line in article.split("\n"):
            if not self._is_bad_line(line):
                l.append(line)
        article = "\n".join(l)
        i = article.find(".©")
        if i != -1:
            article = article[:i + 1]
        return self._strip_text(article)

    def _is_bad_line(self, line: str) -> bool:
        bad_lines_contain = [
            "====================",
            "Artiklar får ej distribueras utanför den egna organisationen utan godkännande från Retriever",
        ]
        for bad in bad_lines_contain:
            if bad in line:
                return True
        return False

    def _strip_text(self, text: str) -> str:
        if not text:
            return ""
        text = text.rstrip().rstrip("\n")
        text = text.lstrip().lstrip("\n")
        return text

    def _split_into_three_parts(self, article: str) -> tuple:
        matches = re.split("\n\n", article)
        if matches:
            if len(matches) >= 3:
                return matches[0], matches[1], matches[2]
            if len(matches) == 2:
                return matches[0], "", matches[1]  # assumes that there is no lead
            if len(matches) == 1:
                return matches[0], "", ""  # assumes that there is no lead or body
            raise ValueError(f"Expected 1 or more parts (metadata, lead/body)")
        raise ValueError("Expected to find parts separated by \\n\\n, but I didn't find any")

    def _parse_metadata(self, article: str) -> NewsArticle:
        lines = article.split("\n")
        lines = self._strip_empty_lines(lines)
        news = NewsArticle()
        news.title = lines[0]
        news.section = self._find_section(lines)
        news.newspaper = self._find_newspaper(lines)
        news.date_raw = self._find_date(lines)
        news.date = self._try_parse_date(news.date_raw)
        news.page = self._find_page(lines)
        news.edition = self._find_edition(lines)
        news.imagetext = self._find_imagetext(lines)
        news.url = self._find_url(lines)
        return news

    def _strip_empty_lines(self, lines: list) -> list:
        l = []
        for line in lines:
            line = line.strip()
            if line and not line == "":
                l.append(line)
        return l

    def _find_section(self, lines: list) -> list:
        # matches CAPITAL LETTERS
        for line in lines:
            if re.search(r"([A-ZÅÄÖ0-9]){2}\.", line):
                return line
        return ""

    def _find_newspaper(self, lines: list) -> str:
        # matches line containing newspaper by looking for date e.g. Aftonbladet, 2021-09-29
        for line in lines:
            if re.search(r"(\d{4}-\d{1,2})", line):
                splitted = line.split(",")
                return splitted[0]
        return ""

    def _find_date(self, lines: list) -> str:
        # matches date e.g. 2021-09-29 or 2021-09-29 14:22
        for line in lines:
            match = re.search(r"\d{4}-\d{2}-\d{2}\s*(?:\d{2}:\d{2}(?::\d{2})?)?", line)
            if match:
                return match.group()
        return ""

    def _try_parse_date(self, date_string: str) -> datetime:
        if not date_string:
            return None
        return parser.parse(date_string)

    def _find_page(self, lines: list) -> str:
        for line in lines:
            if line.startswith("Sida"):
                return line
        return ""

    def _find_edition(self, lines: list) -> str:
        for line in lines:
            if line.startswith("Publicerat i") or line.startswith("Publicerat på"):
                return line
            if line.startswith("Sänt i"):
                return line
        return ""

    def _find_imagetext(self, lines: list) -> str:
        for line in lines:
            if line.startswith("Bildtext:"):
                return line
        return ""

    def _find_url(self, line: str) -> str:
        # matches retriever link to full text version
        if "http://ret.nu/" in line or "https://ret.nu/" in line:
            url = re.search("(?P<url>https?://[^\s]+)", line).group("url")
            if url:
                return url
            return line
        return ""


class Markivet:
    """Loads, parses, and saves Retriever Mediearkivet TXT files."""

    def __init__(self, file: str, verbose=True, parser=ArticleParser):
        self._file = file
        self._verbose = verbose
        self._parser_class = parser
        self._articles = []
        self._files_loaded = []
        self._load_file(file)

    @classmethod
    def from_articles(cls, me, articles: list):
        """Load articles from a list of articles."""
        markivet = cls(file=None, verbose=me.verbose, parser=me.parser)
        markivet.articles = articles
        return markivet

    @classmethod
    def from_folder(cls, path: str, verbose=True):
        """Load articles from all specified files in a folder, e.g. `/my/path/*.txt`."""
        markivet = Markivet(file=None, verbose=verbose)
        markivet._load_path(path)
        return markivet

    @property
    def files(self) -> list:
        """Gets a list of loaded files."""
        return self._files_loaded

    @property
    def articles(self) -> list:
        """Gets a list of parsed articles."""
        return self._articles

    @articles.setter
    def articles(self, value: list):
        self._articles = value

    @property
    def verbose(self) -> bool:
        return self._verbose

    @verbose.setter
    def verbose(self, value: bool):
        self._verbose = value

    @property
    def parser(self) -> bool:
        return self._parser_class

    def _load_path(self, path: str):
        for file in glob.glob(path):
            self._load_file(file)

    def _load_file(self, file: str):
        if not file:
            return
        self._print(f"Loading {file}")
        with open(file, "r", encoding="UTF-8") as f:
            lines = f.readlines()
        if lines:
            article_texts = self._find_all_article_texts(lines)
            self._articles.extend(self._parse_all_article_texts(article_texts))
            self._files_loaded.append(file)
        else:
            self._print(f"No content in {file}")

    def _print(self, text: str):
        if self._verbose:
            print(text)

    def remove_duplicates(self):
        """Removes all duplicate articles."""
        self._print(f"Searching for duplicates in {len(self._articles)} articles...")
        if not self._articles:
            return
        self._articles = list(set(self._articles))
        survived = []
        before = len(self._articles)
        progress = ProgressBar(before)
        # Yes, this is slow but it works...
        for i, article in enumerate(self._articles):
            if not self._contain_article(article, survived):
                survived.append(article)
            if self._verbose:
                progress.print_bar(i)
        if self._verbose:
            progress.stop()
        self._articles = survived
        removed = before - len(survived)
        if removed > 0:
            self._print(f"Removed {removed} duplicates")
        else:
            self._print(f"No duplicates found")

    def add_id(self):
        """Add an ID to to each article."""
        id_articles = []
        for i, article in enumerate(self._articles):
            article.id = i + 1
            id_articles.append(article)
        self._articles = id_articles

    def _contain_article(self, article: NewsArticle, article_list: list) -> bool:
        for current_article in article_list:
            if current_article.to_dict() == article.to_dict():
               return True
        return False

    def save(self, file: str, encoding="UTF-8"):
        """Saves the parsed file into a JSON file."""
        if len(self._articles) == 0:
            self._print("Nothing to save")
            return
        with open(file, "w", encoding=encoding) as f:
            article_json = [article.to_dict() for article in self._articles]
            f.write(json.dumps(article_json, sort_keys=False, indent=4, default=str))
        self._print(f"Saved {len(self._articles)} articles to {file}")

    def _find_all_article_texts(self, lines: str) -> list:
        i = self._find_article_start_index(lines)
        cumulative = []
        article_texts = []
        for line in lines[i:]:
            cumulative.append(line)
            if "===========" in line:
                article_texts.append("\n".join(line.strip() for line in cumulative))
                cumulative.clear()
        article_texts.append("\n".join(cumulative))
        #self._print(f"Extracted {len(article_texts)} article texts")
        return article_texts

    def _find_article_start_index(self, lines: list) -> int:
        prev_line = None
        for i, line in enumerate(lines):
            if prev_line == "\n" and line == "\n":
                return i
            prev_line = line
        return 0

    def _parse_all_article_texts(self, article_texts: str) -> list:
        errors = 0
        articles = []
        for i, article_text in enumerate(article_texts):
            #text_preview = article_text[:50].replace("\n", " ").strip()
            #self._print(f"Parsing article #{i + 1} '{text_preview}...'")
            news = self._parse_article_text_into_news(article_text)
            if news:
                articles.append(news)
            else:
                self._print(f"Parser couldn't identify article #{i + 1}")
                errors += 1
        #error_message = f", {errors} of them contained errors" if errors > 0 else ""
        #self._print(f"Parsed {i + 1} articles" + error_message)
        return articles

    def _parse_article_text_into_news(self, content: str) -> NewsArticle:
        parser = self._parser_class()
        news = parser.parse(content)
        return news

    def __str__(self) -> str:
        min_date, max_date = self._date_range()
        date_range = ""
        if len(self._files_loaded) == 1:
            source = f"Loaded {self._files_loaded[0]}"
        else:
            source = f"Loaded {len(self._files_loaded)} files"
        if min_date and max_date:
            date_range = f", from {min_date.date()} to {max_date.date()}"
        return f"{source} ({len(self.articles)} articles{date_range})"

    def _date_range(self) -> tuple:
        min_date = None
        max_date = None
        for article in self.articles:
            if article.date:
                if not min_date:
                    min_date = article.date
                if not max_date:
                    max_date = article.date
                if article.date < min_date:
                    min_date = article.date
                if article.date > max_date:
                    max_date = article.date
        if min_date and max_date:
            return min_date, max_date
        return None, None

    def __repr__(self) -> str:
        return self.__str__()

    def __iter__(self):
        return iter(self._articles)

    def __len__(self) -> int:
        return len(self._articles)

    def __add__(self, other: object) -> object:
        if type(self) != type(other):
            raise TypeError("Cannot add together, not the same type")
        return Markivet.from_articles(self, self._articles + other.articles)


class ProgressBar():
    """Simple progress bar that shows percent complete."""

    def __init__(self, max_count: int, decimals=1, prefix="[", char="█", suffix="]", width=50):
        self._max_count = max_count
        self._decimals = decimals
        self._prefix = prefix
        self._char = char
        self._suffix = suffix
        self._width = width

    def print_bar(self, iteration: int):
        percent = 100 * (iteration / float(self._max_count))
        percent = ("{0:." + str(self._decimals) + "f}").format(percent)
        pad_width = int(self._width * iteration // self._max_count)
        bar = self._char * pad_width + "-" * (self._width - pad_width)
        print(f"\r{self._prefix}{bar}{self._suffix} {percent}%", end="\r")

    def stop(self):
        self.print_bar(self._max_count)
        print()

if __name__ == "__main__":
    print("Markivet is a library and cannot be runned as an independent program.")
