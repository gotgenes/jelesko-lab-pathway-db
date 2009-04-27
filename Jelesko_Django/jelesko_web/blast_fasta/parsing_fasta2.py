from models import Protein

# b = Protein.objects.get(gi = 5819099)
# print b.sequence

def parsing_fasta(fasta_file):
	"""docstring for parsing_fasta"""
	line = fasta_file.readline()
	while 1:
		line = fasta_file.readline()
		if line.startswith("The best scores are:"):
			break
		if not line:
			raise TypeError("Could not find the best scores lines")

	alignments = []
	while 1:
# for line in fasta_file:
		line = fasta_file.readline()
		line = line.rstrip()
		if line == "":
			break
		position = line.find('(')
		desc = line[:position-1].strip()
		info = line[position:]
		words_desc = desc.split('|')
		gi_number = words_desc[1].strip()
		b = Protein.objects.get(gi = gi_number)
		accession = b.accession.strip()
		genus_species = b.genus_species.strip()
		annotation = b.annotation.strip()
		download_date = b.download_date
		words_info = info.split()
		bit = words_info[-2].strip()
		e_value = words_info[-1].strip()
		alignments.append({'gi_number':gi_number, 'bit': bit, 'e_value': e_value, 'accession': accession, 'genus_species':genus_species, 'annotation': annotation, 'download_date': download_date})
	#	alignments.append([desc, bit, e_value])

	return alignments

