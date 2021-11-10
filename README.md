# Markivet - convert Mediearkivet text files into structured data

Python app **Markivet** helps you convert TXT files exported from Retriever Mediearkivet into JSON files with structured metadata.

The purpose is to make large-scale text analysis easier to do.

## Install

```py
pip install git+https://github.com/peterdalle/markivet.git@v0.1
```

## Usage

Convert a file:

```py
from markivet import Markivet

markivet = Markivet("aftonbladet.txt")
markivet.save("aftonbladet.json")
```

Show a summary:

```py
print(markivet)
```

Convert multiple files:

```py
ab1 = Markivet("aftonbladet1.txt")
ab2 = Markivet("aftonbladet2.txt")
ab3 = Markivet("aftonbladet3.txt")

markivet = ab1 + ab2 + ab3
markivet.remove_duplicates()
markivet.save("aftonbladet.json")
```

Convert all TXT files in a directory:

```py
markivet = Markivet.from_path("/home/username/*.txt")
markivet.save("articles.json")
```

Loop through articles and display:

```py
markivet = Markivet("aftonbladet.txt")

for article in markivet:
    print(article.title) 
    print(article.section)
    print(article.page)
    print(article.newspaper)
    print(article.edition)
    print(article.date)      # parsed date as yyyy-mm-dd hh:mm:ss
    print(article.date_raw)  # date as is it was found
    print(article.lead)
    print(article.body)
```

## Write your own parser if you don't like the default

You can also write your own parser if you don't like the default `ArticleParser`. 

A parser is responsible for converting the article text string into structured metadata (of the type `NewsArticle`). This is useful if the current parser doesn't work as you wish.

How to:

1. Create your own class, like `MyOwnParser`
2. Add a `parse()` method
3. The method must take a string as an input argument
4. The method must return a `NewsArticle` object
5. When you want to use your parser, pass the class name as an argument: `Markivet("file.txt",  parser=MyOwnParser)`

Example:

```py
from markivet import Markivet, NewsArticle

class MyOwnParser:

    def parse(self, content: str) -> NewsArticle:
        """Extract the info you want, put it into NewsArticle, and return it"""
        news = NewsArticle()
        news.title = "I see no God here other than me"
        news.newspaper = "Journal of Advanced Self-Indulgence"
        news.lead = "I walked by the mirror and looked God into the eyes."
        news.body = "True story."
        news.section = "Domestic News"
        return news

journal = Markivet("journal.txt", parser=MyOwnParser)  # <---- Inject your parser here
journal.save("journal.json")
```

## Documentation

Markivet consists of three classes.

Class | What it does
:------------ | :--------------------------
`Markivet` | Loads TXT files, identifies all articles in a TXT file, and saves JSON files
`ArticleParser` | Converts an article text string into a `NewsArticle` object
`NewsArticle` | Represents a news article with title, name of newspaper, lead, body, pages etc.


## Support

File a new issue if you find an error with the software.
