from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen.canvas import Canvas
from reportlab.lib.utils import ImageReader
from datetime import datetime, date
from reportlab.platypus import Image, Table, Paragraph
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle, StyleSheet1
import json
import platform
from pathlib import Path
import os



styles = getSampleStyleSheet()
styles["BodyText"].fontSize = 25 #taillle caractère elements du tableau
styleN = styles["BodyText"]

entreprise = "BOUTIQUE DE LA PROXIMITÉ"
tel1 = "+22656848320"
tel2 = "+22677540940"
tel3 = ""
tel4 = ""
mail = ""

ville = "Bobo-Dioulasso"
pays = "Burkina-Faso"

def recu_paiement_avance(liste_articles_a_vendre, client):
    draw_backgroung_image = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'logo.png')
    backgroung_image_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'bg.png')
    facture_path = os.path.join(BASE_DIR, 'pos', 'static', 'factures', 'facture.pdf')
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    
    canvas = Canvas(facture_path)
    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    if draw_backgroung_image:
        canvas.drawImage(backgroung_image, 0, 0, width=letter[0], height=letter[1]+100, mask="auto")
    #.drawImage(logo, 70, 710, width=100, height=100, mask='auto')
    canvas.setFont('Helvetica', 13)
    x = letter[0]-70-100-5
    y = 800
    canvas.drawString(x, y, f"Date: {date_fr}")
    canvas.setFont('Helvetica-Bold', 15)
    x = 200
    y = 790  # 777
    canvas.drawString(x, y, f"{entreprise}")
    x = letter[0]-70-100-29
    y = 777-20+10
    canvas.setFont('Helvetica', 13)
    #canvas.drawString(x, y, f"Ville: {ville}")
    x = letter[0]-70-100-20
    y = y-18
    #canvas.drawString(x, y, f"Pays: {pays}")
    x = letter[0]-70-100-20
    y = y-18
    #canvas.drawString(x, y, f"Tel: {tel1}")
    y = y-18
    #canvas.drawString(x, y, f"Tel: {tel2}")
    x_desc = 230
    y_desc = 767
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x_desc, y_desc, f"Vente de marchandises divers")
    x_desc = 200
    y_desc = 753
    canvas.drawString(x_desc, y_desc, f"Sis à Bobo-Dioulasso face Immeuble Kadhafi")
    '''
    x_desc = 200
    y_desc = y_desc-13
    canvas.drawString(x_desc, y_desc, f"Ingénieurs conseils, etc...")
    '''
    canvas.setFont('Helvetica-Bold', 20)
    x = 70
    y = y-30
    canvas.drawString(x, y, "RECU DE VERSEMENT")
    data = [['Désignation', 'Quantite', 'Prix Unitaire', 'Montant']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = int(article["quantite"])*float(article["prix"])
        total = total + st
        data.append([article["article"], article["quantite"],
                     float(article["prix"]), st])
    table = Table(data, colWidths='*')
    table.setStyle(
        TableStyle(
            [
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    x = 70
    y = y-20*len(data)-50
    table.wrapOn(canvas, letter[0]-150, letter[1])
    table.drawOn(canvas, x, y)
    x = letter[0]-70-100-5
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Total: {total} fcfa")
    
    
    x = 70
    y = y-40
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x, y, "Le Client")
    #canvas.line(x, y-5, x+90, y-5)
    y = y-20
    canvas.setFont('Helvetica', 13)
    if client.nom != 'default':
        canvas.drawString(x, y, f'{client.prenoms} {client.nom}')
    else:
        canvas.drawString(x, y, f'défaut')
     
    
    x = letter[0]-70-100-5
    y = y+20
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x, y, "Le Vendeur")
    #canvas.line(x, y-5, x+90, y-5)
    '''
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f'AMADOU SAMA')
    '''
    
    canvas.setFont('Helvetica', 20)
    x = 200
    y = y-100
    canvas.drawString(x, y, f"Merci et à bientôt")
    
    x = 70
    y = 30
    canvas.line(x, y, x+letter[0]-150, y)
    canvas.setFont('Helvetica', 10)
    x = 140
    y = y-20
    #canvas.drawString(x, y, f'RC : BF BBD 2016 A 0958    -   IFU : 00077127N   -   COMPTE ECOBANK N°170401709001')
    canvas.drawString(x, y, f'{tel1}         -         {tel2}         -         {tel3}')

    canvas.showPage()
    canvas.save()


def enregistrer_proforma(liste_articles_a_vendre, client, objet_facture):
    draw_backgroung_image = False
    logo_path = ""
    backgroung_image_path = ""
    facture_path = ""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'logo.png')
    backgroung_image_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'bg.png')
    facture_path = os.path.join(BASE_DIR, 'pos', 'static', 'factures', 'proforma.pdf')
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    canvas = Canvas(facture_path)
    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    if draw_backgroung_image:
        canvas.drawImage(backgroung_image, 0, 0, width=letter[0], height=letter[1]+100, mask="auto")
    """
    canvas.drawImage(logo, 70, 710, width=100, height=100, mask='auto')
    """
    canvas.setFont('Helvetica', 13)
    x = letter[0]-70-100-5
    y = 800
    canvas.drawString(x, y, f"Date: {date_fr}")
    canvas.setFont('Helvetica-Bold', 35)
    x = 70
    y = 760  # 777
    canvas.drawString(x, y, f"{entreprise}")
    x = letter[0]-70-100-29
    y = 777-20+10
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Ville: {ville}")
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Pays: {pays}")
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel1}")
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel2}")
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel3}")
    
    x_desc = 175
    y_desc = 767
    """
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x_desc, y_desc, f"Fournitures Scolaire, bureautique, emballage cadeau")
    x_desc = 180
    y_desc = 753
    canvas.drawString(x_desc, y_desc, f"Consommables informatique, produits d'entretien")
    x_desc = 200
    y_desc = y_desc-13
    canvas.drawString(x_desc, y_desc, f"service location et service divers")
    """
    canvas.setFont('Helvetica-Bold', 20)
    x = 70
    y = y-30
    canvas.drawString(x, y, "FACTURE PROFORMA")

    x = 70
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Doit: {client.prenoms} {client.nom}")

    x = 70
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Objet: {objet_facture}")

    data = [['Désignation', 'Quantite', 'Prix Unitaire', 'Montant']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = int(article["quantite"])*float(article["prix"])
        total = total + st
        data.append([article["article"], article["quantite"],
                     float(article["prix"]), st])
    table = Table(data, colWidths='*')
    table.setStyle(
        TableStyle(
            [
                ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
                ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
            ]
        )
    )
    x = 70
    y = y-20*len(data)-50
    table.wrapOn(canvas, letter[0]-150, letter[1])
    table.drawOn(canvas, x, y)
    x = letter[0]-70-100-5
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Total: {total} fcfa")

    x = 100
    y = y-20
    canvas.drawString(x, y, f'Arreté la présente facture proforma à la somme de {total} francs fcfa HT')
    

    x = letter[0]-70-100-5
    y = y-40
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, "Le Responsable")
    canvas.line(x, y-5, x+90, y-5)
    
    """
    y = y-20
    canvas.drawString(x, y, f'ZONGO LAZARE')
    """
    canvas.setFont('Helvetica', 20)
    x = 200
    y = y-70
    """
    canvas.drawString(x, y, f"Merci et à bientôt")
    x = 70
    y = 30
    canvas.line(x, y, x+letter[0]-150, y)
    canvas.setFont('Helvetica', 10)
    x = 90
    y = y-20
    canvas.drawString(x, y, f'RC : BF BBD 2016 A 0958    -   IFU : 00077127N   -   COMPTE ECOBANK N°170401709001')
    """
    canvas.showPage()
    canvas.save()


