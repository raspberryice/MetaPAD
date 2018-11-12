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
                t.append(hyp[0].lemma_names()[0])
                # print(hyp[0]._name,t)
                return t
            else:
                t.append(hyp[0].lemma_names()[0])
                hyp = hyp[0].hypernyms()
    # print("dd",t)
    t.clear()  # not the noun that we want to consider
    return t



def parse_word(filename):
    f = open(filename,"r")
    w = open("input/new_corpus.txt","w")
    for line in f.readlines():
        new_line = ''
        words = line.strip('\r\n').split()

        # get tag
        tmp = copy.deepcopy(words)
        for i in range(len(tmp)):
            if tmp[i][0] == '<':
                if len(tmp[i].split('>'))>1:
                 tmp[i] = tmp[i].split('>')[1]
            if tmp[i][-1] == '>':
                tmp[i] = tmp[i].split('<')[0]
        sen = ''
        for t in tmp:
            sen+=t+' '
        sen.strip()
        text = nltk.word_tokenize(sen)
        sen_tagged = nltk.pos_tag(text)
        # print(sen_tagged)

        for i in range(len(words)): # find the noun that has not been marked
            if words[i][0]=='<' or words[i][-1]=='>': # already marked
                new_line += words[i] + " "
                continue
            if sen_tagged[i][1] not in noun_phrase:
                new_line += words[i] + " "
                continue
            top = get_tag_path(words[i])
            if len(top)>0:
                tag_string = ''
                for top_tag in reversed(top):
                    tag_string+=top_tag+'.'
                tag_string = tag_string.strip('.')
                new_word = "<"+tag_string+">"+words[i]+"</"+tag_string+">"
                words[i] = new_word # replace the original word with tagged word
                # print(new_word)
            new_line+=words[i]+" "
        new_line.strip(' ')
        w.write(new_line+"\n")

    w.close()
    f.close()




if __name__ == '__main__':
    parse_word("input/1_corpus.txt")
    # get_tag_path("professional")
    # print(wn.synsets("professional"))