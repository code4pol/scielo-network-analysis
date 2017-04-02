import urllib.request
import re
import xmltodict
from xml.parsers.expat import ExpatError

f = open('IDhtml.csv')

def retrieve_data(article_html_url):
	article_id = re.search("http://.*pid=(.*?)&",article_html_url).group(1)
	article_pdf_url = "http://www.scielo.br/scieloOrg/php/articleXML.php?pid=%s&lang=en" % article_id

	file = urllib.request.urlopen(article_pdf_url)
	xml = file.read()
	file.close()

	data = {}
	try:
		data = xmltodict.parse(xml)
	except ExpatError as e:
		# XML com problemas
		pass	

	return data


def get_linked_authors_names_expanded(person):
	authors = []
	
	if isinstance(person['name'],list):
		for name in person['name']:

			# Em http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0103-20702014000200003&lang=pt, vem um name = None
			if name:
				surname = ''
				givennames = ''
				if 'surname' in name:
					surname = name['surname']
				if 'given-names' in name:
					givennames = name['given-names']

				authors.append("%s %s" % (surname, givennames))
	else:
		name = person['name']
		if name: # Sim, ha artigos cujo name = None
			surname = ''
			givennames = ''
			if 'surname' in name:
				surname = name['surname']
			if 'given-names' in name:
				givennames = name['given-names']
			authors.append("%s %s" % (surname, givennames))

	return authors


def get_author(data):
	authors = []

	try:
		contribs = data['article']['front']['article-meta']['contrib-group']['contrib']
	except KeyError:
		return authors

	if isinstance(contribs,list):
		for contrib in contribs:
			if contrib['@contrib-type'] == 'author':
				authors.append("%s %s" % (contrib['name']['surname'], contrib['name']['given-names']))
	else:
		contrib = contribs
		if contrib['@contrib-type'] == 'author':
			authors.append("%s %s" % (contrib['name']['surname'], contrib['name']['given-names']))

	return authors


def get_refs(data):
	if 'back' in data['article']:
		return data['article']['back']['ref-list']

def get_linked_authors_names(ref):
	names = []
	if 'person-group' in ref['nlm-citation']:

		person_group = ref['nlm-citation']['person-group']

		# A referencia pode ter apenas autores ou tambem editores.
		# Na duvida, transformo tudo numa lista
		if not isinstance(person_group,list):
			person_group = [person_group]

		for person in person_group:
			if person['@person-group-type'] == 'author':
				
				expanded_names = get_linked_authors_names_expanded(person)
				
				# Como eh o caso do B9 em http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-40362014000400007&lang=pt
				if len(expanded_names) == 0:
					if 'collab' in ref['nlm-citation']:
						expanded_names = [ref['nlm-citation']['collab']]

				names.extend(expanded_names)

	return names

def get_linked_authors(refs):
	linked_authors = []
	
	if isinstance(refs['ref'],list):
		for ref in refs['ref']:
			id = ref['@id']
			type = ref['nlm-citation']['@citation-type']

			if 'article-title' in ref['nlm-citation']:
				title = ref['nlm-citation']['article-title']['#text']
			else:
				title = "?"

			linked = { 'id' : id, 'type' : type, 'names' : get_linked_authors_names(ref)}
			linked_authors.append(linked)
	else:
		ref = refs[ 'ref']
		id = ref['@id']
		type = ref['nlm-citation']['@citation-type']
		linked = { 'id' : id, 'type' : type, 'names' : get_linked_authors_names(ref)}
		linked_authors.append(linked)

	return linked_authors


def print_csv(authors, linked_authors):
	for author in authors:
		for linked_author in linked_authors:
			for linked_name in linked_author['names']:
				print("%s,%s,%s,%s" % (author,linked_author['id'],linked_author['type'],linked_name))

def process_article(article_html_url):
	
	data = retrieve_data(article_html_url)

	if data:
		author = get_author(data)
		refs = get_refs(data)

		if refs:
			linked = get_linked_authors(refs)
			print_csv(author, linked)

if __name__ == "__main__":

	i = 540
	f = f.readlines()[i-1:]

	for l in f:
		# l = "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S1982-88372016000200074&lang=pt"
		print(i,l)
		process_article(l)
		i += 1
