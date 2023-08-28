
from django.test import TestCase
txt = 'I like bananas bananas'

x = txt.replace('bananas', 'apples', 1)
# Create your tests here.
print(x)