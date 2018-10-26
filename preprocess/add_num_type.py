
import argparse
import re
import os
import spacy
from tqdm import tqdm

DATE_PATTERN = r'([0-9X]{4}(?:-[0-9X]{2}?)(?:-[0-9X]{2})?)(?:-W[0-9X]{2})?(?:-[0-9])?(?:T(?:MO|NI|EV|AF)?[0-9]{2}:[0-9]{2})?(:?:[0-9]{2})?'

REG_DATE = re.compile(DATE_PATTERN)


NUM_PATTERN = r'(?<!>)([+-]?\.?\d+(?:,\d+)*(?:\.\d+)?)'

DURATION_PATTERN = r'(?<!>)[><~]?P(?:T)?(\d+[HSDYM])' #Hour, second, day, year, month
def replace_line(line):
    shift = 0
    dates = []
    for item in re.finditer(DATE_PATTERN, line):
        # print(item.group(1))  # match object, normalize to date only
        index_start = item.span()[0] + shift
        index_end = item.span()[1] + shift
        new_text = '<Date>'  + '</Date>'  #omit real date to avoid duplicate matching
        dates.append(item.group(1))
        line = line[0:index_start] + new_text + line[index_end:]
        shift += len('<Date></Date>') - len(item.group(0))

    shift =0
    durations = []
    for item in re.finditer(DURATION_PATTERN, line):
        # print(item.group(1))
        index_start = item.span()[0] + shift
        index_end = item.span()[1] + shift
        new_text = '<Duration>' + '</Duration>'  # omit real date to avoid duplicate matching
        durations.append(item.group(1))
        line = line[0:index_start] + new_text + line[index_end:]
        shift += len('<Duration></Duration>') - len(item.group(0))

    shift =0
    for item in re.finditer(NUM_PATTERN, line):
        # print(item.group(1))
        index_start = item.span()[0] + shift
        index_end = item.span()[1] + shift
        new_text = '<Number>' + item.group(1) + '</Number>'
        line = line[0:index_start] + new_text + line[index_end:]
        shift += len('<Number></Number>')

    # put date back
    shift = 0
    for idx,item in enumerate(re.finditer(r'<Date></Date>',line)):
        index_start = item.span()[0] + shift
        index_end = item.span()[1] + shift
        new_text = '<Date>' + dates[idx] + '</Date>'  # omit real date to avoid duplicate matching
        line = line[0:index_start] + new_text + line[index_end:]
        shift += len(dates[idx])

    # put duration back
    shift =0
    for idx, item in enumerate(re.finditer(r'<Duration></Duration>',line)):
        index_start = item.span()[0] + shift
        index_end = item.span()[1] + shift
        new_text = '<Duration>' + durations[idx] + '</Duration>'  # omit real date to avoid duplicate matching
        line = line[0:index_start] + new_text + line[index_end:]
        shift += len(durations[idx])



    return line


def add_type(file,outfile):
    with open(file) as f, open(outfile, 'w') as fo:
        input = f.read()
        toks = input.split()
        annotated = []
        in_entity = False
        for tok in toks:
            if not in_entity:
                m = re.match(TAG_RE, tok)
                if m:
                    annotated.append((m.group(2), m.group('tag')))
                else:
                    if re.match(OPEN_TAG_RE, tok):
                        in_entity= True
                        tag = re.match(OPEN_TAG_RE, tok).group('tag')
                        entity_text = re.match(OPEN_TAG_RE, tok).group(2)
                        continue

                    if re.match(REG_DATE, tok):
                        annotated.append((re.match(REG_DATE, tok).group(1), 'Date'))
                    elif re.match(DURATION_PATTERN, tok):
                        annotated.append((re.match(DURATION_PATTERN, tok).group(1), 'Duration'))
                    elif re.match(NUM_PATTERN, tok):
                        annotated.append((re.match(NUM_PATTERN, tok).group(1), 'Number'))
                    else:
                        annotated.append((tok, ''))
            else:
                # in entity
                if re.match(CLOSE_TAG_RE, tok):
                    if re.match(CLOSE_TAG_RE, tok).group('tag') == tag:
                        entity_text += ' '+re.match(CLOSE_TAG_RE, tok).group(1)
                        annotated.append((entity_text, tag))
                        in_entity = False
                    else:
                        entity_text += ' '+re.match(CLOSE_TAG_RE, tok).group(1)

                else:
                    entity_text += ' '+tok


        text = ' '.join([x[0] for x in annotated])
        a_len = [len(x[0].split()) for x in annotated]


        # tokenize
        doc = nlp(text)
        shift = 0
        last_idx =0
        for sent in doc.sents:
            sent_len = len(sent.text.strip('\n').split())
            toks_new = []
            # find index corresponding to shift + sent_len token
            cum_l =0
            for idx,l in enumerate(a_len):
                cum_l+=l
                if cum_l >= shift+sent_len:
                    end_idx = idx+1
                    break

            toks = annotated[last_idx:end_idx]
            for tok in toks:
                if tok[1] != '':
                    text = '<{}>{}</{}>'.format(tok[1], tok[0], tok[1])
                    toks_new.append(text)
                else:
                    toks_new.append(tok[0])

            fo.write(' '.join(toks_new) + '\n')
            shift += sent_len
            last_idx = end_idx

    return

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--indir',type=str)
    parser.add_argument('--outdir',type=str)
    args = parser.parse_args()


    # m = re.search(DATE_PATTERN,'2008-05-W20')
    # print(m.group(1)) #date
    #
    # m = re.search(DATE_PATTERN,'2008-05-12TEV00:00:00')
    # print(m.groups())
    # #
    # m = re.search(NUM_PATTERN,'nearly 10 million')
    # print(m.groups())

    # m = re.search(DURATION_PATTERN,'have spent >P10Y rebuilding <Number>26</Number> elementary schools in Sichuan')
    # print(m.group(1))
    #
    # line = '''She said it could take ><Aircraft>3Y</Aircraft> to bring the region back.'''
    # print(replace_line(line))

    TAG_RE = re.compile(r'<(?P<tag>[\w\.]+)>(.+)</(?P=tag)>')
    OPEN_TAG_RE = re.compile(r'<(?P<tag>[\w\.]+)>(.+)')
    CLOSE_TAG_RE = re.compile(r'(.+)</(?P<tag>[\w\.]+)>')
    file_re = r'\d+_\d+_\d+_new.txt'
    nlp = spacy.load('en_core_web_lg',disable=['ner',])
    os.makedirs(args.outdir,exist_ok=True)

    for filename in tqdm(os.listdir(args.indir)):
        if re.match(file_re,filename):
            file= os.path.join(args.indir, filename)
            outfile = os.path.join(args.outdir, os.path.splitext(filename)[0]+'.update.txt')
            add_type(file,outfile)
    # add_type('./0_0_0_new.txt','./0_0_0_update.txt')
