import os.path

class Normalizer(object):

    def __init__(self, maxFolderNameLen):
        self.maxFolderName = maxFolderNameLen
        self.charMap = {
            'а': 'a',
            'б': 'b',
            'в': 'v',
            'г': 'g',
            'д': 'd',
            'е': 'e',
            'ж': 'z',
            'з': 'z',
            'и': 'i',
            'й': 'i',
            'к': 'k',
            'л': 'l',
            'м': 'm',
            'н': 'n',
            'о': 'o',
            'п': 'p',
            'р': 'r',
            'с': 's',
            'т': 't',
            'у': 'u',
            'ф': 'f',
            'х': 'x',
            'ц': 'ts',
            'ч': 'ch',
            'ш': 'sh',
            'щ': 'sh',
            'ь': '',
            'ы': 'y',
            'ъ': '',
            'э': 'e',
            'ю': 'yu',
            'я': 'ya'
        }

    def _transliterate(self, folder):
        result = ""
        for c in folder:
            if c in self.charMap:
                result = result + self.charMap[c]
            else:
                result = result + c

        return result

    def _shorten(self, folder):
        parts = folder.replace('.', ' ').replace('-', ' ').replace('_', ' ').split(' ')
        parts2 = []
        for x in parts:
            if not (len(x) == 0 or x.isspace()):
                parts2.append(x)

#        if len(parts2) > 2:
#            folder = parts2[0] + '.' + parts2[1] + '.' + parts2[2]

        folder = self._transliterate(".".join(parts2[:3]))

        if len(folder) > self.maxFolderName:
            folder = folder[:self.maxFolderName]

        return folder

    def _normalize_folder(self, folder):
        # remove CD1
        tokens = os.path.split(folder)
        if tokens[1].startswith("cd"):
            folder = tokens[0]

        # take 2 deepest subfolders
        tokens = os.path.split(folder)
        last = tokens[1]
        prev = os.path.split(tokens[0])[1]

        if len(prev) > 0:
            folder = self._shorten(prev) + '-' + self._shorten(last)
        else:
            folder = self._shorten(last)

        if (len(folder) > self.maxFolderName):
            temp = ""
            for c in folder:
                if c.isalpha() or c == '-':
                    temp += c
            folder = temp

        l = len(folder)
        if l > self.maxFolderName:
            folder = folder[0:self.maxFolderName]
        return folder
    
    def normalize_path(self, path):
        tokens = os.path.split(path)
        folder = self._normalize_folder(tokens[0].lower())
        tokens = os.path.splitext(tokens[1].lower())
        name = self._shorten(tokens[0])
        ext  = tokens[1]
        path = os.path.join(folder, name + ext)

        n = 0
        while os.path.isfile(path):
            n = n + 1
            path = os.path.join(folder, name + str(n) + ext)

        return path
        

def __test():
    norm = Normalizer(15)
    print(norm.normalize_path("third\\p1    p2\\CD1\\fname.mpg"))
    print(norm.normalize_path("aaa\\bBbйЦ\CD1\\fname.mpg"))
    print(norm.normalize_path("first\\second\\third\\CD1\\fname.mpg"))
    print(norm.normalize_path("third\\CD1\\fname.mpg"))
    print(norm.normalize_path("third\\fname.zaets.mpg"))
    print(norm.normalize_path("Music_2012_05_22\\Calexico\\2003 - Feast Of Wire\\ass.mpg"))
    print(norm.normalize_path("The.Rolling.Stones-Discography.1964-2010.MP3.320kbps.ParadiSe.Kinozal.TV\\1978 - Some Girls (1999 Remastered)\\03 Just Me Imagination.mp3"))
    print(norm.normalize_path("Music_2012_05_22\Makarevich & Mashina Vremeni\\Макаревич\\1994 - Я рисую тебя (оригинал)\\03. А.Макаревич - Наверно, без нас.mp3"))
    print(norm.normalize_path("Music_2012_05_22\Makarevich & Mashina Vremeni\\_________Машина Времени - 1975-2007\\1993 - Внештатный Командир Земли\\08 - На семи ветрах.mp3"))


if __name__ == '__main__':
    __test()
