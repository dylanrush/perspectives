# Dylan Rush 2019
# Provided only for personal or educational use
# Commercial use prohibited

from perspectives import *
from PIL import Image, ImageDraw
from itertools import permutations
from shutil import copyfile

point_finder = Perspectives.find_corner_centroid

dir = "debugging7"
with open("images/A_Sunday_on_La_Grande_Jatte.png", "rb") as template_fp:
    template_im = Image.open(template_fp)
    with open(dir+"/image_base.jpg", "rb") as fp1:
        im1 = Image.open(fp1)
        im_draw = Image.open(fp1)
        draw = ImageDraw.Draw(im_draw)
        corner_coords = []
        image_last = im1
        for corner in ['top-left', 'top-right', 'bottom-right', 'bottom-left']:
            with open(dir+"/image_corner_"+corner+".jpg", "rb") as fp2:
                im2 = Image.open(fp2)
                diff_value = Perspectives.img_diff(image_last, im2)
                print("Diff value: "+str(diff_value))
                image_last = im2
                corner_coords.append(point_finder(im1, im2, 85, True))
                for appendix in ["", "_before_thresh", "_after_thresh"]:
                    copyfile("debugging/diff"+appendix+".jpg", dir + "/" + "diff_" + corner + appendix + ".jpg")
        corner_coords = Perspectives.zoom_corners(corner_coords, 1.15)
        for corner in corner_coords:
            (x, y) = corner
            draw.ellipse([x - 2, y - 2, x + 2, y + 2], fill=(255, 255, 255, 255))
        im_draw.save(dir+"/points.jpg", "JPEG")
        template_coords = []
        for corner in corner_coords:
            template_coords.append(Perspectives.letterbox(corner, im1.size, template_im.size))
        kindle_image = Perspectives.kindle_transform(template_im, (600, 800),
                                                     template_coords)
        kindle_image.save(dir+"/kindle-output.png", "PNG")