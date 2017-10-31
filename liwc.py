"""
Class and functions to organize polarity data from a LIWC dictionary.
"""


class LIWC:
    """
    LIWC dictionary and data class.
    """

    def __init__(self, filename, remove_asterisk=True):
        """Construct LIWC object and initilize the sentiment word dictionary."""

        self.file = open(filename, 'r', encoding='latin-1')
        self.data = self.file.readlines()
        self.dict = dict()

        # Iterate across the LIWC data
        for line in self.data:
            line_words = line.rstrip('\r\n').split()
            word = line_words[0]
            categories = line_words[1:]

            # Remove asterisk notation from word if required
            if remove_asterisk and word[-1] == '*':
                word = word[:-1]

            # Add word to it's corresponding emotion set
            if '126' in categories:
                # Store word as positive emotion
                self.dict[word] = +1

            elif '127' in categories:
                # Store word as an negative emotion
                self.dict[word] = -1

    def get_sentiment(self, word):
        """
        Search a given word on the LIWC dictionary and return the polarity
        associated to it ('-1'/'+1'), otherwise return None.
        """

        # List of word derivations to search for on dictionary
        word_derivations = [word]

        # Add to the list derivations of 'word' removing it's last letters
        if len(word) > 2:
            word_derivations.append(word[:-1])
        if len(word) > 3:
            word_derivations.append(word[:-2])

        # Query the word derivations
        for term in word_derivations:
            polarity = self.dict.get(term)

            # Polarity found (-1 or +1)
            if polarity is not None:
                return(polarity)

        # No polarity value found on the dictionary
        return(None)
