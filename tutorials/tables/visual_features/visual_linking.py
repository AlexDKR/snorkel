import numpy as np
from collections import OrderedDict
from editdistance import eval as editdist

def calculate_offset(listA, listB, seedSize, maxOffset):
    wordsA = zip(*listA[:seedSize])[1]
    wordsB = zip(*listB[:maxOffset])[1]
    offsets = []
    for i in range(seedSize):
        try:
            offsets.append(wordsB.index(wordsA[i]) - i)
        except:
            pass
    return int(np.median(offsets))


def link_lists(listA, listB, searchMax=100, editCost=20, offsetCost=1, offsetInertia=5):
    DEBUG = False
    if DEBUG:
        offsetHist = []
        jHist = []
        editDistHist = 0
    offset = calculate_offset(listA, listB, max(searchMax/10,5), searchMax)
    offsets = [offset] * offsetInertia
    searchOrder = np.array([(-1)**(i%2) * (i/2) for i in range(1, searchMax+1)])
    links = OrderedDict()
    for i, a in enumerate(listA):
        j = 0
        searchIndices = np.clip(offset + searchOrder, 0, len(listB)-1)
        jMax = len(searchIndices)
        matched = False
        # Search first for exact matches
        while not matched and j < jMax:
            b = listB[searchIndices[j]]
            if a[1] == b[1]:
                links[a[0]] = b[0]
                matched = True
                offsets[i % offsetInertia] = searchIndices[j]  + 1
                offset = int(np.median(offsets))
                if DEBUG:
                    jHist.append(j)
                    offsetHist.append(offset)
            j += 1
        # If necessary, search for min edit distance
        if not matched:
            cost = [0] * searchMax
            for k, m in enumerate(searchIndices):
                cost[k] = (editdist(a[1],listB[m][1]) * editCost +
                           k * offsetCost)
            links[a[0]] = listB[searchIndices[np.argmin(cost)]][0]
            if DEBUG:
                editDistHist += 1
    if DEBUG:
        print offsetHist
        print jHist
        print editDistHist
    return links