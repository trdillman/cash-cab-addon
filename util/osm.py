def assignTags(obj, tags):
    for key in tags:
        obj[key] = tags[key]


def parseNumber(s, defaultValue=None):
    s = s.rstrip()
    if s[-1] == 'm':
        s = s[:-1]
    try:
        n = float(s)
    except ValueError:
        n = defaultValue
    return n
