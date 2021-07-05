import sys
import operator

text = '';
for line in sys.stdin:
    text += line;

words = text.split();
count = dict();

for w in words:
    if not w.isalpha(): continue;
    if w in count:
        count[w] += 1;
    else:
        count[w] = 1;

for w in sorted(count.items(), key=operator.itemgetter(1)):
    print(w);
