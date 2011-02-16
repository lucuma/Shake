# -*- coding: utf-8 -*-
"""

"""
from math import ceil
try:
    from PIL import Image, ImageOps
except ImportError:
    raise ImportError('Shake-images needs the Python Image Library (PIL)'
        ' to run.  You can get it from http://pypi.python.org/pypi/Pillow\n'
        ' If you\'ve already installed PIL, then make sure you have '
        ' it in your PYTHONPATH.')
import os


_IMAGE_OPERATIONS = [
    'resize', 'crop', 'crop_square', 'resize_canvas', 'overlay',
    'mask', 'set_opacity', 'rotate', 'grayscale', 'invert_colors',
    ]

__all__ = ['make_thumbnails', 'process_image'] + _IMAGE_OPERATIONS


def make_thumbnails(base_root, src_path, src_name, rules):
    """ """
    path = os.path.join(base_root, src_path, src_name)

    for rule in rules:
        name = rule[0]
        operations = rule[1:]
        new_path = path
        if name:
            new_path = os.path.join(base_root, src_path, name)
            if not os.path.exists(new_path):
                os.makedirs(new_path)
            new_path = os.path.join(new_path, src_name)

        process_image(path, new_path, operations)


def process_image(path, new_path, operations, format=''):
    """ """
    img = Image.open(path)
    format = format.upper()
    if not format:
        format = img.format

    globals_ = globals()
    for fname, kwargs in operations:
        if callable(fname):
            # Do you want to use a custom operation? You got it!
            func = fname
        else:
            if fname not in _IMAGE_OPERATIONS:
                raise KeyError(fname)
            func = globals_[fname]

        img = func(img, **kwargs)

    if format in ('JPEG', 'JPG'):
        img.save(new_path, format='JPEG', quality=90)
    else:
        img.save(new_path, format=format)


def _hex_to_rgb(color):
    """Transforms an hex color (eg: #ffaf2e, #fff, #ffaf2e00) into a
    RGBA tuple.
    """
    if not isinstance(color, basestring):
        return color
    color = color.lstrip('#')
    len_color = len(color)
    try:
        if len_color == 6:
            return tuple([int(c, 16)
                for c in (color[0:2], color[2:4], color[4:6], 255)])
        elif len_color == 3:
            return tuple([int(c, 16) * 17 for c in color]) + (255, )
        elif len_color == 8:
            return tuple([int(c, 16)
                for c in (color[0:2], color[2:4], color[4:6], color[6:8])])
        elif len_color == 4:
            return tuple([int(c, 16) * 17 for c in color])
        else:
            raise ValueError("Hex color must be 6, 3, 8 or 4 characters long")
    except ValueError, error:
        raise ValueError("'%s' is not an hex color (%s)" %
            (color, error.message))


def resize(img, width, height, fit=True, fill=None):
    """Resizes an image to new dimensions.

    If the original image is smaller than both the new dimensions,
    it's returned unchanged or pasted over a new width x height canvas with
    with `fill` background color.

    :param img:
        a `class:PIL.Image` instance.

    :param width:
        new width.

    :param height:
        new height.

    :param fit:
        if True, the new dimensions are maximum.
        if 'width' or 'height, that dimension of the image'll be fitted.

    :param fill:
        A rgba color tuple. If set and the original image is smaller than the
        new dimensions, the image'll be pasted over a width x height canvas
        filled with this color.

    """
    img_width, img_height = img.size
    if (img_width == width) and (img_height == height):
        return img

    if (img_width < width) and (img_height < height):
        if fill:
            return resize_canvas(img, width, height, fill)
        return img

    new_size = (width, height)
    if fit is True:
        img.thumbnail(new_size, Image.ANTIALIAS)
        if fill:
            img = resize_canvas(img, width, height, fill)
        return img

    img_ratio = float(img_width) / img_height
    new_width = int(ceil(height * img_ratio))

    if (fit == 'height') or (new_width > width):
        new_height = height
    else:
        new_width = width
        new_height = int(ceil(width / img_ratio))

    img = img.resize((new_width, new_height), Image.ANTIALIAS)
    if fill:
        width = max(width, new_width)
        height = max(height, new_height)
        return resize_canvas(img, width, height, fill)
    return img


