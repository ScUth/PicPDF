import PIL
from PIL import Image, ExifTags
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import os
import sys
import re
import fitz

# Global variable
y = ['Y', 'y', 'ั', 'υ']
a = ['A', 'a']
m = ['M', 'm']

# root = tk.Tk()
# root.title('Tkinter File Dialog')
# root.resizable(False, False)
# root.geometry('300x150')


def select_files():
    filetypes = (
        ('image files', '*.jpg'),
        ('All files', '*.*')
    )

    filenames = fd.askopenfilenames(
        title='Open files',
        initialdir='/',
        filetypes=filetypes
    )

    return filenames
# Rotate image based on EXIF orientation


def correct_image_orientation(image):
    try:
        for orientation in ExifTags.TAGS.keys():
            if ExifTags.TAGS[orientation] == 'Orientation':
                break

        exif = image._getexif()

        if exif is not None:
            orientation_value = exif.get(orientation)

            if orientation_value == 3:
                image = image.rotate(180, expand=True)
            elif orientation_value == 6:
                image = image.rotate(270, expand=True)
            elif orientation_value == 8:
                image = image.rotate(90, expand=True)

    except (AttributeError, KeyError, IndexError):
        # If there is no EXIF data or the orientation key is missing
        pass
    return image


def format_name(name):
    # used in name that included path in it
    for od, char in enumerate(name):
        if char == "/":
            odr = od
    fmnam = name.replace(name[0:odr + 1], "")
    return fmnam


def extract_name(name):
    for od, char in enumerate(name):
        if char == ".":
            odr = od
    fnam = name.replace(name[odr:len(name)], "")
    return fnam


def extract_type(name):
    for od, char in enumerate(name):
        if char == ".":
            odr = od
    fnam = name.replace(name[0:odr + 1], "")
    return fnam


def file_name(lis):
    fn = min(lis)
    fn = format_name(fn)
    ln = max(lis)
    ln = format_name(ln)
    return f"{extract_name(fn)} - {extract_name(ln)}"


def get_path(name):
    # get path from name
    for od, char in enumerate(name):
        if char == "/":
            odr = od
    path = name.replace(name[odr+1: len(name)], "")
    return path


def natural_sort_key(text):
    # Splits the string into alternating substrings of text and integers
    return [int(c) if c.isdigit() else c for c in re.split(r'(\d+)', text)]


def savePDF(tpl, name, path):
    result = fitz.open()

    for pdf in tpl:
        with fitz.open(pdf) as mfile:
            result.insert_pdf(mfile)

    result.save(f"{path}{name}.pdf")


def auto():
    print("By auto converting, the name of your converted file will be the same as your picture file.")
    tpl = select_files()
    path = get_path(tpl[0])

    for file in tpl:
        filename = format_name(file)
        pdf_path = f"{path}{filename}.pdf"
        print("converting", filename)
        images = [correct_image_orientation(Image.open(file))]
        images[0].save(pdf_path, "PDF", resolution=100.0,
                       save_all=True, append_images=images)

    print(f"All file are save at {path}")


def manual():
    ns = input('Sort by name? (Y/N) : ')
    tpl = select_files()  # Output is tpl
    path = get_path(tpl[0])
    print(path)
    name = input('Name : ')
    numberOfTime = 0
    if name == "":
        name = file_name(tpl)
    pdf_path = f"{path}{name}.pdf"
    type = extract_type(format_name(tpl[0]))

    while ns not in ['Y', 'y', 'ั', 'υ', 'N', 'n', 'ื', 'ν']:
        ns = input('WRONG REPLY!, Sort by name? (Y/N) : ')

    if ns in ['Y', 'y', 'ั', 'υ']:
        check = input(
            'Sort in (1)-normal order [1, 2, 3] OR (2)-reverse order [3, 2, 1] (1/2) : ')
        while check not in ['1', '2']:
            check = input(
                'WRONG REPLY!, Sort in (1)-normal order [1, 2, 3] OR (2)-reverse order [3, 2, 1] (1/2) : ')
        while True:
            tplTMP = tpl
            if check == '1':
                print("confirmed check = 1")
                numberOfTime += 1
                lis = list(tplTMP)
                # lis.sort(reverse=False)
                lis = sorted(lis, key=natural_sort_key)
                tplTMP = tuple(lis)

                for filename in tplTMP:
                    print(filename)
                print()
                nd_check = input("Is this order correct? (Y/N) : ")
                if nd_check in ['Y', 'y', 'ั', 'υ']:
                    break
                else:
                    # print("Try select image by order again and type (N) for not sorting.")
                    if numberOfTime >= 2:
                        sys.exit(
                            "Try select image by order again and type (N) for not sorting.")
                    print("This is (2-reverse order) option ")
                    check = '2'
            elif check == '2':
                print("confirmed check = 2")
                numberOfTime += 1
                tplTMP = sorted(tplTMP, key=natural_sort_key, reverse=True)
                for filename in tplTMP:
                    print(filename)
                print()
                nd_check = input("Is this order correct? (Y/N) : ")
                if nd_check in ['Y', 'y', 'ั', 'υ']:
                    break
                else:
                    if numberOfTime >= 2:
                        sys.exit(
                            "Try select image by order again and type (N) for not sorting.")
                    # print("Try select image by order again and type (N) for not sorting.")
                    print("This is (1-normal order) option ")
                    check = '1'
    else:
        print('Not sorting')
        for filename in tpl:
            print(filename)
        check = input("Is this order correct? (Y/N) : ")
        if check in y:
            pass
        else:
            sys.exit("Program closed")

    if type in ["PDF", "pdf"]:
        savePDF(tplTMP, name, path)
    else:
        images = [correct_image_orientation(Image.open(img)) for img in tplTMP]
        images[0].save(pdf_path, "PDF", resolution=100.0,
                       save_all=True, append_images=images[1:])


def semiAuto():
    pass


def main():
    print("PicPDF version 0.6.0 powered by Python © Scith - Jul 2026")
    print("Update 07-Jul-2026 this version can combined PDF files, but beware of your files to be an all images or all PDF (can't combined now)")
    mode = input(
        'Select mode manual or auto [each picture each PDF] (M/ any ) : ')
    if mode in m:
        manual()
    else:
        auto()


main()
