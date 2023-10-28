from PIL import Image
 
# creating a image object
im = Image.open("frontend\public\maps\kohat_heightmap.png")
buf = im.load()

target = buf[1934, 2010]
print (target)
target = (target[0] << 8) + target[1]
print(target)
print(target * 0.75)
print(target * 0.75 * 0.75)

weapon = buf[1515, 3282]
print (weapon)
weapon = (weapon[0] << 8) + weapon[1]
print(weapon)
print(weapon * 0.75)
print(weapon * 0.75 * 0.75)


print("--")
print((weapon - target))
print((weapon - target) * 0.75)
print((weapon - target) * 0.75 * 0.75)
print((weapon - target) * 0.75/13000)

im = Image.open("kohat_heightmap_raw.png")
buf = im.load()
print("raw")
pixel = buf[1515, 3282]
print (pixel)

print(pixel * 0.75)
print(pixel * 0.75 * 0.75)