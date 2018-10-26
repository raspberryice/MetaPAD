import argparse
from utils import *




def Synonym(file_output_synonym,file_input_table,file_input_goodclass,file_input_verbs,file_input_stopwords):
    goodclassset = SetFromFile(file_input_goodclass,False)
    verbset = SetFromFile(file_input_verbs)
    stopwordset = SetFromFile(file_input_stopwords)
    patterns = []
    pattern2patternid = {}
    str_goodclass2patternidset = {}
    goodclass_entity2patternidset = {}
    invalidpatternset = set()
    fr = open(file_input_table,'rb')
    fr.readline()
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        pattern = arr[3]
        if pattern in invalidpatternset: continue
        if not pattern in pattern2patternid:
            patternid = len(patterns)
            sentence = XMLToSentence(pattern)
            n = len(sentence)
            pos_goodclass,pos_otherclass = [],[]
            for pos in range(0,n):
                [classname,words] = sentence[pos]
                if classname == '' or classname == 'PERIOD': continue
                rootclass = classname
                if '.' in classname:
                    _pos = classname.find('.')
                    rootclass = classname[0:_pos]
                if rootclass in goodclassset:
                    pos_goodclass.append([pos,classname])
                else:
                    pos_otherclass.append(pos)
            if len(pos_goodclass)+len(pos_otherclass) < 2:
                invalidpatternset.add(pattern)
                continue
            str_goodclass = ''
            for [pos,classname] in sorted(pos_goodclass,key=lambda x:x[1]):
                str_goodclass += '\t'+classname
            str_goodclass = str_goodclass[1:]
            patterns.append([pattern,0,pos_goodclass,pos_otherclass,str_goodclass,{}])
            if not str_goodclass in str_goodclass2patternidset:
                str_goodclass2patternidset[str_goodclass] = set()
            str_goodclass2patternidset[str_goodclass].add(patternid)
            pattern2patternid[pattern] = patternid
        patternid = pattern2patternid[pattern]
        patterns[patternid][1] += 1
        xml = arr[2]
        sentence = XMLToSentence(xml)
        n = len(sentence)
        pos_goodclass = patterns[patternid][2]
        pos_otherclass = patterns[patternid][3]
        entities = ['' for i in range(0,n)]
        for [pos,classname] in pos_goodclass:
            words = sentence[pos][1]
            entity = ''
            for word in words:
                entity += ' '+word
            entity = entity[1:]
            entities[pos] = entity
        for pos in pos_otherclass:
            [classname,words] = sentence[pos]
            entity = ''
            for word in words:
                entity += ' '+word
            entity = entity[1:]
            entities[pos] = entity
        n_goodclass = len(pos_goodclass)
        for i in range(0,n_goodclass):
            [pos,classname] = pos_goodclass[i]
            goodclass_entity = classname+'\t'+entities[pos]
            values = []
            for j in range(0,n_goodclass):
                if i == j: continue
                pos = pos_goodclass[j][0]
                values.append(entities[pos])
            for pos in pos_otherclass:
                values.append(entities[pos])
            instance = ''
            for value in sorted(values):
                instance += '\t'+value
            instance = instance[1:]
            if not goodclass_entity in patterns[patternid][5]:
                patterns[patternid][5][goodclass_entity] = set()
            patterns[patternid][5][goodclass_entity].add(instance)
            if not goodclass_entity in goodclass_entity2patternidset:
                goodclass_entity2patternidset[goodclass_entity] = set()
            goodclass_entity2patternidset[goodclass_entity].add(patternid)
    fr.close()
    fw = open(file_output_synonym,'w')
    for [pattern,count,pos_goodclass,pos_otherclass,str_goodclass,goodclass_entity2instanceset] in sorted(patterns,key=lambda x:-x[1]):
        otherpattern2scores = {}
        for patternid in str_goodclass2patternidset[str_goodclass]:
            otherpattern = patterns[patternid][0]
            othergoodclass_entity2instanceset = patterns[patternid][5]
            if otherpattern == pattern: continue
            otherpattern2scores[otherpattern] = [0.0,0.0]
            sum_n1,sum_n2,sum_n3 = 0,0,0
            for goodclass_entity in goodclass_entity2instanceset:
                if not goodclass_entity in othergoodclass_entity2instanceset: continue
                instanceset = goodclass_entity2instanceset[goodclass_entity]
                otherinstanceset = othergoodclass_entity2instanceset[goodclass_entity]
                n1,n2,n3 = len(instanceset),len(otherinstanceset),len(instanceset & otherinstanceset)
                sum_n1 += n1
                sum_n2 += n2
                sum_n3 += n3
            if not sum_n3 == 0:
                otherpattern2scores[otherpattern][0] = 1.0*sum_n3/sum_n1
                otherpattern2scores[otherpattern][1] = 1.0*sum_n3/sum_n2
        for [otherpattern,[score,recall]] in sorted(otherpattern2scores.items(),key=lambda x:-x[1][0]):
            if score == 0: break
            fw.write(pattern+'\t'+otherpattern+'\t'+str(score)+'\t'+str(recall)+'\n')
    goodclass_attributename2patterns = {}
    for pattern in invalidpatternset:
        sentence = XMLToSentence(pattern)
        goodclass = ''
        attributes = []
        for [classname,words] in sentence:
            if classname == '' or classname == 'PERIOD':
                word = words.lower()
                if not (len(word) == 1 or word in stopwordset or IsVerb(word,verbset)):
                    attributes.append(word)
            else:
                rootclass = classname
                if '.' in classname:
                    _pos = classname.find('.')
                    rootclass = classname[0:_pos]
                if rootclass in goodclassset: goodclass = classname
        if goodclass == '' or len(attributes) == 0: continue
        attributename = ''
        for attribute in attributes: attributename += '\t'+attribute
        goodclass_attributename = goodclass+'\t'+attributename[1:]
        if not goodclass_attributename in goodclass_attributename2patterns:
            goodclass_attributename2patterns[goodclass_attributename] = []
        goodclass_attributename2patterns[goodclass_attributename].append(pattern)
    for [goodclass_attributename,patterns] in goodclass_attributename2patterns.items():
        n = len(patterns)
        if n < 2: continue
        for i in range(0,n):
            for j in range(0,n):
                if i == j: continue
                fw.write(patterns[i]+'\t'+patterns[j]+'\t-1\t-1\n')
    fw.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--good-pattern-file', type=str, default='input/goodpattern.txt')
    parser.add_argument('--verb-file',type=str,default='input/verbs.txt')
    parser.add_argument('--good-class-file',type=str,default='input/goodclass.txt')
    parser.add_argument('--corpus-file', type=str, default='input/corpus.txt')
    parser.add_argument('--stop-words', type=str, default='input/stopwords.txt')
    parser.add_argument('--level', type=str, default='TOP')

    args = parser.parse_args()

    # python metapad.py synonym
    # output/top-synonym.txt output/top-table.txt
    # data/goodclass.txt data/verbs.txt data/stopwords.txt

    Synonym('output/top-synonym.txt','output/top-table.txt',args.good_class_file,args.verb_file, args.stop_words)

