#!/usr/bin/python
# coding=utf-8 
from bs4 import BeautifulSoup
import urllib2
import codecs
import re
import sys, getopt

class Analyzer(object):
	"""docstring for Analyzer"""
	def __init__(self):
		super(Analyzer, self).__init__()
	
	# get the page of the blog by url
	def get(self, url):
		headers = {'User-Agent': 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36'}
		req = urllib2.Request(url, headers=headers)
		html_doc = urllib2.urlopen(req).read()
		return html_doc

	def getContent(self, soup):
		return soup.find(id='container').find(id='body').find(id='main').find(class_='main')
		

class Exporter(Analyzer):
	"""docstring for Exporter"""
	def __init__(self):
		super(Exporter, self).__init__()

	# get the title of the article
	def getTitle(self, detail):
		return detail.find(class_='article_title').h1.span.a.get_text().split('\r\n')[1]

	def export(self, link, f):
		html_doc = self.get(link)
		soup = BeautifulSoup(html_doc)
		detail = self.getContent(soup).find(id='article_details')
		f.write(u'#' + self.getTitle(soup) + u'\n')
		article_content = detail.find(class_='article_content')
		f.write(article_content.text)

	def run(self, link, f):
		self.export(link, f)
		

class Parser(Analyzer):
	"""docstring for parser"""
	def __init__(self):
		super(Parser, self).__init__()
		self.article_list = []
		self.page = -1

	# get the articles' link
	def parse(self, html_doc):
		soup = BeautifulSoup(html_doc)
		res = self.getContent(soup).find(class_='list_item_new').find(id='article_list').find_all(class_='article_item')
		i = 0
		for ele in res:
			self.article_list.append('http://blog.csdn.net/' + ele.find(class_='article_title').h1.span.a['href'])

	# get the page of the blog
	# may have a bug, because of the encoding
	def getPageNum(self, html_doc):
		soup = BeautifulSoup(html_doc)
		self.page = 1;
		res = self.getContent(soup).find(id='papelist').span
		# get the page from text
		buf = str(res).split(' ')[3]
		strpage = ''
		for i in buf:
			if i >= '0' and i <= '9':
				strpage += i
		# cast str to int
		self.page =  int(strpage)
		return self.page

	# get all the link
	def getAllArticleLink(self, url):
		self.getPageNum(self.get(url))
		# self.parse(self.get(url))
		for i in range(1, self.page + 1):
			self.parse(self.get(url + '/article/list/' + str(i)))


	def export2markdown(self):
		for link in self.article_list:
			exporter = Exporter()
			f = codecs.open(link.split('/')[7] + '.md', 'w', encoding='utf-8')
			exporter.run(link, f)
			f.close()

	# the page given
	def run(self, url, page = -1):
		self.page = -1
		self.article_list = []
		if page == -1:
			self.getAllArticleLink(url)
		else:
			if page <= self.getPageNum(self.get(url)):
				self.parse(self.get(url + '/article/list/' + str(page)))
			else:
				print 'page overflow:-/'
				sys.exit(2)
		self.export2markdown()
	

def main(argv):
	page = -1
	directory = '-1'
	try:
		opts, args = getopt.getopt(argv,"hu:p:o:")
	except Exception, e:
		print 'main.py -u <username> [-p <page>] [-o <outputDirectory>]'
		sys.exit(2)

	for opt, arg in opts:
		if opt == '-h':
			print 'main.py -u <username> [-p <page>] [-o <outputDirectory>]'
			sys.exit()
		elif opt == '-u':
			username = arg
		elif opt == '-p':
			page = arg
		elif opt == '-o':
			directory = arg
	url = 'http://blog.csdn.net/' + username
	parser = Parser()
	if page != -1:
		parser.run(url, page)
	else:
		parser.run(url)

if __name__ == "__main__":
   main(sys.argv[1:])