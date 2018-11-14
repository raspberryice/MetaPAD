# from nltk.corpus import wordnet as wn
import nltk
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet as wn
import copy
noun_phrase = ['NN','NNS','NNPS','NNP']

top_level_types = {
    'person.n.01': 'person',
    'organization.n.01': 'organization',
    'location.n.01':'location',
    'structure.n.01': 'structure',# house
    'facility.n.01':'facility', # airport
    'artifact.n.01':'artifact',#artifact is actually parent of facility & structure road 
    'phenomenon.n.01':'event', #hurricane and earthquake 
    'event.n.01':'event',#landslide and tsunami 
    #'process.n.06':'process', #decline, increase 
}

def get_top_level_type(t1):
    '''
    t1 is the head word of a noun phrase. Multiple types are allowed in case of ambiguity.
    '''
    
    if t1 in {'datetime','numeric','person','organization','location'}:
        return {t1}

    t = set()
    ss_list = wn.synsets(t1,pos=wn.NOUN)[:3]   # find all the wordset that the word is in（synsets）
    # print(ss_list)
    while ss_list:
        s = ss_list.pop(0)
        hyp = s.hypernyms()   # get all the nearest upper tag set
        # print(hyp)
        if not hyp:
            break 
        elif (hyp[0]._name in top_level_types): # the nearest top
            # print(top_level_types[hyp[0]._name])
            t.add(top_level_types[hyp[0]._name])
        elif hyp[0] == wn.synset('entity.n.01'):  # no other upper tag set
            break
        else:
            ss_list.extend(hyp)
    return t

# get the second tag that beyond the current tag of word
def get_tag_path(t1):
    '''
       t1 is the head word of a noun phrase. Multiple types are allowed in case of ambiguity.
       '''
    t = []
    tag_list = wn.synsets(t1,pos=wn.NOUN)[:1]
    if tag_list:
        s = tag_list.pop(0)  # get the first tag
        hyp = s.hypernyms()
        while hyp:

            if not hyp:
                break
            elif hyp[0] == wn.synset('entity.n.01'):
                break
            elif hyp[0]._name in top_level_types:
                t.append(hyp[0].lemma_names()[0].capitalize())
                return t
            else:
                t.append(hyp[0].lemma_names()[0].capitalize())
                hyp = hyp[0].hypernyms()

    t.clear()
    return t

# correct the form of tag
def check_tag(str):
    tags = str.split('.')
    res = []
    # print(tags)
    for tag in tags:
        if tag.lower() in top_level_types.values():
            res.clear()
            res.append(tag.capitalize())
        elif tag.lower()=='organisation':
            res.clear()
            res.append("Organization")
        elif tag.lower() == 'place':
            res.clear()
            res.append('Location')
        else:
            res.append(tag.capitalize())
    s = ''
    for r in res:
        s+=r+"."
    s = s.strip('.')
    return s


def parse_word(filename):
    f = open(filename,"r")
    w = open("input/new_corpus.txt","w")
    for line in f.readlines():
        new_line = ''
        words = line.strip('\r\n').split()

        # get tag
        tmp = copy.deepcopy(words)
        tagged_word = []
        tmp_flag = 1
        for i in range(len(tmp)):
            if(tmp[i][0]=='<' and tmp[i][-1]=='>'):
                tmp[i] = tmp[i].split('>')[1].split('<')[0]
                tagged_word.append(0)
            elif tmp[i][0] == '<':
                if len(tmp[i].split('>'))>1:
                    tmp[i] = tmp[i].split('>')[1]
                    tmp_flag = 0
                tagged_word.append(tmp_flag)

            elif tmp[i][-1] == '>':
                tmp[i] = tmp[i].split('<')[0]
                tagged_word.append(tmp_flag)
                tmp_flag = 1
            else:
                tagged_word.append(tmp_flag)
        sen = ''
        for t in tmp:
            sen+=t+' '
        sen = sen.strip()
        text = nltk.word_tokenize(sen)
        sen_tagged = nltk.pos_tag(text)

        for i in range(len(words)): # find the noun that has not been marked
            # get the tag of word
            flag = ''  # get the tag of word
            wt = nltk.word_tokenize(words[i])
            tmp_word = wt[0]  # remove . , : and other
            punctuation = ''
            if len(wt)>1:
                punctuation = wt[1]
            for t in sen_tagged:
                if tmp_word == t[0]:
                    flag = t[1]

            # already tagged
            if words[i][0]=='<' or words[i][-1]=='>': # already marked
                if words[i][0]=='<' and words[i][-1] == '>':

                    check1 = words[i].split('>')[0].strip('<')
                    tag1 = check_tag(check1)
                    # print(check1,tag1)
                    new_line+='<'+tag1+'>'+words[i].split('>')[1].split('<')[0]+'</'+tag1+'>'+" "
                elif words[i][0] == '<': # first tag
                    check = words[i].split('>')
                    if len(check)>1:
                        new_tag = '<'+check_tag(words[i].split('>')[0].strip('<'))+ '>'
                        new_line+=new_tag + words[i].split('>')[1]+" "
                elif words[i][-1] == '>' and len(words[i].split('<'))>1:
                    check = words[i].split('<')[1]
                    check = check.strip('/').strip('>')
                    new_tag = '</'+check_tag(check)+'>'
                    new_line += words[i].split('<')[0]+new_tag + " "
                else:
                    new_line += words[i] + " "
                continue


            # do not need to tag or the word is inside a tagged phase
            elif flag not in noun_phrase or tagged_word[i]==0:
                new_line += words[i] + " "
                continue

            # get new tag
            top = get_tag_path(tmp_word)
            if len(top)>0:
                tag_string = ''
                for top_tag in reversed(top):
                    tag_string+=top_tag+'.'
                tag_string = tag_string.strip('.')

                new_word = "<"+tag_string+">"+tmp_word+"</"+tag_string+">"+punctuation
                words[i] = new_word # replace the original word with tagged word
            new_line+=words[i]+" "
        print(new_line)
        new_line = new_line.strip(' ')
        w.write(new_line+"\n")

    w.close()
    f.close()



if __name__ == '__main__':
    parse_word("input/1_corpus.txt")
    # get_tag_path("professional")
    # print(wn.synsets("earthquake"))