from os import environ
from pyuploadcare import Uploadcare

uploadcare = Uploadcare(public_key=environ['UCARE_PUBLIC_KEY'], secret_key=environ['UCARE_SECRET_KEY'])
