import argparse
from utils import *
from tqdm import tqdm
from random import randint

'''
Encoding the input file to use for segmentation.
'''
def Encrypt(file_output_encrypted,file_output_label,file_output_positive,file_output_key,file_input_entitylinking,file_input_goodpattern,file_input_stopwords,NEGATIVE,LEVEL):
    stopwordset = SetFromFile(file_input_stopwords)
    key2value = {}
    value_int = 1000000
    fw = open(file_output_encrypted,'w')
    fr = open(file_input_entitylinking,'rb')
    for lidx,line in tqdm(enumerate(fr)):
        xml = line.strip('\r\n')
        if xml == '':
            continue
        sentence = XMLToSentence(xml) # get class tag and word
        n = len(sentence)
        try:
            if sentence[n - 1][0] == 'PERIOD':
                sentence = sentence[0:n - 1]
        except IndexError:
            print(lidx)

        text = ''
        for [classname,words] in sentence:
            if classname == '':
                try:
                    assert(type(words)==str)
                except AssertionError:
                    print(line)
                    continue
                word = words
                if word.lower() in stopwordset:
                    text += ' '+word
                else:
                    key = '\t'+word
                    if not key in key2value:
                        value = ''
                        for c in str(value_int):
                            value += chr(ord('a')+int(c))  # encrypted
                        key2value[key] = value
                        value_int += 1
                    text += ' '+key2value[key]
            else:
                if LEVEL == 'TOP':  # find top label
                    if '.' in classname:  # TOP - begin
                        pos = classname.find('.')
                        classname = classname[0:pos] # TOP - end
                key = classname+'\t'
                if not key in key2value:
                    value = ''
                    for c in str(value_int):
                        value += chr(ord('a')+int(c))
                    key2value[key] = value
                    value_int += 1
                text += ' '+key2value[key]
        if len(text) > 0:
            fw.write(text[1:]+'\n')
    fr.close()
    fw.close()
    labelset = set()
    fr = open(file_input_goodpattern,'rb')
    for line in fr:
        xml = line.strip('\r\n')
        sentence = XMLToSentence(xml)
        text = ''
        for [classname,words] in sentence:
            if classname == '':
                word = words
                if word.lower() in stopwordset:
                    text += ' '+word
                else:
                    key = '\t'+word
                    if not key in key2value:
                        value = ''
                        for c in str(value_int):
                            value += chr(ord('a')+int(c))
                        key2value[key] = value
                        value_int += 1
                    text += ' '+key2value[key]
            else:
                if LEVEL == 'TOP':
                    if '.' in classname: # TOP - begin
                        pos = classname.find('.')
                        classname = classname[0:pos] # TOP - end
                key = classname+'\t'
                if not key in key2value:
                    value = ''
                    for c in str(value_int):
                        value += chr(ord('a')+int(c))
                    key2value[key] = value
                    value_int += 1
                text += ' '+key2value[key]
        if len(text) > 0:
            labelset.add(text[1:])
    fr.close()
    fw = open(file_output_label,'w')
    fw_positive = open(file_output_positive,'w')
    labels = sorted(labelset)
    n_label = len(labels)
    for label in labels:
        fw.write(label+'\t1\n')
        fw_positive.write(label+'\n')
    wordgroups = []
    for label in labels:
        wordgroups.append(label.split(' '))
    for i in range(0,n_label*NEGATIVE):
        k = randint(0,n_label-1)
        l = len(wordgroups[k])
        p = randint(0,l-1)
        q = randint(0,l-1)
        xmin,xmax = min(p,q),max(p,q)
        if xmin == xmax: continue
        label = ''
        for j in range(xmin,xmax+1):
            label += ' '+wordgroups[k][j]
        label = label[1:]
        if label in labelset: continue
        fw.write(label+'\t0\n')
        labelset.add(label)
    fw_positive.close()
    fw.close()
    fw = open(file_output_key,'w')
    for [key,value] in sorted(key2value.items(),key=lambda x:x[1]):
        fw.write(value+'\t'+key+'\n')
    fw.close()


