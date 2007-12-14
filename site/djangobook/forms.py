from django import newforms as forms
from djangbook.models import Erratum

class ErratumForm(forms.ModelForm):

    class Meta:
        model = Erratum
        exclude = ["book", "date", "approved", "link"]

    def __init__(self, *args, **kwargs):
        super(ErratumForm, self).__init__(*args, **kwargs)
        self.base_fields["chapter"].queryset = self.instance.book.version.chapters.all()
    
