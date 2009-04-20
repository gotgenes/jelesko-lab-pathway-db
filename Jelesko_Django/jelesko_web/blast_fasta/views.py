# Create your views here.
sequence_data_dir = '/Users/caiyizhi/Dropbox/Class/Problem_solving/jelesko-lab-pathway-db/Jelesko_Django/sequence_data/'




from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
class blastform(forms.Form):
	    seq = forms.CharField(widget=forms.Textarea)
	    evalue = forms.FloatField(initial=1) #initial only for unbound form, not here because get data from GET
	    wsoptions=[('9','9'),('10','10'),('11','11'),('12','12'),('14','14'),('16','16')]
	    #ws=forms.ChoiceField(label="Word Size", choices=wsoptions,initial='12') 
	    dboptions = [('/Users/caiyizhi/Desktop/db.fasta', 'Complete DB'), ('/Users/caiyizhi/Dropbox/Class/Problem_solving/jelesko-lab-pathway-db/Jelesko_Django/sequence_data/db.fasta', 'Sample DB')]
	    database_option = forms.ChoiceField(label="Database", choices = dboptions, initial = 'Sample DB')
 

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response
from django import forms
class fastaform(forms.Form):
	"""docstring for fastaform"""
	seq = forms.CharField(widget = forms.Textarea)
	number_sequence = forms.FloatField(initial = 10)    # -b 
	number_alignment_highest = forms.FloatField(initial = 10)   # -E limited number of alignments base on expected number of scores, set the highest
	number_alignment_lowest = forms.FloatField(initial = 0.1) # -F limited number of alighments based on expected number of scores, set the lowes 
	mfoptions = [('P250', 'pam250.mat'), ('P120', 'pam120.mat'), ('BL50', 'BLOSUM50'), ('BL62', 'BLOSUM62'), ('BL80', 'BLOSUM80')]
	matrix_file = forms.ChoiceField(label="Matrix File", choices = mfoptions, initial = 'BLOSUM50') 
	dboptions = [('/Users/caiyizhi/Desktop/db.fasta', 'Complete DB'), ('/Users/caiyizhi/Dropbox/Class/Problem_solving/jelesko-lab-pathway-db/Jelesko_Django/sequence_data/db.fasta', 'Sample DB')]
	database_option = forms.ChoiceField(label="Database", choices = dboptions, initial = 'Sample DB')
	ktupoptions = [('1', 'ktup=1'), ('2', 'ktup=2')]
	ktup = forms.ChoiceField(label="Ktup", choices=ktupoptions, initial = "2")


 
from django import forms   
class displayform(forms.Form):
	"""docstring for displayform"""
	check_box = forms.BooleanField(required = False)
	gi_number = forms.CharField()
	bit_score = forms.CharField()
	e_value = forms.CharField()
	accession = forms.CharField()
	genus_species = forms.CharField()
	annotation = forms.CharField()
	download_date = forms.CharField()         

def fasta(request):
	"""docstring for fasta"""
	import os
	import parsing_fasta2
	import time	
	my_fasta_file = sequence_data_dir + "/fasta_seq.fasta"
	sqfile = open(my_fasta_file, "w")
	if request.method == 'GET':
		f = fastaform(request.GET)
		if not f.is_valid():
			return render_to_response('blast_fasta/fasta2.html', {'form': f, 'res': ''})
		else:
			sqfile.write(f.cleaned_data["seq"])
			sqfile.close()
			if not f.cleaned_data["number_sequence"]:
				b = 10
			else:
				b = f.cleaned_data["number_sequence"]
			if not f.cleaned_data["number_alignment_highest"]:
				E = 10
			else:
				E = f.cleaned_data["number_alignment_highest"]
			if not f.cleaned_data["number_alignment_lowest"]:
				F = 0
			else:
				F = f.cleaned_data["number_alignment_lowest"]
			s = f.cleaned_data["matrix_file"]
			db = f.cleaned_data["database_option"]
			kt = f.cleaned_data["ktup"]	
			cmd = 'fasta35 -b '+ str(b) + ' -E '+ str(E) + ' -F ' +str(F) + ' -s ' +str(s) + ' '+ sequence_data_dir + 'fasta_seq.fasta '+ str(db) + ' ' + str(kt) + ' > '+ sequence_data_dir + 'fasta_output.txt'
			start = time.clock()
			os.system(cmd)
			end = time.clock()
			duration = end - start
			fasta_file = open(sequence_data_dir + 'fasta_output.txt')
		res = parsing_fasta2.parsing_fasta(fasta_file)
		result = {
		'check_box': True,
		'gi_number': 'gi'
		}
		d = displayform(result, request.POST)
	return render_to_response('blast_fasta/fasta2.html', {'form':f, 'res': res, 'duration':duration, 'form2': d})    
	
