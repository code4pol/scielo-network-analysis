import urllib.request
import re
import xmltodict

article_html_url = "http://www.scielo.br/scielo.php?script=sci_arttext&pid=S0104-026X2017000100031&lng=en&nrm=iso"
article_id = re.search("http://.*pid=(.*?)&",article_html_url).group(1)
article_pdf_url = "http://www.scielo.br/scieloOrg/php/articleXML.php?pid=%s&lang=en" % article_id

file = urllib.request.urlopen(article_pdf_url)
xml = file.read()

data = xmltodict.parse(xml)
refs = data['article']['back']['ref-list']

# E se houver mais de um author?
contrib = data['article']['front']['article-meta']['contrib-group']['contrib']
if contrib['@contrib-type'] == 'author':
	author = "%s %s" % (contrib['name']['surname'], contrib['name']['given-names'])

for ref in refs['ref']:
	id = ref['@id']
	type = ref['nlm-citation']['@citation-type']
	referees = []

	if 'article-title' in ref['nlm-citation']:
		title = ref['nlm-citation']['article-title']['#text']

	if 'person-group' in ref['nlm-citation']:

		person_group = ref['nlm-citation']['person-group']

		if isinstance(person_group ,list): # autores e editores

			for person in person_group:

				if person['@person-group-type'] == 'author':
					if isinstance(person['name'],list):
						for name in person['name']:
							referees.append("%s %s" % (name['surname'], name['given-names']))
					else:
						name = person['name']
						referees.append("%s %s" % (name['surname'], name['given-names']))

		else: # so autores, provavelmente

			person = person_group

			if person['@person-group-type'] == 'author':
				if isinstance(person['name'],list):
					for name in person['name']:
						referees.append("%s %s" % (name['surname'], name['given-names']))
				else:
					name = person['name']
					referees.append("%s %s" % (name['surname'], name['given-names']))


	for referee in referees:
		print('%s,%s,%s,%s' % (author,id,type,referee))


file.close()

