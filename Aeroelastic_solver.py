import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + '/utilites')

#Module import
import functions as func
import settings 
import PySimpleGUI as sg
import subprocess
import mesh_to_geometry as mg
import time

def main():
    sg.theme("Default1")
# sg.In and sg.FileBrowse elements
    input_elements = [
    [
        sg.Text("Working directory     "),
        sg.In(size=(25, 1), enable_events=True, key="-WD-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("OpenVSP directory   "),
        sg.In(size=(25, 1), enable_events=True, key="-VSPD-"),
        sg.FolderBrowse(),
    ],
    [
        sg.Text("Calculix CCX location"),  
        sg.In(size=(25, 1), enable_events=True, key="-CCX-"),
        sg.FileBrowse(),
    ],
    [
        sg.Text("Calculix CGX location"),
        sg.In(size=(25, 1), enable_events=True, key="-CGX-"),
        sg.FileBrowse(),
    ],
    ]
    button_elements= [
        [
            sg.Button("Settings",key="setup")
        ],
        [
            sg.Button("Start Solver",key="start")
        ],
        ]
        
    checkbox_elements= [
        [
            sg.Checkbox("Static",key="static",default=True)
        ],
        [
            sg.Checkbox("Buckle (experimental)",key="buckle",default=False)
        ],
        [
            sg.Checkbox("Single Pass Solution",key="single_pass",default=True)
        ]
    ]
    # ----- Full layout -----
    layout_main = [
        [

            sg.Column(input_elements)
        ],
        [
            sg.Column(button_elements),
            sg.Column(checkbox_elements)
        ]
    ]

    
    window_main = sg.Window("Aeroelastic Solver", layout_main)
    # Run the Event Loop
    while True:
        event, values = window_main.read()
        #geompath = values["-GEOMFILE-"]            #Path to the geometry file
        ccxpath = values["-CCX-"]              #Path CCX.exe
        cgxpath = values["-CGX-"]                   #Path of CGX.exe
        #calcpath = values["-CALCULIX_INP-"]        #Path to the calculix input file
        work_dir = values["-WD-"]                    #Working directory
        vsp_dir = values["-VSPD-"]
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        #Calculationcs
        if event == "start":
            if values["single_pass"] == True:
                # Single pass solver
                func.aero_simulation(work_dir,aero_data,advanced_data)

                #MESH GENERATING 

                func.load_application(work_dir,vsp_dir, aero_data)

                if values["static"] == True:
                    func.calculix_static(work_dir,ccxpath)
                if values["buckle"] == True:
                    func.calculix_buckle(work_dir,ccxpath)

                func.calculix_export(work_dir)
                mesh, disp = func.move_file(work_dir)
                LE_coord, TE_coord, span = mg.LE_TE_find(mesh, disp)
                mg.deformed_geoemtry(LE_coord, TE_coord, span, advanced_data)
                func.move_vsp(work_dir)

            else:
                #Iteration solver
                #Filecheck
                #Setup_rename
                #while 
                    #Aerosim
                    #Load_App
                    #Calculix
                    #Geomgeneration
                pass
        #Setup file create
        if event == "setup":
            aero_data, mesh_data, advanced_data = settings.window_vsp_data(work_dir)
            print(aero_data, mesh_data, advanced_data)


        
    window_main.close()


main()

