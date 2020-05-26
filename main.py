import traceback

from googlesearch import search
from pip._vendor import requests
from urllib.parse import urlparse
from M3uParser import M3uParser
import logging
from bs4 import BeautifulSoup
import urllib.request
from urllib.parse import urljoin

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}


class loggingSystem:
    def __init__(self, name, arquivo='./arquivo.log', format='%(name)s - %(levelname)s - %(message)s',
                 level=logging.DEBUG):
        """

        :param name: nome do log a ser escrito no arquivo
        :param arquivo: nome do arquivo a ser utilizado
        :param format: formato do texto a ser inserido no output do log
        :param level: nivel de log padrão de saida
        """
        formatter = logging.Formatter(format)
        handler = logging.FileHandler(arquivo)
        handler.setFormatter(formatter)
        f = open(arquivo, "w+")
        f.write("")
        f.close()
        logger = logging.getLogger(name)
        logger.setLevel(level)
        logger.addHandler(handler)
        self.debug = logger.debug
        self.warning = logger.warning
        self.error = logger.error
        self.info = logger.info
        self.log = logger.log
        self.critical = logger.critical
        self.setlevel = logger.setLevel
        self.fatal = logger.fatal


log = loggingSystem(name="m3u parser", arquivo='m3u_Parser.log')
m3u = M3uParser(log)


def pesquisa(termo, start=0, numero_result_page=10, stop=30, pause=0):
    my_results_list = []
    try:
        for i in search(termo,  # The query you want to run
                        tld='com.br',  # The top level domain
                        lang='pt-br',  # The language
                        num=numero_result_page,  # Number of results per page
                        start=start,  # First result to retrieve
                        stop=stop,  # Last result to retrieve
                        pause=pause,  # Lapse between HTTP requests
                        ):
            my_results_list.append(i)
        return my_results_list
    except urllib.error.URLError as E:
        print(E)
        return pesquisa(termo, start, numero_result_page, stop, pause)
    except:
        traceback.print_exc()


def get_links_in_page(url):
    try:
        parser = 'html.parser'
        retorno = []
        req = urllib.request.Request(url, data=None, headers=headers)
        resp = urllib.request.urlopen(req)
        soup = BeautifulSoup(resp, parser, from_encoding=resp.info().get_param('charset'))
        for link in soup.find_all(href=True):
            retorno.append(link['href'])
        return retorno
    except urllib.error.URLError as E:
        if str(E).__contains__("40"):
            print(E)
            return None
        else:
            print(E)
            return get_links_in_page(url)
    except:
        traceback.print_exc()


def get_iptv_from_google(resultados=30):
    retorno = []
    tested = []
    for i in search("iptv m3u",  # The query you want to run
                    tld='com.br',  # The top level domain
                    lang='pt-br',  # The language
                    num=10,  # Number of results per page
                    start=0,  # First result to retrieve
                    stop=resultados,  # Last result to retrieve
                    pause=10,  # Lapse between HTTP requests
                    ):
        print(i)
        sublinks = get_links_in_page(i)

        try:
            if m3u.downloadM3u(i, notSave=True):
                print("m3u valido:")
                print(i)
                tested.append(i)

            for sublink in sublinks:
                if sublink[0] == "/":
                    parsed_uri = urlparse(i)
                    print("substitute")
                    sublink = requests.compat.urljoin('{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri), sublink)
                    print(sublink)
                if sublink not in tested and m3u.downloadM3u(sublink, notSave=True):
                    print("m3u valido:")
                    print(sublink)
                    tested.append(sublink)
                elif sublink not in tested:
                    tested.append(sublink)
        except:
            traceback.print_exc()
    return retorno


#
# while not m3u.downloadM3u("https://pastebin.com/raw/6dXd7i5j",notSave=True):
#     pass
# m3u.remove_offline()
# print(m3u.getList())
print(get_iptv_from_google())
# if m3u.downloadM3u("https://gist.github.com/rubenbruno89/3afe153f09b50ab491330fc214d9b677/raw/2f3a33142be678626fd128da2165e112ccb4a8c7/iptv.m3u",notSave=True):
#     print("m3u")
m3u.remove_duplicate()
m3u.remove_offline()
print(m3u.getList())
