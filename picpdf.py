import PIL
from PIL import Image, ExifTags
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog as fd
import os
import sys
import re
import fitz
from pathlib import Path

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

def select_folder():
    folderName = fd.askdirectory(
        title="Select a Folder",
        initialdir="/"
    )
    return folderName


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


def extract_type(name): # extension
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


def OneByOne():
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


def ask_yes_no(prompt):
    """Ask a yes/no question, retry until valid answer. Returns True for yes."""
    while True:
        ans = input(prompt).strip()
        if ans in ['Y', 'y', 'ั', 'υ']:
            return True
        if ans in ['N', 'n', 'ื', 'ν']:
            return False
        print("WRONG REPLY! Please answer Y or N.")


def preview_and_confirm(tpl_sorted, path, name, type):
    """Show the file order and let user confirm or pick a different order.
    Returns the confirmed tuple, or exits if user gives up."""
    attempts = 0
    max_attempts = 3

    while True:
        print("\n--- Preview ---")
        for i, filename in enumerate(tpl_sorted, 1):
            print(f"  {i}. {format_name(filename)}")
        print(f"Output: {path}{name}.pdf")
        print("---------------")

        if ask_yes_no("Is this order correct? (Y/N): "):
            return tpl_sorted

        attempts += 1
        if attempts >= max_attempts:
            sys.exit("Too many failed attempts. Program closed.")

        # Ask for a different order
        choice = input(
            "Sort order: (1)-Ascending [1,2,3]  (2)-Descending [3,2,1]  (N)-No sort (1/2/N): "
        ).strip().lower()
        while choice not in ['1', '2', 'n']:
            choice = input(
                "WRONG REPLY! (1)-Ascending  (2)-Descending  (N)-No sort (1/2/N): "
            ).strip().lower()

        tpl_sorted = apply_sort(tpl_sorted, choice)


def apply_sort(tpl, choice):
    """Return tpl sorted according to choice: '1'=asc, '2'=desc, 'n'=as-is."""
    if choice == '1':
        return tuple(sorted(tpl, key=natural_sort_key))
    if choice == '2':
        return tuple(sorted(tpl, key=natural_sort_key, reverse=True))
    return tuple(tpl)


def manual():
    print("Manual mode: choose files, set output name, choose order, confirm.")

    # 1. Pick files
    tpl = select_files()
    if not tpl:
        sys.exit("No files selected.")

    path = get_path(tpl[0])
    print(f"Files will be saved in: {path}")

    # 2. Output name
    name = input("Name (leave blank to auto-generate): ").strip()
    if name == "":
        name = file_name(tpl)
    pdf_path = f"{path}{name}.pdf"
    file_type = extract_type(format_name(tpl[0]))

    # 3. Initial sort choice
    choice = input(
        "Sort order: (1)-Ascending [1,2,3]  (2)-Descending [3,2,1]  (N)-No sort (1/2/N): "
    ).strip().lower()
    while choice not in ['1', '2', 'n']:
        choice = input(
            "WRONG REPLY! (1)-Ascending  (2)-Descending  (N)-No sort (1/2/N): "
        ).strip().lower()

    tpl_sorted = apply_sort(tpl, choice)

    # 4. Preview + confirm (can change order if not happy)
    tpl_sorted = preview_and_confirm(tpl_sorted, path, name, file_type)

    # 5. Build the PDF
    if file_type.lower() == "pdf":
        savePDF(tpl_sorted, name, path)
    else:
        images = [correct_image_orientation(Image.open(img)) for img in tpl_sorted]
        images[0].save(
            pdf_path, "PDF", resolution=100.0,
            save_all=True, append_images=images[1:]
        )

    print(f"\nDone! PDF saved at: {pdf_path}")


def Folder():
    print("Folder mode: Convert all images in a folder into a single PDF")
    path = select_folder()
    if not path:
        sys.exit("No folder selected")
    
    # Ensure path ends with separator
    if not path.endswith(os.sep):
        path += os.sep
    
    # Get all image files in folder
    valid_ext = ('.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.tif', '.webp')
    all_files = os.listdir(path)
    tpl = tuple(
        os.path.join(path, f) for f in all_files
        if f.lower().endswith(valid_ext) and os.path.isfile(os.path.join(path, f))
    )
    
    if not tpl:
        sys.exit("No image files found in the selected folder")
    
    print(f"\nFound {len(tpl)} image file(s):")
    for f in tpl:
        print(f"  {format_name(f)}")
    
    # Ask for output name
    default_name = format_name(path.rstrip(os.sep))
    nameDecision = input(f"\nDo you want to use '{default_name}' as the PDF name? (Y/N): ")
    if nameDecision in y:
        name = default_name
    else:
        name = input("Enter PDF name: ").strip()
        if name == "":
            name = default_name
    
    # Ask for sorting order
    sort_choice = input(
        "Sort order: (1)-Ascending [1,2,3]  (2)-Descending [3,2,1]  (N)-No sort (1/2/N): "
    ).strip().lower()
    while sort_choice not in ['1', '2', 'n']:
        sort_choice = input(
            "WRONG REPLY! (1)-Ascending  (2)-Descending  (N)-No sort (1/2/N): "
        ).strip().lower()
    
    # Apply sorting
    if sort_choice == '1':
        tpl_sorted = tuple(sorted(tpl, key=natural_sort_key))
        order_label = "Ascending"
    elif sort_choice == '2':
        tpl_sorted = tuple(sorted(tpl, key=natural_sort_key, reverse=True))
        order_label = "Descending"
    else:
        tpl_sorted = tpl
        order_label = "No sort (as listed)"
    
    # Show sorting result and confirm
    print(f"\n--- Sorting result ({order_label}) ---")
    for i, filename in enumerate(tpl_sorted, 1):
        print(f"  {i}. {format_name(filename)}")
    print("-----------------------------------")
    print(f"Output: {path}{name}.pdf")
    
    confirm = input("\nConfirm and create PDF? (Y/N): ").strip()
    while confirm not in y and confirm not in ['N', 'n', 'ื', 'ν']:
        confirm = input("WRONG REPLY! Confirm and create PDF? (Y/N): ").strip()
    
    if confirm not in y:
        sys.exit("Program closed")
    
    # Create PDF
    pdf_path = f"{path}{name}.pdf"
    images = [correct_image_orientation(Image.open(img)) for img in tpl_sorted]
    images[0].save(
        pdf_path, "PDF", resolution=100.0,
        save_all=True, append_images=images[1:]
    )
    print(f"\nDone! PDF saved at: {pdf_path}")


def main():
    print("PicPDF version 0.7.0 powered by Python - Oct 2026")
    print("Update 17-Oct-2026 this version can combined PDF files, but beware of your files to be an all images or all PDF (can't combined now)")
    mode = input(
        'Select mode manual or one-by-one or folder [each picture each PDF] (M/O/F): ').lower()
    if mode == "m":
        manual()
    elif mode == "o":
        OneByOne()
    elif mode == "f":
        Folder()

main()
