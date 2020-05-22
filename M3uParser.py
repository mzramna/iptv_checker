#!/usr/bin/python3
# Purpose:	
# Usage:	
# Author:	Timmy93
# Date:		
# Version:	
# Disclaimer:	

import os
import re
import traceback
import urllib.request
import random
from ssl import CertificateError

import validators


class M3uParser:

    def __init__(self, logging):
        self.files = []
        self.logging = logging
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    # Download the file from the given url
    def downloadM3u(self, url, filename="", notSave=False):
        try:
            is_m3u, filename = self.isM3u(url, filename, notSave=False)
        except TypeError:
            return False
        if is_m3u:
            self.readAllLines(filename)
            self.parseFile()
            if notSave:
                os.remove(filename)
            else:
                self.filename = filename
        return is_m3u

    def isM3u(self, url, filename="", notSave=True):
        retorno = False
        if not validators.url(url):
            return retorno
        if not notSave:#not save false
            currentDir = os.path.dirname(os.path.realpath(__file__))
            if filename == "":
                filename = "test.m3u"
            try:
                filename = os.path.join(currentDir, filename)
                urllib.request.urlretrieve(url, filename)
                file = open(self.filename, encoding="utf8")

                if file[0] == "#EXTM3U":
                    retorno = True
                return retorno, filename
            except urllib.error.HTTPError as E:
                print(E)
                return retorno
            except urllib.error.URLError as E:
                if str(E).__contains__("Errno 11001"):
                    return retorno
                else:
                    print(E)
                    return retorno
            except:
                return retorno
        else:# notsave true
            try:
                req = urllib.request.Request(url, data=None, headers=self.headers)
                page = urllib.request.urlopen(req)
                pagina = str(page.read()).split('\\n')
                for line in pagina:
                    if line.__contains__("#EXTM3U"):
                        retorno = True
                        return retorno
            except urllib.error.HTTPError as E:
                print(E)
                return retorno
            except urllib.error.URLError as E:
                if str(E).__contains__("Errno 11001"):
                    return retorno
                else:
                    print(E)
                return retorno
            except:
                traceback.print_exc()
                return retorno

    # Read the file from the given path
    def readM3u(self, filename):
        self.filename = filename
        self.readAllLines()
        self.parseFile()

    # Read all file lines
    def readAllLines(self, filename=""):
        # try:
        if filename == "":
            self.lines = [line.rstrip('\n') for line in open(self.filename, encoding="utf8")]
        else:
            self.lines = [line.rstrip('\n') for line in open(filename, encoding="utf8")]
        return len(self.lines)

    def parseFile(self):
        numLine = len(self.lines)
        for n in range(numLine):
            line = self.lines[n]
            try:
                if line[0] == "#":
                    # print("Letto carattere interessante")
                    self.manageLine(n)
            except IndexError:
                pass

    def manageLine(self, n):
        lineInfo = self.lines[n]
        lineLink = self.lines[n + 1]
        if not validators.url(lineLink):
            return 0
        test = {}
        if lineInfo != "#EXTM3U":
            tags = re.findall(r"\ (.*?)=", lineInfo)
            self.logging.info("infos: " + str(lineInfo) + " tags: " + str(tags))
            for tag in tags:
                try:
                    m = re.search(tag + "=\"(.*?)\"", lineInfo)
                    value = m.group(1)
                except AttributeError as E:
                    value = ""

                test[tag] = value
            test["link"] = lineLink
            self.files.append(test)

    def exportJson(self):
        # TODO
        print("Not implemented")

    # Select only files that contais a certain filterWord
    def filterInFilesOfGroupsContaining(self, filterWord):
        # Use the filter words as list
        if not isinstance(filterWord, list):
            filterWord = [filterWord]
        if not len(filterWord):
            self.logging.info("No filter in based on groups")
            return
        new = []
        for file in self.files:
            for fw in filterWord:
                if fw in file["tvg-group"]:
                    # Allowed extension - go to next file
                    new.append(file)
                    break
        self.logging.info("Filter in based on groups: [" + ",".join(filterWord) + "]")
        self.files = new

    # Getter for the list
    def getList(self):
        return self.files

    # Return the info assciated to a certain file name
    def getCustomTitle(self, originalName):
        result = list(filter(lambda file: file["titleFile"] == originalName, self.files))
        if len(result):
            return result
        else:
            print("No file corresponding to: " + originalName)

    # Return a random element
    def getFile(self, randomShuffle):
        if randomShuffle:
            random.shuffle(self.files)
        if not len(self.files):
            self.logging.error("No files in the array, cannot extract anything")
            return None
        return self.files.pop()

    def remove_offline(self):
        for line in self.lines:
            try:
                code = urllib.request.urlopen(line["link"]).getcode()
                # if code == 200:  #Edited per @Brad's comment
                if str(code).startswith('2') or str(code).startswith('3'):
                    pass
                else:
                    self.logging.info(str(line) + " is offline and get code: " + str(code))
                    self.lines.remove(line)
            except urllib.error.HTTPError as E:
                self.logging.error(str(line) + " is offline and get error " + str(E))
                self.lines.remove(line)
            except CertificateError as E:
                self.logging.error(str(line) + " get error " + str(E))
            except urllib.error.URLError as E:
                self.logging.error(str(line) + " get error " + str(E))

    def remove_duplicate(self):
        for line in self.lines:
            for comparated_line in self.lines:
                if self.lines.index(line) != self.lines.index(comparated_line):
                    if line["link"] == comparated_line["link"]:
                        self.lines.remove(comparated_line)
