'''

  VUE synchronization data reader

  http://soft.seliverstoff.ru

  Author: Maxim Seliverstov (aka Seliverstoff)
  E-Mail: maxim@seliverstoff.ru

  This program is free software; you can redistribute it and/or
  modify it under the terms of the GNU General Public License
  as published by the Free Software Foundation; either version 2
  of the License, or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
  GNU General Public License for more details.

  You should have received a copy of the GNU General Public License
  along with this program.  If not, see <http://www.gnu.org/licenses/>.

  All Rights Reserved. VUE(R) is a registered trademark of e-on software, inc.
  http://www.e-onsoftware.com/

'''

import os, sys
import struct
from math import radians
import math
import struct
from collections import namedtuple
	
# next_step, num_obj, num_frames, start_frame, fps, frame_width, frame_height, pixel_aspect, scale, type_obj

class VueSyncFileRead(object):
    next_step    = int
    num_obj      = int
    num_frames   = int
    start_frame  = int
    fps          = float
    frame_width  = int
    frame_height = int
    pixel_aspect = float
    scale        = float
    type_obj     = int
    obj_names    = []
    obj_table    = []
    obj_data     = {}

    def __init__(self, path):
        super(VueSyncFileRead, self).__init__()
        self.path = path

        try:
            f = open(self.path, 'rb')
            self.Get_Sync_Header(f)
            self.Get_Data(f, self.obj_table)
        except IOError:
            print("ERROR: No file!")

    def Get_Sync_Header(self, f):
        h = f.read(36) 
        h = struct.unpack('iiiifiiff', h)

        self.next_step    = h[0]
        self.num_obj      = h[1]
        self.num_frames   = h[2]
        self.start_frame  = h[3]
        self.fps          = h[4]
        self.frame_width  = h[5]
        self.frame_height = h[6]
        pixel_aspect      = h[7]
        scale             = h[8]

        obj = []

        for no in range(self.num_obj):
            n = f.read(12)
            n = struct.unpack('iii', n)
            obj.append(n)

        nm = ""
        no = 0
        for i in range(n[2]-n[1]):
            l = f.read(1)
    
            if(l==b'\x00' and self.num_obj>no):
                self.obj_table.append({
                                        'obj_name'    :nm,
                                        'obj_type'    :obj[no][0],
                                        'length_block':obj[no][1],
                                        'start_block' :obj[no][2]
                                      })
                nm = ""
                l = ""
                no += 1

            nm += l

    def Get_Data(self, f, obt):
        for i in obt:

            self.obj_data[i['obj_name']] = {
                                    'obj_type':i['obj_type'],
                                    'frames'  :[]        
                                }

            f.seek(i['start_block'])
            for frame in range(self.num_frames):

                translate = f.read(12)
                translate = struct.unpack('fff', translate)

                row1 = f.read(12)
                row1 = struct.unpack('fff', row1)

                row2 = f.read(12)
                row2 = struct.unpack('fff', row2)

                row3 = f.read(12)
                row3 = struct.unpack('fff', row3)

                matrix = (row1, row2, row3)

                if i['obj_type'] >= 2: # etc. obj

                    self.obj_data[i['obj_name']]['frames'].append({ 'frame'    :frame,
                                                                    'translate':translate,
                                                                    'matrix'   :matrix
                                                                  })
                    
                elif i['obj_type'] == 1: # CAMERA

                    cam = f.read(12)
                    cam = struct.unpack('fff', cam)
                    duble = f.read(56)

                    self.obj_data[i['obj_name']]['frames'].append({ 'frame'    :frame,
                                                                    'translate':translate,
                                                                    'matrix'   :matrix,
                                                                    'fov'      :cam[0],
                                                                    'focus'    :cam[1],
                                                                    'm_blur'   :cam[2]
                                                                  })



        

test = VueSyncFileRead("/Users/dorshs/Desktop/waterfall_for_vue.dat")
print(test.obj_data['Camera'])


