# set parameters 
# example Using Larch with python3

import larch_plugins as lp
# library containign functions that read and write to csv files
import lib.handle_csv as csvhandler
# regular expression matching
import re
# display editable spreadsheet
import ipysheet
# File handling
from pathlib import Path
#library for writing to log
import logging

# read parameters from csv file
# each line contains a parameter defined as follows
##############################
# id,name,value,expr,vary
# 1,alpha,1e-07,,True
# 2,ss2,0.003,,True
# 3,ss3,0.003,ss2,False
# 4,ssfe,0.003,,True
##############################
def read_gds(gds_file, session):
    gds_pars, _ = csvhandler.read_csv_data(gds_file)
    dgs_group = dict_to_gds(gds_pars, session)
    return dgs_group

# save parameters from csv file
# each line contains a parameter defined as follows
##############################
# id,name,value,expr,vary
# 1,alpha,1e-07,,True
# 2,ss2,0.003,,True
# 3,ss3,0.003,ss2,False
# 4,ssfe,0.003,,True
##############################
def save_gds(gds_group, gds_file):
    # convert gds group to dictionary
    gds_data = gds_to_dict(gds_group)
    csvhandler.write_csv_data(gds_data,gds_file)

# take gds group data and convert it to a dictionary
def gds_to_dict(gds_group):
    gds_params = gds_group.__params__
    gds_count = 1
    data_dict = {}
    for par in gds_params:
        data_dict[gds_count] = {'id': gds_count,
                               'name':par,
                               'value':gds_params[par].value,
                               'expr':gds_params[par].expr,
                               'vary':gds_params[par].vary
                              }
        gds_count += 1
    return data_dict

# take data from dictionary and create a gds group
def dict_to_gds(data_dict, session):
    dgs_group = lp.fitting.param_group(_larch=session)
    for par_idx in data_dict:
        #gds file structure:
        gds_name = data_dict[par_idx]['name']
        gds_val = 0.0
        gds_expr = ""
        try:
            gds_val = float(data_dict[par_idx]['value'])
        except ValueError:
            #print("Not a float value")
            gds_val = 0.00
        gds_expr = data_dict[par_idx]['expr']
        gds_vary = True if str(data_dict[par_idx]['vary']).strip().capitalize() =='True' else False
        one_par = None
        if gds_vary:
            # equivalent to a guess parameter in Demeter
            one_par = lp.fitting.guess(name=gds_name ,value=gds_val, vary=gds_vary, expr=gds_expr)
        else:
            # equivalent to a defined parameter in Demeter
            one_par = lp.fitting.param(name=gds_name ,value=gds_val, vary=gds_vary, expr=gds_expr)
        if one_par != None:
            dgs_group.__setattr__(gds_name,one_par)
    return dgs_group

# take gds group data and convert it to a list of lists
def gds_to_list(gds_group):
    gds_params = gds_group.__params__
    gds_count = 1
    data_list = [['id','name','value','expr','vary']]
    for par in gds_params:
        new_par = [gds_count, par, gds_params[par].value,
                   gds_params[par].expr, gds_params[par].vary]
        data_list.append(new_par)
        gds_count += 1
    return data_list

# show gds parameters in a spreadsheet
def show_gds(gds_group):
    gds_list = gds_to_list(gds_group)
    #print(gds_list)
    #add 10 more rows in case we need more parameters
    for i in range(10):
        gds_list.append([(len(gds_list)-1)+1,None,None,None,None])
    a_sheet = ipysheet.sheet(rows=len(gds_list), columns=len(gds_list[0]))
    ipysheet.cell_range(gds_list)
    display(a_sheet)
    return a_sheet

# get data from spreadsheet and build a gds group
def spreadsheet_to_gds(a_sheet, session):
    df_sheet = ipysheet.to_dataframe(a_sheet).transpose()
    data_dict = {}
    gds_count = 1
    for col in df_sheet:
        if df_sheet[col][0] != 'id':
            if (not df_sheet[col][1] in [None,""]) and (not df_sheet[col][2] in [None,""]) and (not df_sheet[col][4] in [None,""]):
                #print(df_sheet[col][0],df_sheet[col][1],df_sheet[col][2],df_sheet[col][3],df_sheet[col][4])
                data_dict[gds_count] = {'id': df_sheet[col][0],
                                       'name':df_sheet[col][1],
                                       'value':df_sheet[col][2],
                                       'expr':df_sheet[col][3],
                                       'vary':df_sheet[col][4]
                                      }
            gds_count+=1
    #print(data_dict)
    gds_gp = dict_to_gds(data_dict, session)
    return gds_gp


