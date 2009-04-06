# Parse FASTA file

class BlastResult(object):
    def __init__(self,
                 version,  # "BLASTP 2.0.11 [Jan-20-2000]"
                 database_sequences,  # number of sequences in the database
                 database_letters,    # number of letters in the database
                 descriptions):       # list of BlastDescriptions
        self.version = version
        self.database_sequences = database_sequences
        self.database_letters = database_letters
        self.descriptions = descriptions

class BlastDescription(object):
    def __init__(self,
                 title,  # Title of the hit
                 score,  # Number of bits (int)
                 e):     # E-value (float)
        self.title = title
        self.score = score
        self.e = e


def parse_blastp(blast_file):

    line = blast_file.readline()

    # Sanity check that this is a BLASTP output text file
    if not line.startswith("BLASTP"):
        raise TypeError("Not a BLASTP file: %r" % version)

    # Remove the trailing newline
    version = line.rstrip()

    # Skip to the "Database: " line
    while 1:
        line = blast_file.readline()
        if line.startswith("Database: "):
            break
        # Sanity check that we haven't gone too far
        if not line or line.startswith("Searching..."):
            raise TypeError("Could not find the 'Database: ' line")

    # The next line contains the sequence and total letter counts, like this
    # "      72,615 sequences; 26,335,942 total letters"
    counts_line = blast_file.readline().strip()

    # Convert the two number fields into Python integers
    words = counts_line.split()
    num_sequences = int(words[0].replace(",", ""))
    num_letters = int(words[2].replace(",", ""))

    # The start of the description lines looks like
    # (though I deleted a few characters per line to make it fit nicely)
#
#                                                            Score     E
# Sequences producing significant alignments:                (bits)  Value
# 
# P07155;P27109;P27428 HIGH MOBILITY GROUP PROTEIN HMG1 (...   326  2e-89
# P09429 HIGH MOBILITY GROUP PROTEIN HMG1 (HMG-1).             326  2e-89
    #
    # The summaries start two lines after the line that starts with
    # "Sequences producing significant alignments:"

    # Skip lines to the "Sequences producing significant alignments:" line
    while 1:
        line = blast_file.readline()
        if line.startswith("Sequences producing significant alignments:"):
            break
        if not line:
            # End of file - this should not happen
            raise TypeError("Could not find the description section")

    # Read the blank line after the header for the description line
    line = blast_file.readline()
    if line.strip() != "":
        # Double check that it's a blank line
        raise TypeError("Expected a blank line after the description header")

    # Start of the description lines
    descriptions = []
    while 1:
        line = blast_file.readline()
        if not line:
            # End of file - this should not happen
            raise TypeError("Found end of file when reading summaries")
        line = line.rstrip()
        if line == "":
            # End of the summaries
            break

        # I have a description line.  Break it up into parts
        title = line[:67].strip()
        fields = line[67:].split()
        bits = int(fields[0])
        expect = float(fields[1])

        description = BlastDescription(title, bits, expect)
        descriptions.append(description)

    return BlastResult(version, num_sequences, num_letters, descriptions)

# self-test code

def test():
    blast_file = open("blastp.txt")
    result = parse_blastp(blast_file)
    if result.version != "BLASTP 2.0.11 [Jan-20-2000]":
        raise AssertionError(result.version)
    if result.database_sequences != 72615:
        raise AssertionError(result.database_sequences)
    if result.database_letters != 26335942:
        raise AssertionError(result.database_letters)
    if len(result.descriptions) != 125:
        raise AssertionError(len(result.descriptions))

    expected = (
        BlastDescription(
        "P07155;P27109;P27428 HIGH MOBILITY GROUP PROTEIN HMG1 (HMG-1) (...",
         326, 2e-89),
        BlastDescription(
        "P09429 HIGH MOBILITY GROUP PROTEIN HMG1 (HMG-1).",
        326, 2e-89),
        BlastDescription(
        "P10103 HIGH MOBILITY GROUP PROTEIN HMG1 (HMG-1).",
        326, 2e-89),
        BlastDescription(
        "P12682 HIGH MOBILITY GROUP PROTEIN HMG1 (HMG-1).",
        324, 9e-89),
        BlastDescription(
        "P26583 HIGH MOBILITY GROUP PROTEIN HMG2 (HMG-2).",
        284, 1e-76),
        )

    # Compare the expected value to the parsed value
    for i in range(len(expected)):
        expect = expected[i]
        description = result.descriptions[i]
        if expect.title != description.title:
            raise AssertionError((expect.title, description.title))
        if expect.score != description.score:
            raise AssertionError((expect.score, description.score))
        if expect.e != description.e:
            raise AssertionError((expect.e, description.e))

if __name__ == "__main__":
    test()
    print "All tests passed."
