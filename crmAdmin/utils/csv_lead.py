#################################  C S V  D A T A  F E T C H I N G  #################################
import csv, io
from .validate_util import *
from .assign_utils import *
from crmAdmin.models import *

def csv_fetch(file, admin):
    text_file = io.TextIOWrapper(file, encoding='utf-8')
    csv_reader = csv.reader(text_file)
    header = next(csv_reader)
    normalized_header = [col.lower() for col in header]
    for row in csv_reader:
        cleaned_phone = ''.join(filter(str.isdigit, row[normalized_header.index('phone')].strip()))
        number = cleaned_phone[3:] if cleaned_phone.startswith("+91") else cleaned_phone[2:] if cleaned_phone.startswith("91") else cleaned_phone
        phone_status = phone_validate(number)
        if phone_status:
            if not Lead.objects.filter(phone=number).exists():
                lead = Lead.objects.create(
                    name=row[normalized_header.index('name')].strip(), 
                    phone=number, 
                    email=row[normalized_header.index('email')].strip(), 
                    department=row[normalized_header.index('department')].strip() ,
                    admin=admin,
                )
                lead.save()
                assign_leads(lead)