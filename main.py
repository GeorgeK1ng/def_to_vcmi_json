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
from pathlib import Path
import json

from homm3data import deffile

path = askopenfilename(filetypes=[("H3 def", ".def")])
if len(path) > 0:
    foldername = os.path.dirname(path)
    filename = os.path.basename(path)

    Path(os.path.join(foldername, Path(filename).stem)).mkdir(parents=True, exist_ok=True)

    tmp_json = { "images": [], "basepath": Path(filename).stem + "/" }
    with deffile.open(path) as d:
        for group in d.get_groups():
            for frame in range(d.get_frame_count(group)):
                frame_base_name = d.get_image_name(group, frame)
                tmp_json["images"].append({ "group": group, "frame": frame, "file": "%s.png" % frame_base_name })

                img = d.read_image('normal', group, frame)
                img.save(os.path.join(foldername, Path(filename).stem, "%s.png" % frame_base_name))
                img = d.read_image('shadow', group, frame)
                if img is not None:
                    img.save(os.path.join(foldername, Path(filename).stem, "%s-shadow.png" % frame_base_name))
                img = d.read_image('overlay', group, frame)
                if img is not None:
                    img.save(os.path.join(foldername, Path(filename).stem, "%s-overlay.png" % frame_base_name))
        
        with open(os.path.join(foldername, "%s.json" % Path(filename).stem),"w+") as o:
            json.dump(tmp_json,o,indent=4)