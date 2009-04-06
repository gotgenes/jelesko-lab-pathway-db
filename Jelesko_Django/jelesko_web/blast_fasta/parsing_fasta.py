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
		line = fasta_file.readline()
		line = line.rstrip()
		if line == "":
			break
		position = line.find('(')
		desc = line[:position-1].strip()
		info = line[position:]
		words_desc = desc.split('|')
		gi_number = words_desc[1].strip()
		accession_ref = words_desc[3].strip()
		detail = words_desc[4].strip()
		words_info = info.split()
		bit = words_info[-2].strip()
		e_value = words_info[-1].strip()
		alignments.append({'gi_number':gi_number, 'accession_ref': accession_ref, 'detail':detail, 'bit': bit, 'e_value': e_value}) 
	#	alignments.append([desc, bit, e_value])

	return alignments 
	