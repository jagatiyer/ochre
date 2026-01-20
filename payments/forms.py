from django import forms


class AddressForm(forms.Form):
    full_name = forms.CharField(label="Full name", max_length=200)
    line1 = forms.CharField(label="Address line 1", max_length=255)
    line2 = forms.CharField(label="Address line 2", max_length=255, required=False)
    city = forms.CharField(label="City", max_length=100)
    state = forms.CharField(label="State / Region", max_length=100)
    postcode = forms.CharField(label="Postal code", max_length=20)
    country = forms.CharField(label="Country", max_length=100, initial="India")
    phone = forms.CharField(label="Phone", max_length=30, required=False)


class BookingForm(forms.Form):
    experience_id = forms.IntegerField(widget=forms.HiddenInput)
    date = forms.DateField(label="Date", widget=forms.DateInput(attrs={"type": "date"}))
    time_slot = forms.CharField(label="Time slot", max_length=100)
    customer_name = forms.CharField(label="Name", max_length=200)
    customer_email = forms.EmailField(label="Email")
    customer_phone = forms.CharField(label="Phone", max_length=30, required=False)
    notes = forms.CharField(label="Notes", widget=forms.Textarea, required=False)
