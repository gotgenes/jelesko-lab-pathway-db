{% for i in record %}
<td><a href="http://www.genocad.org/{{i}}">{{i}}</a></td>
{% endfor %}             

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
