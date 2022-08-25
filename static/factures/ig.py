import os

from tempfile import NamedTemporaryFile
from InvoiceGenerator.api import Invoice, Item, Client, Provider, Creator, Address
from InvoiceGenerator.pdf import SimpleInvoice

os.environ["INVOICE_LANG"] = "fr"

client = Client('Ecobank')
provider = Provider(summary="Senfenico", city="Bobo-Dioulasso", phone="+226651361880", email="cheicknouhoun@gmail.com", logo_filename="../images/logo.png")
creator = Creator("Emmanuel BOLY")


invoice = Invoice(client, provider, creator)

invoice.add_item(Item(1, 100000, description="Infix hot 10"))
invoice.add_item(Item(1, 50000, description="Infix hot 9"))

pdf = SimpleInvoice(invoice)
pdf.gen("facture.pdf")
