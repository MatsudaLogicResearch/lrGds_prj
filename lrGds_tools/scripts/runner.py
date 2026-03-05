#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#===================================================================
# This file is associated with the lrGen project.
# Copyright (C) 2025-2026 Logic-Research K.K. (Author: MATSUDA Masahiro)
# 
# This script file is licensed under the MIT License.
#===================================================================
#[Description]
# runs sub command script.
#===================================================================

import argparse
import sys
from . import lrGds_findtext
from . import lrGds_renamebus

cmds=["findtext", "renamebus"]

def print_help():
  msg_cmds=",".join(cmds)
  print(f" Usage: lrGds_tools <command> [args...]")
  print(f" Available commands: {msg_cmds}")
  print(f"")
    
def main():
  # 引数を知らない部分 (サブコマンド以降) を取っておく
  if len(sys.argv)<2 or (sys.argv[1] in ("-h","-help")) or (sys.argv[1] not in cmds):
    print_help()
    sys.exit(0)
  
  ## execute
  cmd=sys.argv[1]
  argv=sys.argv[2:]
  
  #print(argv)
  if cmd == "findtext":
    lrGds_findtext.main(argv=argv, prog_name=cmd)
  elif cmd == "renamebus":
    lrGds_renamebus.main(argv=argv, prog_name=cmd)
  else:
    print_help()
    sys.exit(0)
    
if __name__ == "__main__":
    main()
        
