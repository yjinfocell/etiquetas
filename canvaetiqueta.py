import pandas as pd
from PIL import Image, ImageDraw, ImageFont
from reportlab.pdfgen import canvas
import os

# Função auxiliar para adicionar quebras de linha a cada duas palavras
def adicionar_quebra_de_linha(texto):
    palavras = texto.split()
    linhas = []
    for i in range(0, len(palavras), 2):
        linhas.append(' '.join(palavras[i:i + 2]))
    return '\n'.join(linhas)

# Função para determinar a posição X do texto varejo com base na quantidade de dígitos
def calcular_posicao_x(preco):
    preco_str = str(preco)
    num_digitos = len(preco_str)
    if num_digitos == 1:
        return 320
    elif num_digitos == 2:
        return 310
    elif num_digitos == 3:
        return 300
    else:
        return 290

# Função para criar uma imagem a partir de uma linha do DataFrame usando uma imagem base
def criar_imagem(nome, referencia, varejo, fonte_nome, fonte_referencia, fonte_varejo, imagem_base, output_path):
    imagem = Image.open(imagem_base)
    draw = ImageDraw.Draw(imagem)

    # Definindo as fontes
    font_nome = ImageFont.truetype("Montserrat-Bold.ttf", fonte_nome)
    font_referencia = ImageFont.truetype("Montserrat-Bold.ttf", fonte_referencia)
    font_varejo = ImageFont.truetype("Montserrat-Bold.ttf", fonte_varejo)
    font_varejo_menor = ImageFont.truetype("Montserrat-Bold.ttf", int(fonte_varejo * 0.4))

    # Adicionando quebras de linha ao nome
    nome_com_quebras = adicionar_quebra_de_linha(nome)

    # Calculando a posição X do texto varejo
    posicao_x_varejo = calcular_posicao_x(varejo)

    # Adicionando ,00 ao varejo
    varejo_str = str(varejo)
    varejo_completo = varejo_str + ",00"

    # Desenhando o texto na imagem
    draw.text((40, 20), nome_com_quebras, font=font_nome, fill='black')
    draw.text((700, 500), referencia, font=font_referencia, fill='black')
    
    # Desenhando o preço e ,00 separadamente
    draw.text((posicao_x_varejo, 700), varejo_str, font=font_varejo, fill='black')
    bbox = draw.textbbox((posicao_x_varejo, 700), varejo_str, font=font_varejo)
    largura_preco = bbox[2] - bbox[0]
    draw.text((posicao_x_varejo + largura_preco, 900), ",00", font=font_varejo_menor, fill='black')

    imagem.save(output_path)

# Função para criar uma colagem de imagens
def create_collage(images, output_path):
    rows = 6
    cols = 3
    collage_width = max(img.width for img in images) * cols
    collage_height = max(img.height for img in images) * rows

    collage = Image.new('RGB', (collage_width, collage_height), color='white')

    for i, img in enumerate(images):
        x_offset = (i % cols) * img.width
        y_offset = (i // cols) * img.height
        collage.paste(img, (x_offset, y_offset))

    collage.save(output_path)

# Função para criar um PDF a partir de colagens de imagens
def create_pdf(collage_paths, output_pdf_path):
    first_collage = Image.open(collage_paths[0])
    pdf_width, pdf_height = first_collage.size

    c = canvas.Canvas(output_pdf_path, pagesize=(pdf_width, pdf_height))

    for collage_path in collage_paths:
        c.drawInlineImage(collage_path, 0, 0, width=pdf_width, height=pdf_height)
        c.showPage()

    c.save()

# Função principal para gerar imagens, colagens e o PDF final
def main():
    df = pd.read_csv('nova_planilha.csv', encoding='latin1')
    tamanho_fonte_nome = 90
    tamanho_fonte_referencia = 150
    tamanho_fonte_varejo = 450
    imagem_base = 'aa.png'
    output_folder = r'A:\testes impressora\criador etiquetas do canva'
    output_pdf_path = os.path.join(output_folder, "output.pdf")

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    image_paths = []
    for index, row in df.iterrows():
        output_path = os.path.join(output_folder, f"imagem_{index}.png")
        criar_imagem(
            row['nome'], 
            row['referencia'], 
            row['varejo'],
            tamanho_fonte_nome, 
            tamanho_fonte_referencia, 
            tamanho_fonte_varejo,
            imagem_base,
            output_path
        )
        image_paths.append(output_path)

    collage_paths = []
    collage_groups = [image_paths[i:i+18] for i in range(0, len(image_paths), 18)]
    for i, group in enumerate(collage_groups):
        collage_path = os.path.join(output_folder, f"3x6_{i + 1}.png")
        collage_images = [Image.open(img_path) for img_path in group]
        create_collage(collage_images, collage_path)
        collage_paths.append(collage_path)

    create_pdf(collage_paths, output_pdf_path)

if __name__ == "__main__":
    main()
