import io
import os
import random
import argparse


def get_args():
    """Return parsed command line arguments
    Two optional arguments in total: --import_from, --export_to
    """

    parser = argparse.ArgumentParser(description='Specify files to import cards from at the start and/or export cards '
                                                 'to at the exit')
    parser.add_argument('-i', '--import_from', help='File to import flashcards from at the start of program.')
    parser.add_argument('-e', '--export_to', help='File to save flashcards to at the end of program.')

    return parser.parse_args()


output = io.StringIO()  # file-like object that stores data inputted or printed to the console for
# logging purposes upon request


class Flashcard:
    """A flashcard instance stores its term, definition and error count.

    Vocabulary:
        Term: text on the "front" of the card; what the user will be questioned on
        Definition: text on the "back" of the card; wha the user will try to answer correctly
        Error count: total number of wrong guesses that have been made on a single card

    - Static dictionaries: flashcards -> dict
                        definitions -> dict
        * flashcards - stores all instances of created or imported flashcards as values; under terms as keys
        * definitions - stores all definitions as keys to prevent creation of cards with the same definition
             We used a dictionary that has definitions as keys and terms as values instead of just a set of definitions
             just to be able to inform the user if they have guessed the correct answer but to the wrong card.
    """

    flashcards = {}  # term(key): Flashcard() (value)
    definitions = {}  # definition(key): term(value)

    def __init__(self, term, definition, error_count=0):
        self.term = term
        self.definition = definition
        self.error_count = error_count  # total number of mistakes made when asked about flashcard

        Flashcard.definitions[definition] = term

    def set_term(self, term):
        self.term = term

    def set_definition(self, definition):
        self.definition = definition
        Flashcard.definitions[definition] = self.term

    def __repr__(self):
        return f"{self.term}=|={self.definition}=|={self.error_count}"


def out(msg):
    """To be used instead of print()"""
    print(msg)
    output.write(msg + '\n')


def _input():
    """To be used instead of input()"""
    string = input()
    print(string, file=output)
    return string


def add():
    """Create a flashcard

    Restrictions:
        1. Cannot create card with the same term/definition that already exists
    """

    out(f"The card:")
    while True:
        term = _input()
        if term in Flashcard.flashcards:
            out(f'The card "{term}" already exists. Try again:')
        else:
            break

    out(f"The definition of the card:")
    while True:
        definition = _input()
        if definition in Flashcard.definitions:
            out(f'The definition "{definition}" already exists. Try again:')
        else:
            break

    Flashcard.flashcards[term] = Flashcard(term, definition)
    out(f'The pair ("{term}":"{definition}") has been added.')


def remove():
    """Remove specified card. If specified card doesn't exist, inform the user."""

    out('Which card?')
    card = _input()
    try:
        definition = Flashcard.flashcards[card].definition
    except KeyError:
        out(f'Can\'t remove "{card}": there is no such card.')
    else:
        del Flashcard.flashcards[card]
        del Flashcard.definitions[definition]
        out("The card has been removed.")


def import_file(filename=None):
    """Import flashcards from specified file. If file does not exist, inform the user. For cards already exist, update
    their definitions. """

    if not filename:
        out("File name:")
        filename = _input()
    if not os.path.exists(filename):
        out("File not found.")
        return

    with open(filename, 'r') as file:
        n = 0
        for line in file:
            term, definition, error_count = line.strip().split('=|=')  # '=|=' is a separator in files that contain flashcards
            Flashcard.flashcards[term] = Flashcard(term, definition, int(error_count))
            n += 1

    out(f"{n} cards have been loaded.")


def export(filename=None):
    """Export current flashcards to specified file in special format: '=|=' is used as a separator between term,
    definition and error count."""

    if not filename:
        out("File name:")
        filename = _input()

    with open(filename, 'w') as file:
        for flashcard in Flashcard.flashcards.values():
            print(f"{flashcard.term}=|={flashcard.definition}=|={flashcard.error_count}", file=file)
    out(f"{len(Flashcard.flashcards)} cards have been saved.")


def ask():
    """Prompt user for #n number of flashcards they want to be questioned on, and ask them #n definitions for given terms

    1. In case user guesses correctly, 'Correct!' will be displayed.
    2. In case user guessed incorrectly, appropriate message and correct definition will be displayed.
    3. In case user guessed incorrectly, but the definition they provided matches some other term in available
       flashcards, user will be informed
    """

    out("How many times to ask?")
    n = int(_input())
    if n > len(Flashcard.flashcards):
        # in case n > number of flashcards: n number of cards will be questioned, but duplicates will be allowed
        flashcards = (list(Flashcard.flashcards.values()) * (n // len(Flashcard.flashcards) + 1))[0:n]
    else:
        # random sample with no duplicates
        flashcards = random.sample(list(Flashcard.flashcards.values()), n)  # must convert to list for dicts or sets

    for flashcard in flashcards:
        out(f'Print the definition of "{flashcard.term}":')
        guess = _input()
        if guess.lower() == flashcard.definition.lower():
            out("Correct!")
        else:
            if guess in Flashcard.definitions:
                out(f'Wrong. The right answer is "{flashcard.definition}", but your definition is correct for '
                    f'"{Flashcard.definitions[guess]}".')
            else:
                out(f'Wrong. The right answer is "{flashcard.definition}".')

            flashcard.error_count += 1


def log():
    """Save all contents of console to specified file.
    Contents of console are stored in the 'output' variable that is an io.StringIO object."""

    out("File name:")
    filename = input()
    content = output.getvalue().split('\n')
    with open(filename, 'w') as file:
        for line in content:
            print(line, file=file)
    out('The log has been saved')


def hardest_card():
    """Display the hardest card/cards. Hardest card is one that has the highest error count."""

    errors = [flashcard.error_count for flashcard in Flashcard.flashcards.values()]
    max_error = max(errors) if errors else 0
    if max_error == 0:
        out("There are no cards with errors.")
        return
    hardest_cards = []

    for flashcard in Flashcard.flashcards.values():
        if flashcard.error_count == max_error:
            hardest_cards.append(flashcard.term)

    if len(hardest_cards) == 1:
        out(f'The hardest card is "{hardest_cards[0]}". You have {max_error} errors answering it.')
    else:
        msg = 'The hardest cards are "' + '", "'.join(hardest_cards) + f'". You have {max_error} errors answering them.'
        out(msg)


def reset_stats():
    """Reset error count to 0 for all flashcards and inform the user."""

    for flashcard in Flashcard.flashcards.values():
        flashcard.error_count = 0
    out("Card statistics have been reset.")


def main():
    args = get_args()
    if args.import_from:
        import_file(args.import_from)

    actions = {'add': add, 'remove': remove, 'import': import_file, 'export': export, 'ask': ask, 'log': log,
               'hardest card': hardest_card, 'reset stats': reset_stats}

    while True:
        out("Input the action (add, remove, import, export, ask, exit, log, hardest card, reset stats):")
        action = _input()

        if action == 'exit':
            out('Bye bye!')
            break
        try:
            actions[action]()
        except KeyError:
            continue
        out('')

    if args.export_to:
        export(args.export_to)


if __name__ == '__main__':
    main()
