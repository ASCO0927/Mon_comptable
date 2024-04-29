from datetime import datetime, date
from pyinvoice.models import InvoiceInfo, ServiceProviderInfo, ClientInfo, Item, Transaction
from pyinvoice.templates import SimpleInvoice

doc = SimpleInvoice('facture.pdf')

# Paid stamp, optional
#doc.is_paid = True

d = str(datetime.now())
d = d.split(" ")[0]

annee = d.split("-")[0]
mois = d.split("-")[1]
jour = d.split("-")[2]

date_fr = "{}/{}/{}".format(jour, mois, annee)

doc.invoice_info = InvoiceInfo(date_fr)

doc.service_provider_info = ServiceProviderInfo(
    city='Bobo-Dioulasso',
    country='Burkina-Faso',
)

doc.add_item(Item('Item', 'Item desc', 1, '1.1'))
doc.add_item(Item('Item', 'Item desc', 2, '2.2'))
doc.add_item(Item('Item', 'Item desc', 3, '3.3'))

doc.set_bottom_tip("Tel: 65136188<br />72184746")

doc.finish()