def crop(img, width, height, x=0, y=0, fill=(255, 255, 255, 0)):
    """Crops an image to the specified size.

    :param img:
        a `class:PIL.Image` instance.

    :param width:
        desired width.

    :param height:
        desired height.

    :param x:
        `x` coordinate of the new top-left corner.
        if `center` this'll be dynamic.

    :param y:
        `y` coordinate of the new top-left corner.
        if `center` this'll be dynamic.

    :param fill:
        A rgb color tuple. If set and the original image is smaller than the
        new dimensions, the image'll be pasted over a width x height canvas
        filled with this color.

    """
    img_width, img_height = img.size
    if (img_width == width) and (img_height == height):
        return img

    if (img_width < width) and (img_height < height):
        if fill:
            return resize_canvas(img, width, height, fill)
        return img

    left = x
    top = y
    width = min(img_width, width)
    height = min(img_height, height)

    if x == 'center':
        left = int(round((img_width - width) / 2.0))

    if y == 'center':
        top = int(round((img_height - height) / 2.0))

    right = min(img_width, width + left)
    bottom = min(img_height, height + top)
    new_size = (left, top, right, bottom)
    return img.crop(new_size)


def crop_square(img, side, fill=(255, 255, 255, 0)):
    """Shortcut for crop(img, side, side, 'center', 'center', fill)
    """
    return crop(img, side, side, 'center', 'center', fill)


def resize_canvas(img, width, height, fill=(255, 255, 255, 0)):
    """Adjusts the canvas size and centers the image.

    :param img:
        a `class:PIL.Image` instance.

    :param width:
        width of resized canvas.

    :param height:
        height of resized canvas.

    :param fill:
        color for the canvas background. It can be a RGB or RGBA tuple
        or a string hex color.

    """
    new_size = (width, height)
    if new_size == img.size:
        return img

    fill = _hex_to_rgb(fill)
    new_img = Image.new('RGBA', new_size, fill)
    img_width, img_height = img.size
    x = (width - img_width) / 2
    y = (height - img_height) / 2
    new_img.paste(img, (x, y))
    return new_img


def overlay(img, overlay_img):
    """Renders a translucent image over the image.

    :param img:
        a `class:PIL.Image` instance.

    :param overlay_img:
        system path to the overlay image or a
        `class:PIL.Image` instance.

    """
    if isinstance(overlay_img, basestring):
        overlay_img = Image.open(overlay_img)
    img.paste(overlay_img, (0, 0), overlay_img)
    return img


def mask(img, mask_img):
    """Replaces the alpha channel with a new image.

    :param img:
        a `class:PIL.Image` instance.

    :param mask_img:
        system path to the mask image or a `class:PIL.Image`
        instance.

    """
    if isinstance(mask_img, basestring):
        mask_img = Image.open(mask_img)
    mask_img = mask_img.convert('L')
    img.convert('RGBA')
    img.putalpha(mask_img)
    return img


def set_opacity(img, opacity=0.5):
    """Sets the alpha channel to a given opacity.

    :param img:
        a `class:PIL.Image` instance.

    :param opacity:
        A floating point value between 0 and 1, where 0 is
        fully transparent.

    """
    opacity = max(0, min(255, int(opacity * 255.0)))
    img.putalpha(opacity)
    return img


def rotate(img, angle, expand=False):
    """Rotate an image.

    :param img:
        a `class:PIL.Image` instance

    :param angle:
        degrees [-360, 360] counter-clockwise.

    :param expand:
        if true, the output image is made large enough to hold the
        entire rotated image.

    """
    return img.rotate(angle, resample=Image.BICUBIC, expand=expand)


def grayscale(img):
    """Converts the image to grayscale.

    :param img:
        a `class:PIL.Image` instance.

    """
    return ImageOps.grayscale(img)


def invert_colors(img):
    """Inverts the colors in the image.

    :param img:
        a `class:PIL.Image` instance.

    """
    return ImageOps.invert(img)