def EncryptFast(file_output_train,file_output_mapping,file_output_casesen,file_output_quality,file_input_entitylinking,file_input_goodpattern,LEVEL):
    key2value = {}
    fw = open(file_output_train,'w')
    fw_casesen = open(file_output_casesen,'w')
    fr = open(file_input_entitylinking,'rb')
    for line in fr:
        xml = line.strip('\r\n')
        sentence = XMLToSentence(xml)
        n = len(sentence)
        text = ''
        text_casesen = ''
        for [classname,words] in sentence:
            if classname == '':
                if type(words) != str:
                    continue
                word = words
                key = word
                if not key in key2value:
                    value = len(key2value)
                    key2value[key] = value
                text += ' '+str(key2value[key])
                text_casesen += '0'
            elif classname == 'PERIOD':
                word = words
                text += ' '+word
                text_casesen += '3'
            else:
                if LEVEL == 'TOP':
                    if '.' in classname:  # TOP - begin
                        pos = classname.find('.')
                        classname = classname[0:pos] # TOP - end
                key = '$'+classname
                if not key in key2value:
                    value = len(key2value)
                    key2value[key] = value
                text += ' '+str(key2value[key])
                text_casesen += '1'
        if len(text) > 0:
            fw.write(text[1:]+'\n')
            fw_casesen.write(text_casesen+'\n')
    fr.close()
    fw_casesen.close()
    fw.close()
    fw = open(file_output_quality,'w')
    fr = open(file_input_goodpattern,'rb')
    for line in fr:
        xml = line.strip('\r\n')
        sentence = XMLToSentence(xml)
        n = len(sentence)
        text = ''
        for [classname,words] in sentence:
            if classname == '':
                word = words
                key = word
                if not key in key2value:
                    value = len(key2value)
                    key2value[key] = value
                text += ' '+str(key2value[key])
            else:
                if LEVEL == 'TOP':
                    if '.' in classname:  # TOP - begin
                        pos = classname.find('.')
                        classname = classname[0:pos] # TOP - end
                key = '$'+classname
                if not key in key2value:
                    value = len(key2value)
                    key2value[key] = value
                text += ' '+str(key2value[key])
        if len(text) > 0:
            fw.write(text[1:]+'\n')
    fr.close()
    fw.close()
    fw = open(file_output_mapping,'w')
    for [key,value] in key2value.items():
        fw.write(str(value)+'\t'+key+'\n')
    fw.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-task',type=str,choices=['encrypt','encryptFast'])
    parser.add_argument('--good-pattern-file',type=str,default='input/goodpattern.txt')
    parser.add_argument('--corpus-file',type=str,default='input/corpus.txt')
    parser.add_argument('--stop-words',type=str,default='input/stopwords.txt')
    parser.add_argument('--negative',type=int,default=10)
    parser.add_argument('--level',type=str,default='TOP')

    args = parser.parse_args()

    # python metapad.py encrypt
    # output/top-encrypted.txt output/top-label.txt output/top-positive.txt output/top-key.txt data/corpus.txt data/goodpattern.txt data/stopwords.txt TOP


    #python metapad.py encryptFast
    # output/top-token-train.txt output/top-token-mapping.txt output/top-token-casesen.txt
    # output/top-token-quality.txt data/corpus.txt data/goodpattern.txt TOP

    if args.task == 'encrypt':
        Encrypt('output/top-encrypted.txt','output/top-label.txt','output/top-positive.txt','output/top-key.txt',
                args.corpus_file,args.good_pattern_file, args.stop_words, args.negative, args.level)
    elif args.task == 'encryptFast':
        EncryptFast('output/top-token-train.txt','output/top-token-mapping.txt','output/top-token-casesen.txt',
                    'output/top-token-quality.txt',args.corpus_file, args.good_pattern_file, args.level)


