from __future__ import annotations
import json, tkinter as tk
from pathlib import Path
APP_DIR=Path(__file__).resolve().parent
ASSET_DIR=APP_DIR/'brand_assets'
CONFIG_PATH=ASSET_DIR/'brand_config.json'

def config():
    return json.loads(CONFIG_PATH.read_text(encoding='utf-8'))

def photo(path,master):
    try:return tk.PhotoImage(master=master,file=str(path))
    except tk.TclError:return None

def manager(root):
    for c in root.winfo_children():
        if c.winfo_manager() in {'pack','grid'}:return c.winfo_manager()
    return ''

def add_header(root):
    if getattr(root,'_certiaura_header',None):return
    cfg=config(); col=cfg['palette']; mgr=manager(root)
    frame=tk.Frame(root,bg=col['pearl'],highlightthickness=1,highlightbackground=col['silver'])
    img=photo(ASSET_DIR/cfg['header_image'],root)
    if img:
        lab=tk.Label(frame,image=img,bg=col['pearl']); lab.image=img; lab.pack(side='left',padx=(16,8),pady=6)
    else:
        tk.Label(frame,text='CertiAura',bg=col['pearl'],fg=col['deep_navy'],font=('Segoe UI',20,'bold')).pack(side='left',padx=18,pady=15)
    tk.Frame(frame,width=1,bg=col['silver']).pack(side='left',fill='y',padx=12,pady=16)
    block=tk.Frame(frame,bg=col['pearl']); block.pack(side='left',fill='both',expand=True,padx=8,pady=12)
    tk.Label(block,text='PROJECT GENESIS',bg=col['pearl'],fg=col['midnight_navy'],font=('Segoe UI',23,'bold'),anchor='w').pack(fill='x')
    tk.Label(block,text='CertiAura Repository Manager v1.2.0',bg=col['pearl'],fg=col['aura_violet'],font=('Segoe UI',10,'bold'),anchor='w').pack(fill='x')
    tk.Frame(frame,width=9,bg=col['aura_cyan']).pack(side='right',fill='y')
    if mgr=='grid':
        for c in list(root.winfo_children()):
            if c is frame or c.winfo_manager()!='grid':continue
            info=c.grid_info(); c.grid_configure(row=int(info.get('row',0))+1)
        frame.grid(row=0,column=0,columnspan=50,sticky='ew')
    else:
        kids=[c for c in root.winfo_children() if c is not frame and c.winfo_manager()=='pack']
        kw={'side':'top','fill':'x'}
        if kids:kw['before']=kids[0]
        frame.pack(**kw)
    root._certiaura_header=frame

def add_footer(root):
    if getattr(root,'_certiaura_footer',None):return
    cfg=config(); col=cfg['palette']; mgr=manager(root)
    frame=tk.Frame(root,bg=col['midnight_navy'])
    tk.Label(frame,text=cfg['tagline'],bg=col['midnight_navy'],fg=col['silver'],font=('Segoe UI',8)).pack(fill='x',pady=6)
    if mgr=='grid':
        rows=[]
        for c in root.winfo_children():
            if c is frame or c.winfo_manager()!='grid':continue
            try:rows.append(int(c.grid_info().get('row',0)))
            except:pass
        frame.grid(row=max(rows+[0])+1,column=0,columnspan=50,sticky='ew')
    else:frame.pack(side='bottom',fill='x')
    root._certiaura_footer=frame

def apply(root):
    cfg=config(); root.title(cfg['application_title']); root.option_add('*Font','Segoe UI 10')
    img=photo(ASSET_DIR/cfg['icon_png'],root)
    if img:
        try:root.iconphoto(True,img); root._certiaura_icon=img
        except tk.TclError:pass
    add_header(root); add_footer(root)

def schedule(root,retries=12):
    def go(n):
        try:
            root.update_idletasks()
            if root.winfo_children() or n<=0:return apply(root)
            root.after(100,lambda:go(n-1))
        except tk.TclError:return
    root.after_idle(lambda:go(retries))
