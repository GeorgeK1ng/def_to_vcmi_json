#!/usr/bin/env python3
#
# Copyright (C) 2024  Laserlicht
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

from tkinter.filedialog import askopenfilename
from tkinter import messagebox
import os

from lodextract.lodextract import unpack_lod
from lodextract.defextract import extract_def
from lodextract.makedef import makedef

path = askopenfilename(filetypes=[("H3 def", ".def")])
if path != "":
    foldername = os.path.dirname(path)
    filename = os.path.basename(path)

    extract_def(path, foldername)