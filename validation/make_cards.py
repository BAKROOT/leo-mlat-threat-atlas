"""Build the blind rating cards for the expert validation: the layer prompts of the model panel (llm_panel/prompts/B1-B4)
restricted to the threats of validation/sample.csv. Preamble, rubric and output format are unchanged; only the records
(and the counts that refer to them) differ. Usage: python validation/make_cards.py   -> validation/cards/B?_L?_sample.txt"""
import csv, re, os
ids = [r['ID'] for r in csv.DictReader(open('validation/sample.csv'))]
os.makedirs('validation/cards', exist_ok=True)
for fn in sorted(os.listdir('llm_panel/prompts')):
    if not re.match(r'B\d_L\d\.txt', fn): continue
    t = open('llm_panel/prompts/' + fn, encoding='utf-8').read()
    head, rest = t.split('THREAT RECORDS (', 1)
    nold = int(re.match(r'(\d+)\)', rest).group(1))
    body = rest.split('\n', 1)[1]
    body, tail = body.rsplit('\nNow produce', 1)
    recs = re.split(r'\n(?=\[T\d\.\d\d\] )', '\n' + body.strip('\n'))
    recs = [r.strip('\n') for r in recs if r.strip()]
    keep = [r for r in recs if r[1:6] in ids]
    n = len(keep)
    if n == 0: continue
    head = re.sub(r'\(%d threats: T\d\.\d\d to T\d\.\d\d\)' % nold, '(%d sampled threats)' % n, head)
    head = head.replace('Below are %d threat records' % nold, 'Below are %d threat records' % n)
    head = head.replace('(%d objects)' % nold, '(%d objects)' % n)
    out = head + 'THREAT RECORDS (%d)\n\n' % n + '\n\n'.join(keep) + '\n\nNow produce the JSON object with %d ratings.\n' % n
    open('validation/cards/' + fn.replace('.txt', '_sample.txt'), 'w', encoding='utf-8').write(out)
    print(fn, nold, '->', n, [r[1:6] for r in keep])