def enregistrer_recu_type2(liste_articles_a_vendre, montant_encaisse, monnaie_rendue):#termique
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'logo.png')
    backgroung_image_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'bg.png')
    facture_path = os.path.join(BASE_DIR, 'pos', 'static', 'factures', 'facture.pdf')
    
    canvas = Canvas(facture_path)

    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    heure = str(datetime.now()).split(' ')[1].split('.')[0]

    # logo
    '''
    x = 240
    y = 720
    canvas.drawImage(logo, x, y, width=100, height=100, mask='auto')
    '''

    # entreprise
    canvas.setFont('Helvetica-Bold', 40)
    x = 150
    y = 750
    canvas.drawString(x, y, f"{entreprise}")
    
    # date
    canvas.setFont('Helvetica', 20)
    x = 175
    y = y - 30
    canvas.drawString(x, y, f"Date: {date_fr} {heure}")

    # tableau
    data = [['Désignation', 'Qte', 'PU', 'Montant']]
    st = 0
    total = 0
    data.append([])#saut de ligne apres les entetes du tableau sur le recu
    for article in json.loads(liste_articles_a_vendre):
        st = float(article["quantite"])*float(article["prix"])
        total = total + st
        
        nom_article = Paragraph(article["article"], styleN)
        qte_article = Paragraph(str(article["quantite"]), styleN)
        prix_article = Paragraph(str(float(article["prix"])), styleN)
        sous_total = Paragraph(str(float(article["prix"])*float(article["quantite"])), styleN)
        
        data.append([nom_article, qte_article, prix_article, sous_total])
        #data.append([])#saut de ligne dans le tableau sur le recu

    #######################################################################
    # keep track of the data we have left to draw
    data_left = data

    fist_page = True
    while data_left:
        rows_per_page = 22 if fist_page else 30
        table_data = data_left[:rows_per_page]
        data_left = data_left[rows_per_page:]


        # adjust the size of the table cells
        table = Table(table_data, colWidths=[300, 70, 100], rowHeights=30)

        table.setStyle(
            TableStyle(
                [
                    ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
                    ('TEXTFONT', (0, 0), (-1, -1), 'Times-Bold'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'), # police pour l'entête du tableau
                    ('FONTSIZE', (0, 0), (-1, -1), 25), # taille de la police pour le tableau
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # police pour le contenu du tableau
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
                ]
            )
        )

        x = 30
        y = y-20*len(table_data)-50-10*len(table_data)
        table.wrapOn(canvas, letter[0]-150, letter[1])
        table.drawOn(canvas, x, y)

        # If there's still data left to draw, start a new page
        if data_left:
            canvas.showPage()
            #y = 800  # Reset y to the top of the page
            y = 800
    
    ###################################################################################
    """
    table = Table(data, colWidths=[300, 70, 100])
    table.setStyle(
        TableStyle(
            [
                ('FONTSIZE', (0, 0), (-1, -1), 20),
                ('TEXTFONT', (0, 0), (-1, -1), 'Times-Bold'),
                ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
                #('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
                #('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ]
        )
    )

    #table = Table(data, )
    x = 30
    y = y-20*len(data)*1.2
    table.wrapOn(canvas, letter[0]-150, letter[1])
    table.drawOn(canvas, x, y)
    """
    # total
    x = letter[0]-240
    y = y-70
    if y <= 100:
        canvas.showPage()
        y = 800
    canvas.setFont('Helvetica-Bold', 25)
    canvas.drawString(x, y, f"Total: {total} fcfa")

    #montant encaisse
    #x = letter[0]-240
    x = 30
    y = y-80
    canvas.setFont('Helvetica-Bold', 25)
    canvas.drawString(x, y, f"Montant encaisse: {montant_encaisse} fcfa")
    #monnaie rendue
    #x = letter[0]-240
    x = 30
    y = y-20
    canvas.setFont('Helvetica-Bold', 25)
    canvas.drawString(x, y, f"Monnaie Rendue: {monnaie_rendue} fcfa")

    canvas.setFont('Helvetica', 25)
    x = 200
    y = y-20
    canvas.drawString(x, y, f"{mail}")
    x = 250
    y = y-20
    #canvas.drawString(x, y, f"(+226) {tel1} / {tel2} / {tel3}")
    canvas.drawString(x, y, f" {tel1}")

    canvas.showPage()
    canvas.save()


# avec FORMAT A4 LOGO
def _enregistrer_recu_type1(liste_articles_a_vendre, client):

    draw_backgroung_image = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'logo.png')
    backgroung_image_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'bg.png')
    facture_path = os.path.join(BASE_DIR, 'pos', 'static', 'factures', 'facture.pdf')
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    
    canvas = Canvas(facture_path)
    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    if draw_backgroung_image:
        canvas.drawImage(backgroung_image, 0, 0, width=letter[0], height=letter[1]+100, mask="auto")
    canvas.drawImage(logo, 70, 710, width=100, height=100, mask='auto')
    canvas.setFont('Helvetica', 13)
    x = letter[0]-70-100-5
    y = 800
    canvas.drawString(x, y, f"Date: {date_fr}")
    canvas.setFont('Helvetica-Bold', 15)
    x = 200
    y = 790  # 777
    canvas.drawString(x, y, f"{entreprise}")
    x = letter[0]-70-100-29
    y = 777-20+10
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f"Ville: {ville}")
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Pays: {pays}")
    x = letter[0]-70-100-20
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel1}")
    y = y-18
    canvas.drawString(x, y, f"Tel: {tel2}")
    x_desc = 180
    y_desc = 767
    canvas.setFont('Helvetica', 10)
    canvas.drawString(x_desc, y_desc, f"RCCM N° BFBBD2021A1170 - IFU N°00163308N")
    '''
    x_desc = 230
    y_desc = 753
    canvas.drawString(x_desc, y_desc, f"du Burkina-Faso")
    x_desc = 200
    y_desc = y_desc-13
    canvas.drawString(x_desc, y_desc, f"Ingénieurs conseils, etc...")
    '''
    canvas.setFont('Helvetica-Bold', 20)
    x = 70
    y = y-30
    canvas.drawString(x, y, "FACTURE")

    ###DEBUT NOUVEAU
    canvas.setFont('Helvetica', 15)  # augmenter à 15

    data = [['Désignation', 'Qte', 'P.U', 'Montant']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = int(article["quantite"])*float(article["prix"])
        total = total + st
        data.append([article["article"], article["quantite"],
                    float(article["prix"]), st])

    
    # keep track of the data we have left to draw
    data_left = data

    fist_page = True
    while data_left:
        rows_per_page = 16 if fist_page else 21
        table_data = data_left[:rows_per_page]
        data_left = data_left[rows_per_page:]

        # adjust the size of the table cells
        table = Table(table_data, colWidths=[200, 70, 100], rowHeights=40)

        table.setStyle(
            TableStyle(
                [
                    ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if fist_page else 'Helvetica'), # police pour l'entête du tableau
                    ('FONTSIZE', (0, 0), (-1, -1), 20), # taille de la police pour le tableau
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # police pour le contenu du tableau
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                ]
            )
        )

        x = 70
        y = y-20*len(table_data)-50-18*len(table_data)
        table.wrapOn(canvas, letter[0]-150, letter[1])
        table.drawOn(canvas, x, y)
        
        fist_page = False

        # If there's still data left to draw, start a new page
        if data_left:
            canvas.showPage()
            #y = 800  # Reset y to the top of the page
            y = 850

    ###FIN NOUVEAU
    
    x = letter[0]-70-100-5-30
    y = y-20
    if y <= 100:
        canvas.showPage()
        y = 800
        print(f"{y} total")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, f"Total: {total} fcfa")
    
    
    x = 70
    y = y-40
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} le client")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, "Le Client")
    #canvas.line(x, y-5, x+90, y-5)
    y = y-20
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} nom prenom client")
    canvas.setFont('Helvetica', 20)
    if client.nom != 'default':
        canvas.drawString(x, y, f'{client.prenoms} {client.nom}')
    
    
    x = letter[0]-70-100-5
    y = y+20
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} le vendeur")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, "Le Vendeur")
    #canvas.line(x, y-5, x+90, y-5)
    '''
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f'AMADOU SAMA')
    '''
    
    canvas.setFont('Helvetica', 20)
    x = 200
    y = y-100
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} merci et a biento")
    canvas.drawString(x, y, f"Merci et à bientôt")
    '''
    x = 70
    y = 30
    canvas.line(x, y, x+letter[0]-150, y)
    canvas.setFont('Helvetica', 10)
    x = 90
    y = y-20
    canvas.drawString(x, y, f'RC : BF BBD 2016 A 0958    -   IFU : 00077127N   -   COMPTE ECOBANK N°170401709001')
    '''
    canvas.showPage()
    canvas.save()


