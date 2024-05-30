import os
import subprocess
import openvsp as vsp
import shutil
import time

def aero_simulation(working_dir,aero_data, advanced_data):

        vsp.VSPRenew() # API refresh
        stdout = vsp.cvar.cstdout
        errorMgr = vsp.ErrorMgrSingleton.getInstance()           

        for fname in os.listdir(working_dir):
                if fname.endswith(".vsp3"):
                        print("Creating geometry!")
                        
                        #Get name of the .vsp file
                        vspfile = os.path.join(working_dir, os.path.basename(fname))
                        degenfile = os.path.join(working_dir, os.path.splitext(os.path.basename(fname))[0] + ".csv:")
                        print("VSP3: " , vspfile, "\nDegenGeom: ", degenfile)

                        #Opening the VSP file
                        vsp.ReadVSPFile(vspfile)

                        #Setting up DegenGeom
                        vsp.ComputeDegenGeom(vsp.SET_ALL, vsp.DEGEN_GEOM_CSV_TYPE)
                        vsp.SetAnalysisInputDefaults("DegenGeom")
                        vsp.SetIntAnalysisInput("DegenGeom", "WriteCSVFlag", [0], 0)

                        #Creating the DegenGeom
                        vsp.ExecAnalysis("VSPAEROComputeGeometry")
                        
                        print("Starting aerodynamic simulation!")

                        #Setting up the analysis
                        analysis_name = "VSPAEROSweep"
                        vsp.SetAnalysisInputDefaults(analysis_name)

                        #Set Reference
                        wing = vsp.FindGeoms()
                        vsp.SetVSPAERORefWingID(wing[0])

                        #Set Params
                        vsp.SetDoubleAnalysisInput(analysis_name, "MachStart", aero_data["Mach"] )
                        vsp.SetIntAnalysisInput(analysis_name, "MachNpts", [1])
                        
                        vsp.SetDoubleAnalysisInput(analysis_name, "AlphaStart", aero_data["Alpha"])
                        vsp.SetIntAnalysisInput(analysis_name, "AlphaNpts", [1])

                        vsp.SetDoubleAnalysisInput(analysis_name, "BetaStart", aero_data["Beta"])
                        vsp.SetIntAnalysisInput(analysis_name, "BetaNpts", [1])

                        vsp.SetIntAnalysisInput(analysis_name, "WakeNumIter", advanced_data["Iter"])

                        vsp.SetIntAnalysisInput(analysis_name, "Symmetry", advanced_data["Symmetry"])

                        #Start Analysis
                        vsp.ExecAnalysis(analysis_name)
                        print("Aerodynamic simulation finished!")

                errorMgr.PopErrorAndPrint(stdout)
                num_err = errorMgr.GetNumTotalErrors()   #Error check
                for i in range(0,num_err):
                        err = errorMgr.PopLastError()
                        print("error: ", err.m_ErrorString)



def load_application(working_dir, vspdir, aero_data):
    
    #Creating the .bat file for load application
    loadbatloc = os.path.join(working_dir, "load.bat") #batch location
    
    vsploadloc = os.path.join(vspdir,"vsploads.exe")

    for fname in os.listdir(working_dir):
        if fname.endswith(".csv"):
            geom = os.path.join(working_dir, os.path.splitext(os.path.basename(fname))[0])
        if fname.endswith(".inp"):
            calc_input = os.path.join(working_dir, os.path.splitext(os.path.basename(fname))[0])

    #Pressure at sea level
    p = 1.225
    #Mach at sea level
    M = 340.3
    print("Mach",aero_data["Mach"][0])
    dynp = round(0.5 * p * (aero_data["Mach"][0] * M)**2)

    print(dynp)
    print(calc_input)
    #creating a bat file to run vspaero
    fid = open(loadbatloc,"w+")
    fid.write("""@echo off \n"""
           + vsploadloc +""" -interp """ + geom +" "+ calc_input + f""" -dynp {dynp} """ +
          """ \n exit """)
    fid.close()
    #batchfile run
    subprocess.call(loadbatloc)

    

def calculix_base(workdir,ccxpath,calcpath): #creating necessary calculix file
    calcbatloc = os.path.join(workdir, "calculix.bat") #batch location
    #creating a bat file to run vspaero
    fid = open(calcbatloc,"w+")
    fid.write("""@echo on \n"""
               + ccxpath +" "+ calcpath +
          #C:\\SZTAKI\\bConverged\\CalculiX\\ccx\\ccx.exe C:\SZTAKI\OpenVSP_Toolbox\TEST_2\Test_1_WingGeom_Struct0_calculix.static.inp
          """\n exit""")
    fid.close()
    subprocess.call(calcbatloc)

def calculix_static(working_dir,ccxpath):

    calcstaticbatloc = os.path.join(working_dir, "calculixstatic.bat") #batch location
    for fname in os.listdir(working_dir):
        if fname.endswith(".static.inp"):
            calc_stat = os.path.join(working_dir, os.path.splitext(os.path.basename(fname))[0])
    
    fid = open(calcstaticbatloc,"w+")
    fid.write("""@echo on\n """
               + ccxpath +" "+ calc_stat +
          """ \n exit""")
    fid.close()
    subprocess.call(calcstaticbatloc)

def calculix_buckle(working_dir,ccxpath):
    calcbucklebatloc = os.path.join(working_dir, "calculixbuckle.bat") #batch location
    for fname in os.listdir(working_dir):
        if fname.endswith(".static.inp"):
            calc_buckle = os.path.join(working_dir, os.path.splitext(os.path.basename(fname))[0])

    fid = open(calcbucklebatloc,"w+")
    fid.write("""@echo on \n """
               + ccxpath +" "+ calc_buckle +
          """\n exit""")
    fid.close()
    subprocess.call(calcbucklebatloc)

def calculix_export(workdir):
    for fname in os.listdir(workdir):
        if fname.endswith(".frd"):
            print("Results found")
            result_loc = os.path.join(workdir, os.path.basename(fname))

    calc_export = os.path.join(workdir, "export.fbd") #batch location
    fid = open(calc_export,"w+")
    fid.write("read " + result_loc + "\n" +
              "send all abq \nsend all abq ds1 \nquit")
    fid.close()
    os.startfile(calc_export)

def move_file(workdir):
    for fname in os.listdir(os.getcwd()):
        if fname == "all.msh":
            shutil.move(fname, workdir)
            mesh = os.path.join(workdir,fname)
        elif fname == "all_ds1.dat":
            shutil.move(fname, workdir)
            disp = os.path.join(workdir,fname)
    print(mesh, disp)
    return mesh, disp

def move_vsp(workdir):
     for fname in os.listdir(os.getcwd()):
        if fname == "def_wing.vsp3":
            shutil.move(fname, workdir)
            os.path.join(workdir,fname)
