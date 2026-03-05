#===================================================================
# This file is associated with the lrGen project.
# Copyright (C) 2026 Logic-Research K.K. (Author: MATSUDA Masahiro)
# 
# This script file is licensed under the MIT License.
#===================================================================
#[Description]
# search TEXT(layer/texttype) from TargetCell.
#
#[HISTORY]
#===================================================================

import gdstk
import numpy as np
import argparse
import os.path
import sys

__version__ = "2.0.0"
g_disp_hd=1

def find_text(lib, hier, prefix, off_x, off_y, mag, inv, rot, cell, text_layer_names, text_depth=0, text_is_one=False):

  # cell名の表示
  #print(cell.name)
  #print(text_depth)
  
  # 上位セル名の取得
  prefix_list =  prefix.split('/')
  if len(prefix_list)>=2:
    up_cell_name  = prefix.split('/')[-2]
  else:
    up_cell_name  = prefix.split('/')[-1]

  up_cell_name  = up_cell_name.split(':')[0]; 

  
  # セル名の取得。
  tgt_cell_name = cell.name
  
  tgt_x         = off_x
  tgt_y         = off_y
  tgt_mag       = mag
  tgt_inv       = inv
  tgt_rot       = rot
  
  
  # テキストの探索
  for layer_ttype in text_layer_names.split(','):
    layer = int(layer_ttype.split('/')[0])
    ttype = int(layer_ttype.split('/')[1])

    for label in cell.get_labels(depth=text_depth, layer=layer, texttype=ttype):
    #for label in cell.get_labels():
      #print(label)
      
      # 対象TEXTのoffsetをゲット
      org=label.origin

      # X軸反転
      if inv:
        a = np.array([[1,0],
                      [0,-1]])
      else:
        a = np.array([[1,0],
                      [0,1]])
      
      org_inv=np.dot(a,org)
      
      # rotation
      r = np.array([[np.cos(rot), -np.sin(rot)],
                    [np.sin(rot),  np.cos(rot)]])
      org_rot= np.dot(r, org_inv)
            
      # mag
      m = np.array([[mag, 0],
                      [0, mag]])

      org_mag = np.dot(m, org_rot)
    
      # 
      #x = off_x + org_mag[0]
      #y = off_y + org_mag[1]
      
      #-- offset from target_cell
      x = org_mag[0]
      y = org_mag[1]

      #hier,path,x,y,mag,rotation,unit
      
      tgt_rot_deg=tgt_rot*180/np.pi
      rot_deg=rot*180/np.pi
      
      
      global g_disp_hd
      if(g_disp_hd):
        print(" hier,cell_path(cell_name:ins_num:ins_name),upper_cell_name,target_cell_name,tgt_x,tgt_y,tgt_mag,tgt_inv,tgt_rot,text_name,text_x_off,text_y_off,text_mag,text_inv,text_rot,unit,layer,datatype")
        g_disp_hd=0

      #print("%d,%s,%s,%s,%f,%f,%f,%d,%f,%s,%f,%f,%f,%d,%f,%f" % (hier, prefix, up_cell_name, tgt_cell_name, tgt_x ,tgt_y, tgt_mag, tgt_inv, tgt_rot, label.text, x, y, mag, inv, rot, lib.unit))
      print("%d,%s,%s,%s,%f,%f,%f,%d,%f,%s,%f,%f,%f,%d,%f,%f,%s,%s" % (hier, prefix, up_cell_name, tgt_cell_name, tgt_x ,tgt_y, tgt_mag, tgt_inv, tgt_rot_deg, label.text, x, y, mag, inv, rot_deg, lib.unit, layer, ttype))
      
      
      if(text_is_one):
        print("one is True")
        return

  return
      

