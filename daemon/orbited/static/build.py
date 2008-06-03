import shutil
import sys
import os
from minify import jsmin
def load_target(name):
    filename = os.path.join(*name.split('/'))
    f = open(filename)
    data = f.read()
    f.close()
    output = "\n// start @include(%s)\n" % name
    output += data
    output += "\n// end @include(%s)\n" % name
    return output

def fillout(template):
    marker = 0
    output = ""
    while True:
        i = template.find('@include(', marker)
        if i == -1:
            output += template[marker:]
            break
        j = template.find(')@', i)
        k = template.find('\n', i, j)
        if k != -1:
            print "Error, \\n found inside an include body: \"" + template[i:j+2].replace("\n", "\\n") + "\""
            sys.exit(0)
        include_filename = template[i+9:j]
        print "including: " + include_filename
        output += template[marker:i]
        output += load_target(include_filename)
        marker = j+2
    return output
  

def main():
    for name in os.listdir('.'):
        if not name.endswith('.template'):
            continue
        print "Building",  name[:-9]
        f = open(name, 'r')
        template = f.read()
        f.close()
        output = fillout(template)
        print "%s otal Size: %dk" % (name[:-9], len(output)/1024.0 )
        
        f = open(name[:-9], 'w')
        f.write(output)
        f.close()





if __name__ == "__main__":
    main()