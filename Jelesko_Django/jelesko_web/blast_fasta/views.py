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
	matrix_file = forms.ChoiceField(label="Matrix File", choices = mfoptions, initial = 'BL50')


def fasta(request):
	"""docstring for fasta"""
	import os
	import parsing_fasta	
	my_fasta_file = sequence_data_dir + "/fasta_seq.fasta"
	sqfile = open(my_fasta_file, "w")
	if request.method == 'GET':
		f = fastaform(request.GET)
		if not f.is_valid():
			return render_to_response('blast_fasta/fasta.html', {'form': f, 'res': ''})
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
			cmd = 'rm '+ sequence_data_dir + '/fasta_output.txt|fasta35 -b '+ str(b) + ' -E '+ str(E) + ' -F ' +str(F) + ' -s ' +str(s) + ' '+ sequence_data_dir + '/fasta_seq.fasta '+ sequence_data_dir+'/db.fasta > '+ sequence_data_dir + '/fasta_output2.txt'
			os.system(cmd)
			fasta_file = open(sequence_data_dir + '/fasta_output2.txt')
		res = parsing_fasta.parsing_fasta(fasta_file)
	return render_to_response('blast_fasta/fasta.html', {'form':f, 'res': res})    
	

def blast(request):
	"""docstring for blast"""
	from Bio.Blast import NCBIStandalone
	from Bio.Blast import NCBIXML
	import os
	my_blast_dir = sequence_data_dir
	my_blast_file = sequence_data_dir + "/seq.fasta"
	sqfile = open(my_blast_file, "w")
	my_blast_db = sequence_data_dir + "/db.fasta"
	if request.method == 'GET':
		f = blastform(request.GET)
		if not f.is_valid():
			return render_to_response('blast_fasta/blast.html', {'form': f,'res':''}) #do sth else
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
		   # result_handle, error_handle = NCBIStandalone.blastall(blastcmd = my_blast_exe,  program = "blastp", database = my_blast_db, infile = my_blast_file)
			result_handle, error_handle = NCBIStandalone.blastall(blastcmd = my_blast_exe,  program = "blastp", database = my_blast_db, infile = my_blast_file, expectation = e) 
			blast_records = NCBIXML.parse(result_handle)
			res = []
			for br in blast_records:
				for a in br.alignments:
					for hsp in a.hsps:
						res.append((a.accession,a.length,hsp.expect,hsp.identities,hsp.query_start,hsp.sbjct_start,hsp.query_end,hsp.sbjct_end))
	return render_to_response('blast_fasta/blast.html', {'form': f,'res':res})