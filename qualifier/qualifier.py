from enum import auto, StrEnum
import re
import warnings

MAX_QUOTE_LENGTH = 50


# The two classes below are available for you to use
# You do not need to implement them
class VariantMode(StrEnum):
    NORMAL = auto()
    UWU = auto()
    PIGLATIN = auto()


class DuplicateError(Exception):
    """Error raised when there is an attempt to add a duplicate entry to a database"""


# Implement the class and function below
class Quote:
    def __init__(self, quote: str, mode: "VariantMode") -> None:
        if len(quote) > MAX_QUOTE_LENGTH:
            raise ValueError("Quote is too long")
        elif len(quote) == 0:
            warnings.warn("Empty quote")
        self.quote = quote
        self.mode = mode
        try:
            Database.add_quote(self)
        except DuplicateError as de:
            print("Quote has already been added previously")

    def __str__(self) -> str:
        return self._create_variant()

    def _create_variant(self) -> str:
        match self.mode:
            case VariantMode.NORMAL:
                return self.normalify()
            case VariantMode.PIGLATIN:
                return self.pigliatinify()
            case VariantMode.UWU:
                return self.uwuify()

    def uwuify(self) -> str:
        uwu_quote = self.quote

        # apply letter transformations
        letter_transformations = {
            "L": "W",
            "l": "w",
            "R": "W",
            "r": "w",
        }
        for old, new in letter_transformations.items():
            uwu_quote = uwu_quote.replace(old, new)

        # apply stutter
        # find all available words to apply stutter to
        stutter_finder = re.compile("\s(([Uu])\S+)")
        stutter_matches = stutter_finder.finditer(uwu_quote)

        # iterate through all the possible stutter words
        stutter_counter = 0
        for stutter_match in stutter_matches:
            if len(uwu_quote) <= MAX_QUOTE_LENGTH - 2:  # check if the length of the quote is small enough
                start, end = stutter_match.span()
                # adjust start and end when previous stutters displaced the words
                start, end = start + 2*stutter_counter, end + 2*stutter_counter
                uwu_quote = uwu_quote[:start] + f" {stutter_match.group(2)}-{stutter_match.group(1)}" + uwu_quote[end:]
            else:
                warnings.warn("Quote too long, only partially transformed")
                break
            stutter_counter += 1

        if uwu_quote == self.quote:
            raise ValueError("Quote was not modified")

        return uwu_quote

    def pigliatinify(self) -> str:
        vowels = "aeiouAEIOU"
        piglatin_words = []
        words_finder = re.compile("(\S+)")
        word_matches = words_finder.finditer(self.quote)

        for word_match in word_matches:
            word = word_match.group(0)
            if word[0] in vowels:
                piglatin_words.append(word + 'way')
            else:
                pivot = 0
                while word[pivot] not in vowels:
                    pivot += 1
                piglatin_words.append(word[pivot:] + word[:pivot] + 'ay')

        piglatin_quote = ' '.join(piglatin_words)
        if len(piglatin_quote) <= MAX_QUOTE_LENGTH:
            return piglatin_quote.capitalize()
        else:
            raise ValueError("Quote was not modified")

    def normalify(self) -> str:
        return self.quote


def run_command(command: str) -> None:
    """
    Will be given a command from a user. The command will be parsed and executed appropriately.

    Current supported commands:
        - `quote` - creates and adds a new quote
        - `quote uwu` - uwu-ifys the new quote and then adds it
        - `quote piglatin` - piglatin-ifys the new quote and then adds it
        - `quote list` - print a formatted string that lists the current
           quotes to be displayed in discord flavored markdown
    """
    # compile a regular expression to extract the quote, command and variant
    re_extractor = re.compile("^(?P<command>[Qq][Uu][Oo][Tt][Ee]) "  # command
                              "(?P<variant>[Pp][Ii][Gg][Ll][Aa][Tt][Ii][Nn]|[Uu][Ww][Uu]|[Ll][Ii][Ss][Tt])?"  # variant
                              "(?: ?(?P<delimiter>\"|“|'')(?P<quote>.*)(?:(?P=delimiter)|”))?$")  # quote

    # match the pattern and store named groups in the `matches` object
    try:
        matches = re_extractor.match(command.strip())
    except re.error as e:
        raise e

    # check if any mandatory group did not match to raise the `Invalid command` error
    if not matches:
        raise ValueError("Invalid command")

    # create the Quote object with the proper VariantMode
    match str(matches.group("variant")).upper():
        case "UWU":
            Quote(matches.group("quote"), VariantMode.UWU)
        case "PIGLATIN":
            Quote(matches.group("quote"), VariantMode.PIGLATIN)
        case "LIST":
            if matches.group("quote"):
                raise UserWarning("Quote given with `list` command : quote will be ignored")
            print(*[f'- {q}' for q in Database.get_quotes()], sep='\n')
        case _:
            Quote(matches.group("quote"), VariantMode.NORMAL)


# The code below is available for you to use
# You do not need to implement it, you can assume it will work as specified
class Database:
    quotes: list["Quote"] = []

    @classmethod
    def get_quotes(cls) -> list[str]:
        "Returns current quotes in a list"
        return [str(quote) for quote in cls.quotes]

    @classmethod
    def add_quote(cls, quote: "Quote") -> None:
        "Adds a quote. Will raise a `DuplicateError` if an error occurs."
        if str(quote) in [str(quote) for quote in cls.quotes]:
            raise DuplicateError
        cls.quotes.append(quote)
