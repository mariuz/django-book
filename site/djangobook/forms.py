from django import newforms as forms
from djangobook.models import Erratum

class ErratumForm(forms.ModelForm):
    class Meta:
        model = Erratum
        exclude = ["book", "date", "approved", "link"]
    
