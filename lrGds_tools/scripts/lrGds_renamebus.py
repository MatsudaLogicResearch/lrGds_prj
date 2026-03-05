#===================================================================
# This file is associated with the lrGen project.
# Copyright (C) 2026 Logic-Research K.K. (Author: MATSUDA Masahiro)
# 
# This script file is licensed under the MIT License.
#===================================================================
#[Description]
# rename bus expression from <%d> to [%d] in GDS.
#
#[HISTORY]
#===================================================================

import argparse
import os.path
import gdstk
import re
import sys

__version__ = "2.0.0"

ptn = re.compile(r"<(\d+)>")

def convert_text(cell, depth, max_depth, visited=None):
  #-- check visited
  if visited is None:
    visited = set()
  elif cell.name in visited:
    return

  visited.add(cell.name)
    
  #-- convert text
  for label in cell.labels:
    if label.text:
      old_text = label.text
      new_text = ptn.sub(r"[\1]", old_text)

      if new_text != old_text:
        indent = " "*(depth-1)
        print(f"  [INF]:{depth:2d}:{indent}{cell.name}: {old_text} -> {new_text}")
        label.text = new_text

  #-- check depth
  if (max_depth>0) and (depth >= max_depth):
    return

  #-- search bottom
  for ref in cell.references:
    if ref.cell:
      convert_text(ref.cell, depth+1, max_depth, visited)
  
def main(argv=None, prog_name=None):

  if prog_name is None and argv:
    prog_name = sys.argv[0]
    
  # argv が None なら sys.argv[1:] を使う
  if argv is None:
    argv = sys.argv[1:]

  #-- create parser
  parser = argparse.ArgumentParser(prog=prog_name)

  #-- define parameter
  parser.add_argument('-v',"--version"     ,action='version', version=f'%(prog)s {__version__}')
  parser.add_argument("--in_gds"           ,type=str ,default='in.gds'  ,help='input gds.')
  parser.add_argument("--out_gds"          ,type=str ,default='out.gds' ,help='outoput gds.')
  parser.add_argument("--max_depth"        ,type=int ,default=1         ,help='search depth(0 or 1 or 2 or ,,,).')
  
  #-- parse
  args = parser.parse_args(argv)  
  
  #-- check in_gds
  if not os.path.isfile(args.in_gds):
    print(f"[ERR]: input gds={args.in_gds} not exist.")
    sys.exit(1)

  #-- read gds
  lib = gdstk.read_gds(args.in_gds)
  top_cells = lib.top_level()

  #-- convert
  for cell in top_cells:
    convert_text(cell, 1, args.max_depth)
  
  #-- write gds
  lib.write_gds(args.out_gds)
  

if __name__ == "__main__":
  main(sys.argv[1:])
  
