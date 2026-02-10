from django import forms
from netbox.forms import NetBoxModelForm, NetBoxModelFilterSetForm
from dcim.models import Device, Site
from virtualization.models import VirtualMachine
from .models import Certificate

# Исправленный импорт для NetBox 4.4
try:
    from utilities.forms.fields import (
        DynamicModelMultipleChoiceField,
        DynamicModelChoiceField,
        TagFilterField
    )
except ImportError:
    from utilities.forms.fields import (
        DynamicModelMultipleChoiceField,
        DynamicModelChoiceField
    )
    from utilities.forms import TagFilterField


class CertificateForm(NetBoxModelForm):
    """Form for creating/editing certificates"""
    
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Devices',
        help_text='Select devices that use this certificate'
    )
    
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machines',
        help_text='Select virtual machines that use this certificate'
    )
    
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Sites',
        help_text='Select sites that use this certificate'
    )
    
    ca_certificate = DynamicModelChoiceField(
        queryset=Certificate.objects.all(),
        required=False,
        label='CA Certificate',
        help_text='CA certificate for chain verification'
    )
    
    class Meta:
        model = Certificate
        fields = [
            'name', 'description', 'certificate_file', 'private_key',
            'ca_certificate', 'devices', 'virtual_machines', 'sites',
            'tags', 'comments'
        ]
        widgets = {
            'certificate_file': forms.Textarea(attrs={
                'rows': 10,
                'class': 'font-monospace',
                'placeholder': '-----BEGIN CERTIFICATE-----\n...\n-----END CERTIFICATE-----'
            }),
            'private_key': forms.Textarea(attrs={
                'rows': 10,
                'class': 'font-monospace',
                'placeholder': '-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----'
            }),
        }


class CertificateImportForm(forms.Form):
    """Form for importing certificates from files"""
    
    certificate_file = forms.FileField(
        label='Certificate File',
        help_text='Upload PEM encoded certificate file (.crt, .pem, .cer)',
        widget=forms.FileInput(attrs={'accept': '.crt,.pem,.cer,.cert'})
    )
    
    private_key_file = forms.FileField(
        required=False,
        label='Private Key File (Optional)',
        help_text='Upload PEM encoded private key file (.key, .pem)',
        widget=forms.FileInput(attrs={'accept': '.key,.pem'})
    )
    
    ca_certificate_file = forms.FileField(
        required=False,
        label='CA Certificate File (Optional)',
        help_text='Upload CA certificate for chain verification',
        widget=forms.FileInput(attrs={'accept': '.crt,.pem,.cer,.cert'})
    )
    
    name = forms.CharField(
        max_length=200,
        help_text='Name for the certificate (leave empty to auto-generate from CN)'
    )
    
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        help_text='Optional description'
    )
    
    devices = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Devices',
        help_text='Assign to devices'
    )
    
    virtual_machines = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machines',
        help_text='Assign to virtual machines'
    )
    
    sites = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Sites',
        help_text='Assign to sites'
    )
    
    verify_chain = forms.BooleanField(
        required=False,
        initial=True,
        label='Verify Certificate Chain',
        help_text='Verify certificate chain if CA certificate is provided'
    )
    
    def clean_certificate_file(self):
        file = self.cleaned_data['certificate_file']
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be text/PEM encoded')
        
        # Validate PEM format
        if not ('-----BEGIN CERTIFICATE-----' in content and '-----END CERTIFICATE-----' in content):
            raise forms.ValidationError('Invalid certificate format. Must be PEM encoded.')
        
        return content
    
    def clean_private_key_file(self):
        file = self.cleaned_data.get('private_key_file')
        if not file:
            return ''
        
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be text/PEM encoded')
        
        # Validate PEM format
        if not ('-----BEGIN' in content and '-----END' in content):
            raise forms.ValidationError('Invalid private key format. Must be PEM encoded.')
        
        return content
    
    def clean_ca_certificate_file(self):
        file = self.cleaned_data.get('ca_certificate_file')
        if not file:
            return ''
        
        try:
            content = file.read().decode('utf-8')
        except UnicodeDecodeError:
            raise forms.ValidationError('File must be text/PEM encoded')
        
        if not ('-----BEGIN CERTIFICATE-----' in content and '-----END CERTIFICATE-----' in content):
            raise forms.ValidationError('Invalid CA certificate format. Must be PEM encoded.')
        
        return content


class CertificateScanForm(forms.Form):
    """Form for scanning domains"""
    
    hostname = forms.CharField(
        max_length=255,
        label='Hostname',
        help_text='Domain name to scan (e.g., example.com)',
        widget=forms.TextInput(attrs={'placeholder': 'example.com'})
    )
    
    port = forms.IntegerField(
        initial=443,
        min_value=1,
        max_value=65535,
        label='Port',
        help_text='SSL/TLS port (default: 443)'
    )
    
    name = forms.CharField(
        max_length=200,
        required=False,
        label='Certificate Name (Optional)',
        help_text='Leave empty to auto-generate (hostname:port)'
    )
    
    update_existing = forms.BooleanField(
        required=False,
        initial=True,
        label='Update Existing Certificate',
        help_text='Update certificate if it already exists'
    )
    
    assign_to_device = DynamicModelChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Assign to Device',
        help_text='Optionally assign certificate to a device'
    )


class CertificateFilterForm(NetBoxModelFilterSetForm):
    """Filter form for certificates"""
    
    model = Certificate
    
    q = forms.CharField(
        required=False,
        label='Search'
    )
    
    status = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'All'),
            ('valid', 'Valid'),
            ('expiring_soon', 'Expiring Soon'),
            ('expired', 'Expired'),
        ],
        label='Status'
    )
    
    device_id = DynamicModelMultipleChoiceField(
        queryset=Device.objects.all(),
        required=False,
        label='Device'
    )
    
    virtual_machine_id = DynamicModelMultipleChoiceField(
        queryset=VirtualMachine.objects.all(),
        required=False,
        label='Virtual Machine'
    )
    
    site_id = DynamicModelMultipleChoiceField(
        queryset=Site.objects.all(),
        required=False,
        label='Site'
    )
    
    is_self_signed = forms.NullBooleanField(
        required=False,
        label='Self-Signed',
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
    
    chain_verified = forms.NullBooleanField(
        required=False,
        label='Chain Verified',
        widget=forms.Select(choices=[
            ('', '---------'),
            ('true', 'Yes'),
            ('false', 'No'),
        ])
    )
    
    tag = TagFilterField(model)