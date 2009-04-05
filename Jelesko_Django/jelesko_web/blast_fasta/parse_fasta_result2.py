class FASTADescription(object):
    def __init__(self,
                 title,  # Title of the hit
                 score,  # Number of bits (int)
                 e):     # E-value (float)
        self.title = title
        self.score = score
        self.e = e



fasta_file = open ('../../sequence_data/result33.txt')

line = fasta_file.readline()

while 1:
	line = fasta_file.readline()
	if line.startswith("Library:"):
		break
	if not line or line.startswith("Searching..."):
		raise TypeError("Could not find the library line")
lib_line = line.strip()
print lib_line

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
	alignments.append([gi_number, accession_ref, detail, bit, e_value]) 
#	alignments.append([desc, bit, e_value])

return alignments 
  