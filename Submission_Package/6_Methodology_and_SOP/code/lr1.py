# LPS final reference session 28 Sep 2026 (60 % / 40 s / 5 acc) - inventory, copy, process, QC
import os,re,glob,shutil,hashlib,pickle,numpy as np,pandas as pd
from scipy.signal import savgol_filter
from lib2 import read_any,process_v3h,LIB
SRC=os.path.expanduser('~/mnt/28-9-26-lps-bulk')
md5=lambda p: hashlib.md5(open(p,'rb').read()).hexdigest()
items=[]
for i in range(10,21): items.append((f'40-60-5-diffrentposition-/SP_{i}.csv','LPS_Bulk',f'LPS_Bulk_20260928_P060pct_T40s_A05_S{i:02d}.csv','final set'))
for i,n in enumerate(['blank.csv','blank2.csv','blank3.csv'],1): items.append((f'blank+short/{n}','Glass_Blank',f'Glass_Blank_20260928_P060pct_T40s_A05_S{i:02d}.csv','matched blank'))
for i in (1,2): items.append((f'blank+short/short blank at 60p- 5s-1 acc-{i}.csv','Glass_Blank',f'Glass_Blank_20260928_P060pct_T05s_A01_S{i:02d}_short.csv','short (unsaturated) blank'))
IC='Instrument_Checks'
items+= [('blank+short/shutter-closed check frame at 60p-40 s- 5 acc.csv',IC,'Check_20260928_P060pct_T40s_A05_ShutterClosedFrame_S02.csv','shutter-closed check frame (end of session)'),
 ('unwanted/test-machine/SP_8.csv',IC,'Check_20260928_P060pct_T40s_A05_ShutterClosedFrame_S01.csv','shutter-closed check frame (orig SP_8)'),
 ('unwanted/test-machine/dark.csv',IC,'Check_20260928_P060pct_T40s_A05_ShutterClosedDark_S01.csv','dark acquired with shutter closed by hand (orig dark.csv)'),
 ('unwanted/laseroff test.csv',IC,'Check_20260928_P070pct_T30s_A05_LaserOff_S01.csv','laser-off test (orig "laseroff test")'),
 ('unwanted/test-machine/laseroff-manualllyclosed shutter.csv',IC,'Check_20260928_P060pct_T30s_A05_ShutterClosedFrame_S01.csv','laser off, shutter closed by hand'),
 ('unwanted/SP_3.csv','LPS_Bulk','LPS_Bulk_20260928_P070pct_T30s_A05_S06.csv','troubleshooting (orig unwanted/SP_3) - ripple'),
 ('unwanted/SP_4.csv','LPS_Bulk','LPS_Bulk_20260928_P070pct_T30s_A05_S07.csv','troubleshooting (orig unwanted/SP_4) - ripple'),
 ('unwanted/SP_5.csv','LPS_Bulk','LPS_Bulk_20260928_P070pct_T30s_A05_S08.csv','troubleshooting (orig unwanted/SP_5) - ripple'),
 ('unwanted/test-machine/30s-60p-5ac-sp1.csv','LPS_Bulk','LPS_Bulk_20260928_P060pct_T30s_A05_S11.csv','troubleshooting (orig sp1) - dark contains sample light'),
 ('unwanted/test-machine/30s-60p-5ac-sp2.csv','LPS_Bulk','LPS_Bulk_20260928_P060pct_T30s_A05_S12.csv','troubleshooting (orig sp2) - dark contains sample light'),
 ('unwanted/test-machine/SP_6-diffrent.csv','LPS_Bulk','LPS_Bulk_20260928_P060pct_T40s_A05_S06.csv','supporting (orig SP_6-diffrent) - dark contains sample light'),
 ('unwanted/test-machine/SP_7-diffrent.csv','LPS_Bulk','LPS_Bulk_20260928_P060pct_T40s_A05_S07.csv','supporting (orig SP_7-diffrent) - dark contains sample light'),
 ('unwanted/test-machine/SP_4.txtr',IC,'Check_20260928_SP_4_duplicate.txtr','TXTR export of orig SP_4 (duplicate format)'),
 ('unwanted/test-machine/SP_5.txtr',IC,'Check_20260928_SP_5_duplicate.txtr','TXTR export of orig SP_5 (duplicate format)')]
rows=[]
for src,cat,new,role in items:
  s=os.path.join(SRC,src); d=os.path.join(LIB,'01_Raw_Data_Renamed',cat,new); os.makedirs(os.path.dirname(d),exist_ok=True)
  if os.path.exists(d): raise SystemExit('exists '+d)
  shutil.copy2(s,d); rows.append(dict(original=src,category=cat,library_file=new,role=role,md5=md5(s),copy_ok=md5(s)==md5(d)))
inv=pd.DataFrame(rows); print(inv[['original','library_file','copy_ok']].to_string()); inv.to_pickle('lr_inv.pkl')
