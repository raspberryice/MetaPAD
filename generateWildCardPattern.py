def generateWildCardPattern(filename):
    f = open(filename,"r")
    w = open("input/new_goodpattern_wildcard.txt","w")
    i = 0
    for line in f.readlines():
        newLine = ''
        for index in range(len(line)):
            if (line[index] != '<' or (line[index] == '<' and line[index + 1] == '/')):
                newLine += line[index]
                continue;
            else:
                newLine += '* '
                newLine += line[index]
        newLine = newLine.strip(' ')
        w.write(newLine)
    w.close()
    f.close()
if __name__ == '__main__':
    generateWildCardPattern("input/new_goodpattern.txt")


