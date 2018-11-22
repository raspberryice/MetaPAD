# from nltk.corpus import wordnet as wn
import nltk
# nltk.download('wordnet')
# nltk.download('averaged_perceptron_tagger')
from nltk.corpus import wordnet as wn
import copy
noun_phrase = ['NN','NNS','NNPS','NNP']
adj_phrase = ['JJ','JJR','JJS']
periodset = set(['.','?','!',','])
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
    # w = open("input/goodpattern_wildcard.txt","w")
    w = open("input/corpus_wildcard.txt", "w")
    for line in f.readlines():
        d = {}
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
        for word in sen_tagged:
            if word[0] not in d.keys():
                d[word[0]] = [word[1]]
            else:
                d[word[0]].append(word[1])
        idx = 0
        added = 0  # flag for add wild card
        for i in range(len(words)): # find the noun that has not been marked
            # get the tag of word

            tmp_word = words[i]
            label = ''
            if tmp_word[-1] in periodset:
                tmp_word = tmp_word[:-1]
            if len(tmp_word) > 1 and (tmp_word[0] == '<' or tmp_word[-1] == '>'):
                if tmp_word[0] == '<' and tmp_word[-1] == '>':
                    label = tmp_word.split('>')[0][1:]
                    tmp_word = tmp_word.split('>')[1].split('<')[0]
                elif (tmp_word[0] == '<' and tmp_word[-1] != '>'):
                    tmp_word = tmp_word.split('>')[1]
                elif (tmp_word[0] != '<' and tmp_word[-1] == '>'):
                    tmp_word = tmp_word.split('<')[0]

            # print(sen_tagged[idx],idx,len(sen_tagged))
            # print(words[i])
            # if words[i] in d.keys():
            #     print(words[i],d[words[i]],line)
            if label!='Date' and words[i] in d.keys() and d[words[i]][0] in adj_phrase and (i<len(words)-1 and (words[i+1][0]=='<' and len(words[i+1])>1 and words[i+1][1]!='/') ):
                d[words[i]] = d[words[i]][1:]
                added = 1
                new_line += "WILDCARD "
                if(len(d[words[i]])==0):
                    d.pop(words[i])
                    continue


                # new_line+=""
                # added = 1
            elif(label!='Date' and words[i][0]=='<' and len(words[i])>1 and words[i][1]!='/' and added==0):
                # print(words[i])
                new_line+="WILDCARD "+words[i]+" "
                # new_line += words[i] + " "
            else:
                # print(words[i])
                new_line+=words[i]+" "
                added = 0
                # added = 0
            # pop the tag


            if tmp_word in d.keys():
                d[tmp_word] = d[tmp_word][1:]
                if (len(d[tmp_word]) == 0):
                    d.pop(tmp_word)
                # print(words[i],d[words[i]])



        # print(new_line)
        new_line = new_line.strip(' ')
        w.write(new_line+"\n")

    w.close()
    f.close()

if __name__ == '__main__':
    # parse_word("input/goodpattern.txt")
    parse_word("input/new_corpus.txt")
    # get_tag_path("professional")
    # print(wn.synsets("earthquake"))