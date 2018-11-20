# from nltk.corpus import wordnet as wn
import nltk
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet as wn
import copy
noun_phrase = ['NN','NNS','NNPS','NNP']
adj_phrase = ['JJ','JJR','JJS']
periodset = set(['.','?','!'])
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


def parse_word(filename):
    f = open(filename,"r")
    w = open("input/new_small.txt","w")
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

        idx = 0
        added = 0  # flag for add wild card
        for i in range(len(words)): # find the noun that has not been marked
            # get the tag of word
            flag_idx = 0
            wt = nltk.word_tokenize(words[i])
            if(words[i]!=sen_tagged[idx][0] and len(wt)==2 and wt[1] in periodset):
                # print(words[i],sen_tagged[idx])
                flag_idx=1

            # print(sen_tagged[idx],idx,len(sen_tagged))
            if (sen_tagged[idx][1] in adj_phrase) and (i<len(words)-1 and (words[i+1][0]=='<' and len(words[i+1])>1)):
                new_line+="* "
                added = 1
            elif(words[i][0]=='<' and len(words[i])>1 and added==0):
                # print(words[i])
                new_line+="* "+words[i]+" "
            else:
                # print(words[i])
                new_line+=words[i]+" "
                added = 0


            # update idx
            idx = idx + 1 + flag_idx



        # print(new_line)
        new_line = new_line.strip(' ')
        w.write(new_line+"\n")

    w.close()
    f.close()

if __name__ == '__main__':
    parse_word("input/small.txt")
    # get_tag_path("professional")
    # print(wn.synsets("earthquake"))