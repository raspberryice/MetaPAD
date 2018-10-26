import argparse
from utils import *

def SalientFast(file_output_salient,file_output_key,file_input_phrase,file_input_mapping):
    fw = open(file_output_key,'w')
    fr = open(file_input_mapping,'rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        key,value = arr[0],arr[1]
        if len(value) > 1 and value[0] == '$':
            fw.write(key+'\t'+value[1:]+'\t'+''+'\n')
        else:
            fw.write(key+'\t'+''+'\t'+value+'\n')
    fr.close()
    fw.close()
    fw = open(file_output_salient,'w')
    fr = open(file_input_phrase,'rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        fw.write(arr[1].replace(' ','_')+','+arr[0]+'\n')
    fr.close()
    fw.close()


def MPTable(file_output_table,file_output_metapattern,file_input_salient,file_input_key,file_input_entitylinking,file_input_goodclass,file_input_verbs,file_input_stopwords,LEVEL):
    goodclassset = SetFromFile(file_input_goodclass,False)
    verbset = SetFromFile(file_input_verbs)
    stopwordset = SetFromFile(file_input_stopwords)
    stopwordpatternset = {'and','or','say','says','said','told','announced'}
    commaset = {':','-','.',';'}
    key2value = {}
    fr = open(file_input_key,'rb')
    for line in fr:
        arr = line.strip('\r\n').split('\t')
        key,classname = arr[0],arr[1]
        value = ''
        if classname == '' or classname == 'PERIOD':
            value = arr[2]
        else:
            value = '<'+arr[1]+'>'+arr[2]+'</'+arr[1]+'>'
        key2value[key] = value
    fr.close()
    pattern2score = {}
    fr = open(file_input_salient,'rb')
    for line in fr:
        arr = line.strip('\r\n').split(',')
        pattern = ''
        for key in arr[0].split('_'):
            if key in key2value:
                pattern += ' '+key2value[key]
            else:
                pattern += ' '+key
        pattern = pattern[1:]
        if pattern == '': continue
        if 'that' in pattern or ' , and ' in pattern or ' , or ' in pattern: continue
        score = float(arr[1])
        sentence = XMLToSentence(pattern)
        n = len(sentence)
        posStart,posEnd = -1,-1
        for i in range(0,n):
            [classname,words] = sentence[i]
            if not (classname == '' and (words == ',' or words in commaset or words.lower() in stopwordset or words.lower() in stopwordpatternset)):
                posStart = i
                break
        for j in range(n-1,-1,-1):
            [classname,words] = sentence[j]
            if not (classname == '' and (words == '(' or words in commaset or words.lower() in stopwordset or words.lower() in stopwordpatternset)):
                posEnd = j
                break
        if posStart < 0 or posEnd < 0 or posStart >= posEnd:
            continue
        sentence = sentence[posStart:posEnd+1]
        n = len(sentence)
        [classname,words] = sentence[0]
        if classname == '' and IsVerb(words.lower(),verbset):
            continue
        [classname,words] = sentence[n-1]
        if classname == '' and IsVerb(words.lower(),verbset):
            continue
        mention_class_set = set()
        num_mention_context = 0
        for [classname,words] in sentence:
            rootclass = classname
            if '.' in classname:
                pos = classname.find('.')
                rootclass = classname[0:pos]
            if rootclass in goodclassset:
                mention_class_set.add(classname)
            elif not (classname == '' and (len(words) == 1 or words.lower() in stopwordset)):
                num_mention_context += 1
        num_mention_class = len(mention_class_set)
        if num_mention_class == 0: continue
        if not ((num_mention_class > 1 and num_mention_context == 0) or (num_mention_context > 0)): continue
        pattern = SentenceToXML(sentence)
        if pattern in pattern2score:
            score = max(score,pattern2score[pattern])
        pattern2score[pattern] = score
    fr.close()
    fw = open(file_output_metapattern,'w')
    for [pattern,score] in sorted(pattern2score.items(),key=lambda x:-x[1]):
        sentence = XMLToSentence(pattern)
        dollar = SentenceToDollar(sentence)
        fw.write(pattern+'\t'+str(score)+'\t'+dollar+'\n')
    fw.close()
    index = PatternIndex(file_output_metapattern)
    n_index = len(index)
    fw = open(file_output_table,'w')
    fw.write('MENTION\tXMLBOTTOM\tXML\tPATTERN\tSCORE\tPOS\n')
    mention = 0
    fr = open(file_input_entitylinking,'rb')
    for line in fr:
        xml = line.strip('\r\n')
        sentence_bottom = XMLToSentence(xml)
        if LEVEL == 'TOP':
            sentence = [] # TOP - begin
            for [classname,words] in sentence_bottom:
                if '.' in classname:
                    pos = classname.find('.')
                    rootclass = classname[0:pos]
                    sentence.append([rootclass,words])
                else:
                    sentence.append([classname,words]) # TOP - end
        else:
            sentence = sentence_bottom # BOTTOM
        keys = SentenceToKeys(sentence)
        n = len(sentence)
        for i in range(0,n):
            [classname,words] = sentence[i]
            rootclass = classname
            if '.' in classname:
                pos = classname.find('.')
                rootclass = classname[0:pos]
            if not rootclass in goodclassset: continue
            mention += 1
            entity = ''
            for word in words: entity += ' '+word
            entity = entity[1:]
            last_end = -1
            for p in range(max(0,i-n_index+1),i+1):
                max_score,max_s,max_end = 0,'',-1
                for j in range(min(n_index,n-i),max(1,i-p),-1):
                    temp = index[j-1]
                    k = 0
                    while k < j:
                        key = keys[p+k]
                        if not key in temp:
                            break
                        temp = temp[key]
                        k += 1
                    if k == j:
                        [pattern,score] = temp
                        if score < max_score: continue
                        max_score = score
                        xml_bottom = SentenceToXML(sentence_bottom[p:p+j])
                        xml = SentenceToXML(sentence[p:p+j])
                        s = str(mention)+'\t'+xml_bottom+'\t'+xml+'\t'+pattern+'\t'+str(score)+'\t'+str(i-p)
                        max_s = s
                        max_end = p+j
                if max_score > 0 and max_end > last_end:
                    last_end = max_end
                    fw.write(max_s+'\n')
    fr.close()
    fw.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--good-pattern-file', type=str, default='input/goodpattern.txt')
    parser.add_argument('--verb-file', type=str, default='input/verbs.txt')
    parser.add_argument('--good-class-file', type=str, default='input/goodclass.txt')
    parser.add_argument('--corpus-file', type=str, default='input/corpus.txt')
    parser.add_argument('--stop-words', type=str, default='input/stopwords.txt')
    parser.add_argument('--level', type=str, default='TOP')

    args = parser.parse_args()


    # python metapad.py salientFast
    # output/top-salient.csv output/top-key.txt output/top-token-phrase.txt output/top-token-mapping.txt
    # python metapad.py mptable
    # output/top-table.txt output/top-metapattern.txt output/top-salient.csv output/top-key.txt
    # data/corpus.txt data/goodclass.txt data/verbs.txt data/stopwords.txt TOP

    SalientFast('output/top-salient.txt','output/top-key.txt','output/top-token-phrase.txt','output/top-token-mapping.txt',
                )

    MPTable('output/top-table.txt','output/top-metapattern.txt','output/top-salient.csv','output/top-key.txt',
            args.corpus_file, args.good_class_file, args.verb_file, args.stop_words, args.level)

