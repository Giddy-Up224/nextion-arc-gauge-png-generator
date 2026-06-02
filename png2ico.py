from PIL import Image
filename = 'img/Arcy.png'
img = Image.open(filename)
img.save('img/Arcy.ico')