def ssearch(request):
	"""docstring for fasta"""
	import os
	import parsing_fasta2
	import time	
	my_fasta_file = sequence_data_dir + "ssearch_seq.fasta"
	sqfile = open(my_fasta_file, "w")
	if request.method == 'GET':
		f = fastaform(request.GET)
		if not f.is_valid():
			return render_to_response('blast_fasta/ssearch.html', {'form': f, 'res': ''})
		else:
			sqfile.write(f.cleaned_data["seq"])
			sqfile.close()
			if not f.cleaned_data["number_sequence"]:
				b = 10
			else:
				b = f.cleaned_data["number_sequence"]
			if not f.cleaned_data["number_alignment_highest"]:
				E = 10
			else:
				E = f.cleaned_data["number_alignment_highest"]
			if not f.cleaned_data["number_alignment_lowest"]:
				F = 0
			else:
				F = f.cleaned_data["number_alignment_lowest"]
			s = f.cleaned_data["matrix_file"]
			db = f.cleaned_data["database_option"]
			kt = f.cleaned_data["ktup"]
			start = time.clock()
			cmd = 'ssearch35 -b '+ str(b) + ' -E '+ str(E) + ' -F ' +str(F) + ' -s ' +str(s) + ' '+ sequence_data_dir + 'ssearch_seq.fasta '+ str(db) + ' '+ str(kt) + ' > '+ sequence_data_dir + 'ssearch_output.txt'
			os.system(cmd)              
			end = time.clock()
			duration = end - start
			fasta_file = open(sequence_data_dir + '/ssearch_output.txt')
		res = parsing_fasta2.parsing_fasta(fasta_file)
	return render_to_response('blast_fasta/ssearch.html', {'form':f, 'res': res, 'duration':duration})


from models import Protein

def blast(request):
	"""docstring for blast"""
	from models import Protein
	from Bio.Blast import NCBIStandalone
	from Bio.Blast import NCBIXML
	import time
	import os
	my_blast_dir = sequence_data_dir
	my_blast_file = sequence_data_dir + "/seq.fasta"
	sqfile = open(my_blast_file, "w")
#	my_blast_db = sequence_data_dir + "/db.fasta"
	if request.method == 'GET':
		f = blastform(request.GET)
		if not f.is_valid():
			return render_to_response('blast_fasta/blast2.html', {'form': f,'res':''}) #do sth else
		else: 
			sqfile.write(f.cleaned_data["seq"])
			sqfile.close()
			if not f.cleaned_data["evalue"]: #does not work
				e=1
			else: 
				e=f.cleaned_data["evalue"]
			#wsize=f.cleaned_data["ws"]
			#wsize = 12
			my_blast_exe = "/usr/bin/blastall"
			my_blast_db = str(f.cleaned_data["database_option"])
		   # result_handle, error_handle = NCBIStandalone.blastall(blastcmd = my_blast_exe,  program = "blastp", database = my_blast_db, infile = my_blast_file)
			start = time.clock()
			result_handle, error_handle = NCBIStandalone.blastall(blastcmd = my_blast_exe,  program = "blastp", database = my_blast_db, infile = my_blast_file, expectation = e) 
			blast_records = NCBIXML.parse(result_handle)                             
			end = time.clock()
			duration = end - start
			res = []
			for br in blast_records:
				for a in br.alignments:
					for hsp in a.hsps:
						title_desc = a.title.split('|')
						gi_number = title_desc[-1]
						b = Protein.objects.get(gi = gi_number)
						accession = b.accession.strip()
						genus_species = b.genus_species.strip()
						annotation = b.annotation.strip()
						download_date = b.download_date
						res.append((gi_number,hsp.expect, accession, genus_species, annotation, download_date))
	return render_to_response('blast_fasta/blast2.html', {'form': f,'res':res, 'duration': duration})   
	
	
	
	