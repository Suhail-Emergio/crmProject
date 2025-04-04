#################################  V A L I D A T E  D A T A  #################################
import re

# Validate Phone Number
def phone_validate(number):
    phone_regex = r'^[6789]\d{9}$'
    return True if re.match(phone_regex, number) else False