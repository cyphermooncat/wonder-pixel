import base64
import json
from PIL import Image
import numpy as np
import datetime
import logging
import sys 

# Configurer les logs
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

import numpy as np
from PIL import Image
import logging

def read_colormap(file_path):
    colormap = {}
    with open(file_path, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            index = int(parts[0])
            # Suppression des crochets et conversion des valeurs RGB en entiers
            color = tuple(map(int, parts[1].strip('[]').split()))
            name = parts[2].strip('"')
            colormap[color] = index
    return colormap

def find_closest_color(color, colormap):
    # Convert color to numpy array for vectorized operations
    color = np.array(color)
    min_dist = float('inf')
    closest_color_index = None
    for cmap_color, index in colormap.items():
        cmap_color = np.array(cmap_color)
        dist = np.linalg.norm(color - cmap_color)
        if dist < min_dist:
            min_dist = dist
            closest_color_index = index
    return closest_color_index

def get_palette(image_path, colormap_path):
    logging.info("!!! Ouverture de l'image qui DOIT ETRE EN 128*128 avec 8 couleurs uniquement en premier argument du script python")
    img = Image.open(image_path)
    img = img.convert("RGB")  # Assurer que l'image est en mode RGB
    data = np.array(img)
    
    logging.info("Lecture du fichier de correspondance des couleurs.")
    colormap = read_colormap(colormap_path)
    
    logging.info("Recherche des couleurs uniques dans l'image.")
    unique_colors, counts = np.unique(data.reshape(-1, data.shape[-1]), axis=0, return_counts=True)
    unique_colors = [tuple(color) for color in unique_colors if tuple(color) != (255, 255, 255)]
    
    logging.info("Conversion des couleurs en indices de la table de correspondance.")
    palette = {}
    for color in unique_colors:
        if color in colormap:
            palette[color] = colormap[color]
        else:
            logging.warning(f"Couleur {color} non trouvée dans la table de correspondance. Recherche de la couleur la plus proche.")
            closest_color_index = find_closest_color(color, colormap)
            palette[color] = closest_color_index
    
    return palette, data

# Exemple d'utilisation
image_path = sys.argv[1]
colormap_path = 'colormap3.txt'
palette, data = get_palette(image_path, colormap_path)

palette2 = [None]
palette2.extend(palette.values())
print("palette2:", palette2)


def transform_image_to_array(image_data, palette):
    result = []
    color_index = {tuple(color): idx for idx, color in enumerate(palette)}
    
    logging.info("Transformation des données de l'image en tableau.")
    for y in range(image_data.shape[0]):
        for x in range(image_data.shape[1]):
            pixel_color = tuple(image_data[y, x])
            if pixel_color == (255, 255, 255):
                continue  # Ignorer le blanc
            color_idx = color_index[pixel_color]
            result.append([x, y, color_idx + 1])
    
    result.sort(key=lambda p: (p[0], p[1]))
    return result

# Chemin de l'image
image_path = sys.argv[1]

# Obtenir la palette et les données de l'image
logging.info("Obtention de la palette et des données de l'image.")
palette, image_data = get_palette(image_path, colormap_path)

# Transformer l'image en tableau avec positions et index de couleur
logging.info("Transformation de l'image en tableau avec positions et index de couleur.")
transformed_array = transform_image_to_array(image_data, palette)

# Sauvegarder le tableau dans le fichier tableaufinal.txt
logging.info("Sauvegarde du tableau dans le fichier tableaufinal.txt.")
with open('tableaufinal.txt', 'w') as f:
    json.dump(transformed_array, f)

# Encoder l'image en base64
logging.info("Encodage de l'image en base64.")
with open(image_path, 'rb') as img_file:
    img_base64 = base64.b64encode(img_file.read()).decode('utf-8')

# Lire le contenu du fichier import
logging.info("Lecture du contenu du fichier fichierimport.txt.")
with open('fichierimport.txt', 'r') as file:
    content = file.read()

# Obtenir le timestamp actuel
timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
logging.info(f"Timestamp actuel: {timestamp}")

# Lire le contenu de tableaufinal.txt
logging.info("Lecture du contenu de tableaufinal.txt.")
with open('tableaufinal.txt', 'r') as f:
    tableaucode = f.read()

# Remplacer les valeurs dans le contenu
logging.info("Remplacement des valeurs dans le contenu du fichier import.")
content = content.replace('nomfichier', f'nomfichier_{timestamp}')
logging.debug(f"Contenu après remplacement de nomfichier: {content}")

content = content.replace('codebase', img_base64)
logging.debug(f"Contenu après remplacement de codebase: {content[:500]}...")  # Afficher seulement les premiers 500 caractères

content = content.replace('tableaucode', tableaucode)
logging.debug(f"Contenu après remplacement de tableaucode: {content[:500]}...")  # Afficher seulement les premiers 500 caractères

palette2str = str(palette2)

content = content.replace('palettefinal', palette2str)
logging.debug(f"Contenu après remplacement de palette: {content[:500]}...")  # Afficher seulement les premiers 500 caractères

content = content.replace('None', "null")
logging.debug(f"Contenu après remplacement de palette: {content[:500]}...")  # Afficher seulement les premiers 500 caractères

# Sauvegarder le contenu modifié dans fichierimport.txt
logging.info("Sauvegarde du fichier import après modification.")
with open('fichierimportnew.txt', 'w') as file:
    file.write(content)

# Encoder le contenu modifié en base64
logging.info("Encodage du contenu modifié en base64.")
encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

# Sauvegarder le contenu encodé en base64 dans fichierimportbase64.txt
logging.info("Sauvegarde du contenu encodé en base64 dans fichierimportbase64.txt.")
with open('fichierimportbase64.txt', 'w') as f:
    f.write(encoded_content)

logging.info("Processus terminé !! COPIE COLLE fichierimportbase64 dans MOONCAT DESIGNER IMPORT")
