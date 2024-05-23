# ieeexplorer_parser
Async parser for ieeexplore.ieee.org. You can choose query to parse, save dataframe .pickle format and translate parsed articles to russian via googletranslate api. <br />
python > 3.11 not supported (aiohttp)
Parse articles from IEEE Xplore.

  This command allows you to parse articles from IEEE Xplore based on the
  specified query and number of articles.

  Example: python main.py 100 "Agricultural Production" out.csv

  Args:

      number_of_docs (int): The number of articles to parse. The number of
      articles must be divisible by 25 without a remainder.

      query (str): The search query to use for retrieving articles. If you
      want to use multiple words,     use double quotes. For example, to
      search for articles about "machine learning", you would use the query
      "machine learning".

      output (str): The file path to save the parsed articles. The file will
      be saved in CSV or pickle format.

      translate (bool, optional): Whether to translate the titles and
      abstracts to Russian. Defaults to False.

      id (bool, optional): Whether to include the article IDs in the output.
      Defaults to True.

      publicationDate (bool, optional): Whether to include the publication
      dates in the output. Defaults to True.

      year_only (bool, optional): Whether to include only the year of
      publication. Defaults to True.

      title (bool, optional): Whether to include the article titles in the
      output. Defaults to True.

      abstract (bool, optional): Whether to include the article abstracts in
      the output. Defaults to True.

      authors (bool, optional): Whether to include the author names in the
      output. Defaults to True.

Arguments:
  NUMBER_OF_DOCS  [required]
  QUERY           [required]
  OUTPUT          [required]

Options:
  --translate / --no-translate    [default: no-translate]
  --id / --no-id                  [default: id]
  --publicationdate / --no-publicationdate
                                  [default: publicationdate]
  --year-only / --no-year-only    [default: year-only]
  --title / --no-title            [default: title]
  --abstract / --no-abstract      [default: abstract]
  --authors / --no-authors        [default: authors]
  --install-completion [bash|zsh|fish|powershell|pwsh]
                                  Install completion for the specified shell.
  --show-completion [bash|zsh|fish|powershell|pwsh]
                                  Show completion for the specified shell, to
                                  copy it or customize the installation.
  --help                          Show this message and exit.