# show the paths stored in path files in the FEFF directory.
# These paths are stored by feff in the files.dat file
def show_feff_paths(var = "FeS2.inp"):
    crystal_f = Path(var)
    feff_dir = crystal_f.name[:-4]+"_feff"
    feff_inp = crystal_f.name[:-4]+"_feff.inp"
    feff_files = "files.dat"
    input_file = Path(feff_dir, feff_files)
    #check if feff dir exists
    if input_file.parent.exists() and input_file.exists():
        logging.info(str(input_file.parent) + " path and "+ str(input_file)+ " found")
    else:
        logging.info(str(input_file.parent) + " path not found, run feff before running select paths")
        return False
    count = 0
    # the .dat data is stored in fixed width strings 
    field_widths = [[0,13],[14,21],[22,31],[32,41],[42,48],[49,61]]
    is_meta = True
    data_headers = []
    path_count = 0
    paths_data = []
    logging.info("Reading from: "+ str(input_file))
    with open(input_file) as datfile:
        dat_lines = datfile.readlines()
        for a_line in dat_lines:
            count += 1
            if re.match('-*', a_line.strip()).group(0)!= '':
                is_meta = False
                logging.info("{}: {}".format(count, a_line.strip()))
            elif is_meta:
                logging.info("{}: {}".format(count, a_line.strip()))
            elif data_headers == []:
                data_headers = [a_line[s:e].strip().replace(' ','_') for s,e in field_widths]
                logging.info("headers:"+ str(data_headers))
                data_headers.append('select')
                paths_data.append(data_headers)
            else:
                path_count += 1
                data_values = [a_line[s:e].strip() for s,e in field_widths]
                data_values.append(0)
                data_values[0] = feff_dir+"/"+data_values[0]
                paths_data.append(data_values)
    # use data to populate spreadsheet
    
    path_sheet = ipysheet.sheet(rows=path_count+1, columns=7)
    ipysheet.cell_range(paths_data)
    return path_sheet

def show_selected_paths(pats_sheet):
    df_sheet = ipysheet.to_dataframe(pats_sheet)
    files = []
    for f_name, selected in zip(df_sheet["A"], df_sheet["G"]):
        if selected == '1':
            files.append(f_name)    

    sel_paths_data = [[0 for col in range(6)] for row in range(4)]
    sel_paths_data[:0]=[['file','label','s02','e0','sigma2','deltar']]
    ps_row = 1
    for a_name in files:
        sel_paths_data[ps_row][0] = a_name
        ps_row += 1

    sp_sheet = ipysheet.sheet(rows=len(files)+1, columns=6)
    ipysheet.cell_range(sel_paths_data)
    display(sp_sheet)
    return sp_sheet

# use data frame to create selected paths list
def build_selected_paths_list(sp_sheet, session):
    df_sheet = ipysheet.to_dataframe(sp_sheet).transpose()
    sp_list = []
    for col in df_sheet:
        if df_sheet[col][0] != 'file':
            new_path = lp.xafs.FeffPathGroup(filename = df_sheet[col][0],
                                             label    = df_sheet[col][1],
                                             s02      = df_sheet[col][2],
                                             e0       = df_sheet[col][3],
                                             sigma2   = df_sheet[col][4],
                                             deltar   = df_sheet[col][5],
                                             _larch   = session)
            sp_list.append(new_path)
    return sp_list

def save_selected_paths_list(sp_sheet, f_prefix = "FeS2"):
    # it is easier to transpose as dataframes main objects are columns
    df_sheet = ipysheet.to_dataframe(sp_sheet).transpose()
    sp_list = {}
    path_count = 1
    for col in df_sheet:
        if df_sheet[col][0] != 'file':
            sp_list[path_count] = {'id': path_count,
                                   'filename':df_sheet[col][0],
                                   'label':df_sheet[col][1],
                                   's02':df_sheet[col][2],
                                   'e0':df_sheet[col][3],
                                   'sigma2':df_sheet[col][4],
                                   'deltar':df_sheet[col][5]}
            path_count += 1
    print(sp_list)
    file_name = f_prefix+"_sp.csv"
    csvhandler.write_csv_data(sp_list,file_name)