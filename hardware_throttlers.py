from snorkel.lf_helpers import *
from collections import namedtuple

throttlers = {}

def get_part_throttler_wrapper():
    """get a part throttler wrapper to throttler unary candidates with the usual binary throttler"""
    def part_throttler_wrapper(part):
        return part_throttler((part[0], None))
    return part_throttler_wrapper

def get_part_throttler():
    return part_throttler

def part_throttler((part, attr)):
    """throttle parts that are in tables of device/replacement parts"""
    aligned_ngrams = set(get_aligned_ngrams(part))
    if (overlap(['replacement'], aligned_ngrams) or
        (len(aligned_ngrams) > 25 and 'device' in aligned_ngrams) or
        # CentralSemiconductorCorp_2N4013.pdf:
        get_prev_sibling_tags(part).count('p') > 25 or
        overlap(['complementary', 'complement', 'empfohlene'], 
                chain.from_iterable([
                    get_left_ngrams(part, window=10),
                    get_aligned_ngrams(part)]))):
        return False
    else:
        return True

throttlers['part'] = part_throttler

# FakeCandidate = namedtuple('FakeCandidate', ['part', 'attr'])
ce_keywords = set(['collector emitter', 'collector-emitter', 'collector - emitter'])
ce_abbrevs = set(['ceo', 'vceo'])
def ce_v_max_throttler((part, attr)):
    # c = FakeCandidate(part, attr)
    return (part_throttler((part, attr)) and
            overlap(ce_keywords.union(ce_abbrevs), get_row_ngrams(attr, spread=[0,3], n_max=3)))

throttlers['ce_v_max'] = ce_v_max_throttler

def get_throttler(attr):
    for a in ['ce_v_max']:
        if attr.startswith(a):
            return throttlers[a]
    return throttlers['part']