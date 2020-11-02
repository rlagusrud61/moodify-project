import colorsys
from colr import color

if __name__ == '__main__':
    for i in range(0, 360, 1):
        colour_tuple = colorsys.hsv_to_rgb(i/360, 1, 1)
        colours = []
        for hex in colour_tuple:
            hex = int(hex*255)
            colours.append(hex)
        # print(colours)
        print(color("WOO", back=tuple(colours)))
