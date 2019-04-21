# Dylan Rush 2019
# Provided only for personal or educational use
# Commercial use prohibited


import numpy
from PIL import Image, ImageOps, ImageFilter
import time
import subprocess

class Perspectives:
    def __init__(self, template_image, camera_res, hosts, cam_fn, corner_thresh, diff_thresh,
                 find_corner_fn, save_debug_photos=False):
        self.template_image = template_image
        self.camera_res = camera_res
        self.hosts = hosts
        self.get_pil_snapshot = cam_fn
        self.diff_thresh = diff_thresh
        self.corner_thresh = corner_thresh
        self.find_corner_fn = find_corner_fn
        self.save_debug_photos = save_debug_photos

    def set_template_image(self, template_image):
        self.template_image = template_image

    @staticmethod
    def find_coeffs(target_coords, source_coords):
        matrix = []
        for s, t in zip(source_coords, target_coords):
            matrix.append([t[0], t[1], 1, 0, 0, 0, -s[0]*t[0], -s[0]*t[1]])
            matrix.append([0, 0, 0, t[0], t[1], 1, -s[1]*t[0], -s[1]*t[1]])
        A = numpy.matrix(matrix, dtype=numpy.float)
        B = numpy.array(source_coords).reshape(8)
        res = numpy.dot(numpy.linalg.inv(A.T * A) * A.T, B)
        return numpy.array(res).reshape(8)

    #coords from the painting. white as background. looks like:
    # [(-30, -30), (400, -30), (400, 900), (-30, 900)]
    @staticmethod
    def kindle_transform(template_image, resolution, coords):
        kindle_width, kindle_height = resolution
        coeffs = Perspectives.find_coeffs(
            [(0, 0), (kindle_width, 0), (kindle_width, kindle_height), (0, kindle_height)],
            coords)
        return ImageOps.invert(ImageOps.invert(template_image).transform((kindle_width, kindle_height), Image.PERSPECTIVE, coeffs,
                           Image.BICUBIC).convert("L"))

    # Returns corner relative to camera (int, int)
    @staticmethod
    def find_corner_centroid(image_base, image_corner, thresh, save_debug_photos=False):
        image_base = numpy.array(image_base.convert("L")).astype(int)
        image_corner = numpy.array(image_corner.convert("L")).astype(int)
        diff = image_corner - image_base
        super_threshold_indices = diff < thresh
        diff[super_threshold_indices] = 0
        if save_debug_photos:
            diff_im = Image.fromarray(numpy.absolute(diff).astype('uint8'), "L")
            diff_im.save("debugging/diff.jpg", "JPEG")
        pix_sum = numpy.sum(diff)

        if pix_sum < 0:
            print("Could not find centroid")
            return 0, 0

        def find_centroid(sums):
            #print(sums)
            left_sum = 0
            right_sum = pix_sum
            best_balance_x = 0
            best_balance = pix_sum
            for x in range(len(sums)):
                left_sum = left_sum + sums[x]
                right_sum = right_sum - sums[x]
                balance = abs(right_sum - left_sum)
                if balance < best_balance:
                    best_balance_x = x
                    best_balance = balance
            return best_balance_x

        return (find_centroid(numpy.sum(diff, axis=0)),
                find_centroid(numpy.sum(diff, axis=1)))

    @staticmethod
    def img_diff(img_1, img_2):
        img_1_array = numpy.array(img_1.convert("L")).astype(int)
        img_2_array = numpy.array(img_2.convert("L")).astype(int)
        return numpy.sum(img_1_array - img_2_array)

    @staticmethod
    def find_corner_recurse(image_base, image_corner, thresh, save_debug_photos=False):
        image_base = numpy.array(image_base.convert("L")).astype(int)
        image_corner = numpy.array(image_corner.convert("L")).astype(int)
        diff = image_corner - image_base
        super_threshold_indices = diff < thresh
        if save_debug_photos:
            diff_im = Image.fromarray(numpy.absolute(diff).astype('uint8'), "L")
            diff_im.save("debugging/diff_before_thresh.jpg", "JPEG")
        diff[super_threshold_indices] = 0
        if save_debug_photos:
            diff_im = Image.fromarray(numpy.absolute(diff).astype('uint8'), "L")
            diff_im.save("debugging/diff_after_thresh.jpg", "JPEG")
        axis = 1
        accumulator = [0, 0]
        while diff.shape[0] > 1 or diff.shape[1] > 1:
            index = diff.shape[axis] / 2
            diff_split = numpy.array_split(diff, 2, axis=axis)
            left = diff_split[0]
            right = diff_split[1]
            if numpy.sum(left) < numpy.sum(right):
                accumulator[axis] = index + accumulator[axis]
                diff = right
            else:
                diff = left
            new_axis = 0
            if axis == 0:
                new_axis = 1
            if diff.shape[new_axis] > 1:
                axis = new_axis
        return (int(accumulator[1]), int(accumulator[0]))

    @staticmethod
    def find_corner_average(image_base, image_corner, thresh, save_debug_photos=False):
        (x1, y1) = Perspectives.find_corner_recurse(image_base, image_corner, thresh, save_debug_photos)
        (x2, y2) = Perspectives.find_corner_centroid(image_base, image_corner, thresh, save_debug_photos)
        return (x1 + x2)/2, (y1+y2)/2

    @staticmethod
    def kindle_touch_show_corner_fn(host, corner):
        subprocess.run(["bash", "find-corner-kt.sh", host, corner])
        time.sleep(0.2)
        return 1.15

    @staticmethod
    def letterbox(camera_corners, camera_res, template_image_size):
        temp_width, temp_height = template_image_size
        cam_width, cam_height = camera_res
        cam_aspect_ratio = float(cam_width) / float(cam_height)
        temp_aspect_ratio = float(temp_width) / float(temp_height)
        cam_x, cam_y = camera_corners
        cam_x_f = float(cam_x) / cam_width
        cam_y_f = float(cam_y) / cam_height

        if cam_aspect_ratio == temp_aspect_ratio:
            return int(cam_x_f * temp_width), int(cam_y_f * temp_height)
        elif cam_aspect_ratio < temp_aspect_ratio:
            # print('Image is wider than camera. Letterboxing on top and bottom')
            new_temp_height = temp_width / cam_aspect_ratio
            return int(cam_x_f * temp_width), int(cam_y_f * new_temp_height - (new_temp_height - temp_height)/2)
        else:
            # print('Image is narrower than camera. Letterboxing on left and right')
            new_temp_width = temp_height * cam_aspect_ratio
            return int(cam_x_f * new_temp_width - (new_temp_width - temp_width) / 2), int(cam_y_f * temp_height)

    @staticmethod
    def zoom_corners(corners, factor):
        xs = []
        ys = []
        new_corners = []
        for corner in corners:
            xs.append(corner[0])
            ys.append(corner[1])
        center_x = numpy.sum(xs) / 4
        center_y = numpy.sum(ys) / 4
        for corner in corners:
            new_corners.append((center_x + int((corner[0] - center_x) * factor),
                                center_y + int((corner[1] - center_y) * factor)))
        return new_corners

    def get_different_snapshot(self):
        time.sleep(5)
        return self.get_pil_snapshot()
        return self.get_pil_snapshot().filter(ImageFilter.GaussianBlur(radius=10))
        #next_image = self.get_pil_snapshot()
        #now = time.time()
        #while abs(Perspectives.img_diff(last_image, next_image)) < self.diff_thresh and time.time() < now + 3:
        #    next_image = self.get_pil_snapshot()
        #return next_image

    # returns corners relative to image e.g. [(234, 567), ...]
    def find_corners(self, host, show_corner_fn):
        #last_image = self.get_pil_snapshot()
        show_corner_fn(host, 'all-black')
        image_base = self.get_different_snapshot()
        #last_image = image_base
        if self.save_debug_photos:
            image_base.save("debugging/image_base.jpg", "JPEG")
        corners = []
        for corner in ['top-left', 'top-right', 'bottom-right', 'bottom-left']:
            zoom_factor = show_corner_fn(host, corner)
            # Keep capturing input until it has sufficiently changed
            image_corner = self.get_different_snapshot()
            #last_image = image_corner
            if self.save_debug_photos:
                image_corner.save("debugging/image_corner_"+corner+".jpg", "JPEG")
            corner_px = Perspectives.letterbox(
                self.find_corner_fn(image_base, image_corner, self.corner_thresh, self.save_debug_photos),
                self.camera_res, self.template_image.size)
            print("Found centroid for "+corner+": "+str(corner_px))
            corners.append(corner_px)
        corners = Perspectives.zoom_corners(corners, zoom_factor)

        return corners

    def refresh_host(self, host):
        output_fn = "perspectives-output.png"
        corners = self.find_corners(host, self.hosts[host]['updateFunction'])
        image_to_upload = Perspectives.kindle_transform(self.template_image, self.hosts[host]['resolution'], corners)
        image_to_upload.save(output_fn)
        subprocess.run(["bash", "upload-and-show.sh", host, output_fn])

    def refresh_all_hosts(self):
        for host in self.hosts.keys():
            try:
                self.refresh_host(host)
                time.sleep(2)
            except numpy.linalg.linalg.LinAlgError:
                print("numpy.linalg.linalg.LinAlgError")