def find_cell(lib, hier, prefix, ref_num, cell_ins_name, off_x, off_y, mag, inv, rot,  cell, target_cell_names, text_layer_names, text_depth=0, text_is_one=False):

  
  # 階層情報の更新
  hier2=hier + 1

  prefix2=prefix + "/" + cell.name

  prefix2 += ":{:}".format(cell_ins_name)

  prefix2 += ":{:}".format(ref_num)


  #print(cell.name)
  #print(target_cell_names.split(','))
  
  # セルの一致
  if cell.name in target_cell_names.split(','):
    find_text(lib, hier2, prefix2, off_x, off_y, mag, inv, rot, cell, text_layer_names, text_depth, text_is_one)
    
  # 下位の階層を検索
  if cell.references:
  
    ref_num = 0
    for ref in cell.references:
      # property 情報の取得(KlayoutではPropertyのKEYは整数値のみのため、KEY=0の場合はVLAUEはinstance名としておく)
      props=ref.properties
      prop_dict={}
      if props:
        for prop in props:
          if len(prop) == 3:
            prop_dict[int(prop[1])] = prop[2].decode('utf-8').rstrip(chr(0))

      # インスタンス名があればそれを使う(GDS Property: KEY=0, VALUE=instance name)
      cell_ins_name=""
      if 0 in prop_dict:
         cell_ins_name = prop_dict[0]

      # セル座標の取得
      v_org = [ref.origin[0], ref.origin[1]]

      # X軸反転
      if inv:
        a = np.array([[1,0],
                      [0,-1]])
      else:
        a = np.array([[1,0],
                      [0,1]])
      
      v_org_ref=np.dot(a,v_org)
      
      # rotation
      r = np.array([[np.cos(rot), -np.sin(rot)],
                    [np.sin(rot),  np.cos(rot)]])
      v_org_rot= np.dot(r, v_org_ref)

      # mag
      m = np.array([[mag, 0],
                    [0, mag]])

      v_org_mag = np.dot(m, v_org_rot)

      #
      #off_x2 = off_x + v_org[0]
      #off_y2 = off_y + v_org[1]

      off_x2 = off_x + v_org_mag[0]
      off_y2 = off_y + v_org_mag[1]


      inv2   =int((inv + ref.x_reflection)%2)
      mag2   = mag * ref.magnification
      rot2   = rot + ref.rotation
      
      #
      find_cell(lib, hier2, prefix2, ref_num, cell_ins_name,
                off_x2, off_y2, mag2, inv2, rot2,
                lib[ref.cell_name], target_cell_names, text_layer_names, text_depth, text_is_one)
                
      #
      ref_num += 1


  # 一致しなければ何もしない
  return None
    
def extract_cell(lib, cell, target_cell_names, text_layer_names, text_depth=1, text_is_one=False):
  offset_x=0
  offset_y=0
  
  # GDSファイルを読み込む
  #lib=gdstk.read_gds(gds_file)

  # search hier
  hier=0;
  prefix=""
  ref_num=0
  cell_ins_name=""
  prop_dict={}
  off_x=0;
  off_y=0;
  mag=1.0;
  inv=0;
  rot=0

  find_cell(lib, hier, prefix, ref_num, cell_ins_name,off_x, off_y, mag, inv, rot, cell, target_cell_names, text_layer_names, text_depth, text_is_one)
  

  #if target_cell is None:
  #  print(f"セル '{cell_name}' が見つかりませんでした。")
  #  return
  #
  ## セル内の各要素の座標を抽出
  #for element in target_cell.elements:
  #  if isinstance(element, gdstk.Reference):
  #    print(f"要素 '{element.ref_cell.name}' の座標: ({element.origin.x}, {element.origin.y})")
  #    

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
  parser.add_argument("--gds"              ,type=str ,default='sample/test.gds'          ,help='target gds.')
  parser.add_argument("--top_cell"         ,type=str ,default='LDIC_TEG2'                ,help='top cell name in target gds.')
  parser.add_argument("--target_cell_names",type=str ,default='blk1'                     ,help='target cell names(list).'    )
  parser.add_argument("--text_layers"      ,type=str ,default='46/1,146/1'               ,help='text layer/ text type(list).')
  parser.add_argument("--text_depth"       ,type=int ,default=0                          ,help='search depth(0 or 1 or 2 or ,,,).')
  parser.add_argument("--text_is_one"      ,type=int ,default=0                          ,help='1: find only 1 text in target_cell')
  
  #-- parse
  args = parser.parse_args(argv)  
  
  #-- check & read gds
  if not os.path.isfile(args.gds):
    print(f"[ERR]: input gds={args.gds} not exist.")
    sys.exit(1)
  else:
    lib=gdstk.read_gds(args.gds)
    
  #-- check top_cell
  top_names=[cell.name for cell in lib.top_level()]
  if args.top_cell not in top_names:
    print(f"[ERR]: top_cell={args.top_cell} not exist in GDS(cells={top_names}).")
    sys.exit(1)

  #-- search text
  text_is_one=True if args.text_is_one==1 else False; #--- argsでbool型を扱えない
  extract_cell(lib, lib[args.top_cell], args.target_cell_names, args.text_layers, args.text_depth, text_is_one)
      
if __name__ == "__main__":
  main(sys.argv[1:]);
  