# avec FORMAT A4 Sans LOGO
def enregistrer_recu_type1(liste_articles_a_vendre, client):

    draw_backgroung_image = False
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logo_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'logo.png')
    backgroung_image_path = os.path.join(BASE_DIR, 'pos', 'static', 'images', 'bg.png')
    facture_path = os.path.join(BASE_DIR, 'pos', 'static', 'factures', 'facture.pdf')
    logo = ImageReader(logo_path)
    backgroung_image = ImageReader(backgroung_image_path)
    
    canvas = Canvas(facture_path)
    d = str(datetime.now())
    d = d.split(" ")[0]
    annee = d.split("-")[0]
    mois = d.split("-")[1]
    jour = d.split("-")[2]
    date_fr = "{}/{}/{}".format(jour, mois, annee)
    if draw_backgroung_image:
        canvas.drawImage(backgroung_image, 0, 0, width=letter[0], height=letter[1]+100, mask="auto")

    canvas.setFont('Helvetica', 20)
    x = letter[0]-180
    y = 800
    canvas.drawString(x, y, f"Date: {date_fr}")

    canvas.setFont('Helvetica-Bold', 20)
    x = 70
    y = 750  # 777
    canvas.drawString(x, y, f"{entreprise}")

    x = letter[0]-210
    y = 777-20+10
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, f"Ville: {ville}")
    x = letter[0]-210
    y = y-20
    canvas.drawString(x, y, f"Pays: {pays}")
    x = letter[0]-210
    y = y-20
    canvas.drawString(x, y, f"Tel: {tel1}")
    y = y-20
    canvas.drawString(x, y, f"Tel: {tel2}")
    x_desc = 180
    y_desc = 767
    canvas.setFont('Helvetica', 10)
    #canvas.drawString(x_desc, y_desc, f"RCCM N° BFBBD2021A1170 - IFU N°00163308N")
    '''
    x_desc = 230
    y_desc = 753
    canvas.drawString(x_desc, y_desc, f"du Burkina-Faso")
    x_desc = 200
    y_desc = y_desc-13
    canvas.drawString(x_desc, y_desc, f"Ingénieurs conseils, etc...")
    '''
    canvas.setFont('Helvetica-Bold', 20)
    x = 70
    y = y-30
    canvas.drawString(x, y, "RECU")

    ###DEBUT NOUVEAU
    canvas.setFont('Helvetica', 15)  # augmenter à 15

    data = [['Désignation', 'Qte', 'P.U', 'Montant']]
    st = 0
    total = 0
    for article in json.loads(liste_articles_a_vendre):
        st = int(article["quantite"])*float(article["prix"])
        total = total + st
        truncated_article_name = article["article"][:20]
        data.append([f"{truncated_article_name}...", article["quantite"],
                    float(article["prix"]), st])

    
    # keep track of the data we have left to draw
    data_left = data

    fist_page = True
    while data_left:
        rows_per_page = 16 if fist_page else 21
        table_data = data_left[:rows_per_page]
        data_left = data_left[rows_per_page:]

        # adjust the size of the table cells
        table = Table(table_data, colWidths=[300, 70, 100], rowHeights=40)

        table.setStyle(
            TableStyle(
                [
                    ('ALIGN', (1, 1), (-1, -1), 'LEFT'),
                    ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ('BOX', (0, 0), (-1, -1), 0.25, colors.black),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold' if fist_page else 'Helvetica'), # police pour l'entête du tableau
                    ('FONTSIZE', (0, 0), (-1, -1), 20), # taille de la police pour le tableau
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'), # police pour le contenu du tableau
                    ('LEFTPADDING', (0, 0), (-1, -1), 10),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 10),
                    ('TOPPADDING', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 14),
                ]
            )
        )

        x = 10
        y = y-20*len(table_data)-50-18*len(table_data)
        table.wrapOn(canvas, letter[0]-150, letter[1])
        table.drawOn(canvas, x, y)
        
        fist_page = False

        # If there's still data left to draw, start a new page
        if data_left:
            canvas.showPage()
            #y = 800  # Reset y to the top of the page
            y = 850

    ###FIN NOUVEAU
    
    x = letter[0]-70-100-5-30
    y = y-20
    if y <= 100:
        canvas.showPage()
        y = 800
        print(f"{y} total")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, f"Total: {total} fcfa")
    
    
    x = 70
    y = y-40
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} le client")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, "Le Client")
    #canvas.line(x, y-5, x+90, y-5)
    y = y-20
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} nom prenom client")
    canvas.setFont('Helvetica', 20)
    if client.nom != 'default':
        canvas.drawString(x, y, f'{client.prenoms} {client.nom}')
    
    
    x = letter[0]-70-100-5
    y = y+20
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} le vendeur")
    canvas.setFont('Helvetica', 20)
    canvas.drawString(x, y, "Le Vendeur")
    #canvas.line(x, y-5, x+90, y-5)
    '''
    y = y-20
    canvas.setFont('Helvetica', 13)
    canvas.drawString(x, y, f'AMADOU SAMA')
    '''
    
    canvas.setFont('Helvetica', 20)
    x = 200
    y = y-100
    if y < 100:
        canvas.showPage()
        y = 800
        print(f"{y} merci et a biento")
    canvas.drawString(x, y, f"Merci et à bientôt")
    '''
    x = 70
    y = 30
    canvas.line(x, y, x+letter[0]-150, y)
    canvas.setFont('Helvetica', 10)
    x = 90
    y = y-20
    canvas.drawString(x, y, f'RC : BF BBD 2016 A 0958    -   IFU : 00077127N   -   COMPTE ECOBANK N°170401709001')
    '''
    canvas.showPage()
    canvas.save()
