"""Function to read original/corrected pairs from m2 files.

Adapted from the BEA 2019 corr_from_m2.py script.
"""


def read_pairs(filename, coder_id=0):
    """Extract pairs of original/corrected from a given coder.

    Args:
        filename -- m2 format file as used in the BEA 2019 shared task
        coder_id -- ID of the annotator to rely on (default 0)

    Returns:
        list of (original sentence, corrected sentence)
        where both items of the tuple are lists of str tokens
    """
    m2 = open(filename).read().strip().split("\n\n")

    skip = {"noop", "UNK", "Um"}

    result = []
    for sent in m2:
        sent = sent.split("\n")
        cor_sent = sent[0].split()[1:]  # Ignore "S "
        original_sent = cor_sent.copy()
        edits = sent[1:]
        offset = 0
        for edit in edits:
            edit = edit.split("|||")
            if edit[1] in skip:
                continue  # Ignore certain edits
            coder = int(edit[-1])
            if coder != coder_id:
                continue  # Ignore other coders
            span = edit[0].split()[1:]  # Ignore "A "
            start = int(span[0])
            end = int(span[1])
            cor = edit[2].split()
            cor_sent[start+offset:end+offset] = cor
            offset = offset-(end-start)+len(cor)
        result.append((original_sent, cor_sent))

    return result
