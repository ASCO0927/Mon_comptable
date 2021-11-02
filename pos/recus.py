from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime, date
from reportlab.platypus import Image, Table
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import json
import platform
from pathlib import Path

def enregistrer_recu_type1(liste_articles_a_vendre):
    ville = "Bobo-Dioulasso"
    pays = "Burkina-Faso"
    entreprise = "Kindo Telecom"
    tel1 = "+22678028600"
    tel2 = "+22676671048"
    logo_path = ""
    backgroung_image_path = ""
    facture_path = ""
    
    if platform.system() == "Linux":
    	logo_path = './pos/static/images/logo.png'
    	backgroung_image_path = './pos/static/images/bg.png'
    	facture_path = './pos/static/factures/facture.pdf'
    elif platform.system() == "Windows":
    	home_dir = str(Path.home())
    	logo_path = f"{home_dir}/ALPOS-dev/pos/static/images/logo.png".replace("\\", "//")
    	backgroung_image_path = f"{home_dir}/ALPOS-dev/pos/static/images/bg.png".replace("\\", "//")
    	facture_path = f"{home_dir}/ALPOS-dev/pos/static/factures/facture.pdf".replace("\\", "//")
    	
    	
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    canvas = Canvas(facture_path)

    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)

    canvas.drawImage(backgroung_image, 0, 0, width=letter[0], height=letter[1]+100, mask="auto")

    #logo
    canvas.drawImage(logo, 70, 710, width=100, height=100, mask='auto')

    #date
    canvas.setFont('Helvetica', 13)
    x = letter[0]-70-100-5
    y = 800
    canvas.drawString(x, y, f"Date: {date_fr}")

    #entreprise
    canvas.setFont('Helvetica-Bold', 29)
    x = 200
    y = 790 #777
    canvas.drawString(x, y, f"{entreprise}")

    #ville
    x = letter[0]-70-100-29
    y = 777-20+10
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Ville: {ville}")

    #pays
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Pays: {pays}")

    #tel
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel1}")
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel2}")
    
    #desc
    x_desc = 230
    y_desc = 767
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x_desc, y_desc, f"Vente de téléphones, ordinateurs et")
    x_desc = 250
    y_desc = 757
    canvas.drawString(x_desc, y_desc, f"appareils électroménagers")

    #details
    #canvas.setFont('Helvetica-Bold', 20)
    #x = 70
    #y = y-50
    #canvas.drawString(x, y, "Détail")

    #tableau
    data= [['Article', 'Quantite', 'Prix Unitaire', 'Sous Total']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = int(article["quantite"])*float(article["prix"])
        total = total + st
        data.append([article["article"], article["quantite"], float(article["prix"]), st])

    table=Table(data, colWidths='*')
    table.setStyle(
        TableStyle(
            [
                ('ALIGN',(1,1),(-1,-1),'RIGHT'),
                ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                ('BOX', (0,0), (-1,-1), 0.25, colors.black), 
            ]
        )
    )

    #table = Table(data, )
    x = 70
    y = y-20*len(data)-50
    table.wrapOn(canvas, letter[0]-150, letter[1])
    table.drawOn(canvas, x, y)


    #total
    x = letter[0]-70-100-5
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Total: {total} fcfa")

    #le vendeur
    x = 70
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, "Le Vendeur")
    canvas.line(x,y-5,x+70,y-5)

    #le client
    x = letter[0]-70-100-5
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, "Le Client")
    canvas.line(x,y-5,x+50,y-5)

    canvas.showPage()
    canvas.save()

def enregistrer_recu_type2(liste_articles_a_vendre):
    ville = "Bobo-Dioulasso"
    pays = "Burkina-Faso"
    entreprise = "logoba-agriculture"
    tel = "+22665136188"
    logo_path = ""
    backgroung_image_path = ""
    facture_path = ""
    
    if platform.system() == "Linux":
    	logo_path = './pos/static/images/logo.png'
    	backgroung_image_path = './pos/static/images/bg.png'
    	facture_path = './pos/static/factures/facture.pdf'
    elif platform.system() == "Windows":
    	home_dir = str(Path.home())
    	logo_path = f"{home_dir}/ALPOS-dev/pos/static/images/logo.png".replace("\\", "//")
    	backgroung_image_path = f"{home_dir}/ALPOS-dev/pos/static/images/bg.png".replace("\\", "//")
    	facture_path = f"{home_dir}/ALPOS-dev/pos/static/factures/facture.pdf".replace("\\", "//")
    
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    canvas = Canvas(facture_path)

    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    heure = str(datetime.now()).split(' ')[1].split('.')[0]
    
    
    #logo
    x = 240
    y = 720
    canvas.drawImage(logo, x, y, width=100, height=100, mask='auto')

    #entreprise
    canvas.setFont('Helvetica-Bold', 50)
    x = 75
    y = 700
    canvas.drawString(x, y, f"{entreprise}")

    #date
    canvas.setFont('Helvetica', 20)
    x = 200
    y = 670
    canvas.drawString(x, y, f"Date: {date_fr} {heure}")


    #tableau
    data= [['Article', 'Qte', 'PU']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = article["quantite"]*float(article["prix"])
        total = total + st
        data.append([article["article"], article["quantite"], float(article["prix"])])

    #table=Table(data, colWidths='*')
    table=Table(data, colWidths=[350, 70, 100])
    table.setStyle(
        TableStyle(
            [
                ('FONTSIZE',(0,0),(-1,-1), 20),
                ('TEXTFONT',(0,0),(-1,-1), 'Times-Bold'),
                ('ALIGN',(1,1),(-1,-1),'RIGHT'),
                #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                #('BOX', (0,0), (-1,-1), 0.25, colors.black), 
            ]
        )
    )

    #table = Table(data, )
    x = 30
    y = y-20*len(data)
    table.wrapOn(canvas, letter[0]-150, letter[1])
    table.drawOn(canvas, x, y)


    #total 
    x = letter[0]-240
    y = y-70
    canvas.setFont('Helvetica-Bold', 20)
    canvas.drawString(x, y, f"Total: {total} fcfa")

    canvas.setFont('Helvetica', 20)
    x = 170
    y = 40
    canvas.drawString(x, y, f"www.logoba-agriculture.com")
    x = 100
    y = 15
    canvas.drawString(x, y, f"(+226) 20971525 / 71320233 / 78850032")

    canvas.showPage()
    canvas.save()
