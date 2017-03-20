import urllib.request
import re
import xmltodict

def retrieve_data(article_html_url):
	article_id = re.search("http://.*pid=(.*?)&",article_html_url).group(1)
	article_pdf_url = "http://www.scielo.br/scieloOrg/php/articleXML.php?pid=%s&lang=en" % article_id

	file = urllib.request.urlopen(article_pdf_url)
	xml = file.read()
	file.close()

	return xmltodict.parse(xml)


def get_authors(person):
	authors = []
	if isinstance(person['name'],list):
		for name in person['name']:
			authors.append("%s %s" % (name['surname'], name['given-names']))
	else:
		name = person['name']
		authors.append("%s %s" % (name['surname'], name['given-names']))

	return authors


def get_author(data):
	# E se houver mais de um author?
	contrib = data['article']['front']['article-meta']['contrib-group']['contrib']
	if contrib['@contrib-type'] == 'author':
		author = "%s %s" % (contrib['name']['surname'], contrib['name']['given-names'])

	return author


def get_refs(data):
	return data['article']['back']['ref-list']

def get_names(ref):
	names = []
	if 'person-group' in ref['nlm-citation']:

		person_group = ref['nlm-citation']['person-group']

		# A referencia pode ter apenas autores ou tambem editores.
		# Na duvida, transformo tudo numa lista
		if not isinstance(person_group,list):
			person_group = [person_group]

		for person in person_group:
			if person['@person-group-type'] == 'author':
				names.extend(get_authors(person))

	return names

def get_linked_authors(data):
	linked_authors = []

	for ref in refs['ref']:
		id = ref['@id']
		type = ref['nlm-citation']['@citation-type']

		if 'article-title' in ref['nlm-citation']:
			title = ref['nlm-citation']['article-title']['#text']
		else:
			title = "?"

		linked = { 'id' : id, 'type' : type, 'names' : get_names(ref)}
		linked_authors.append(linked)

	return linked_authors


def print_csv(author, linked_authors):
	for linked_author in linked_authors:
		print("%s,%s,%s,%s" % (author,linked_author['id'],linked_author['type'],linked_author['names']))


if __name__ == "__main__":
	
	article_html_url = "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-026X2017000100031&lng=en&nrm=iso"
	data = retrieve_data(article_html_url)

	author = get_author(data)
	refs = get_refs(data)
	linked = get_linked_authors(data)
	print_csv(author, linked)

