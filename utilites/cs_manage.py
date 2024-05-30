import openvsp as vsp
import os 


def add_cs(working_dir, cs_number, cs_data, cs_id_lst):

    vsp.VSPRenew() # API refresh
    stdout = vsp.cvar.cstdout
    errorMgr = vsp.ErrorMgrSingleton.getInstance()
    for fname in os.listdir(working_dir):
        if fname.endswith(".vsp3"):
            vspfile = os.path.join(working_dir, os.path.basename(fname))

    vsp.ReadVSPFile(vspfile)

    wing = vsp.FindGeoms()
    
    cs_id = vsp.AddSubSurf(wing[0], vsp.SS_CONTROL)
    cs_id_lst.append(cs_id)

    vsp.SetParmVal(wing[0], "EtaFlag", f"SS_Control_{cs_number}", 1)
    vsp.SetParmVal(wing[0], "EtaStart", f"SS_Control_{cs_number}",  cs_data["Start"])
    vsp.SetParmVal(wing[0], "EtaEnd", f"SS_Control_{cs_number}", cs_data["End"])
    vsp.SetParmVal(wing[0], "Length_C_Start", f"SS_Control_{cs_number}", cs_data["Length"])
    print("Control surface added!")


    vsp.AutoGroupVSPAEROControlSurfaces()
    vsp.Update

    cg_container_id = vsp.FindContainer("VSPAEROSettings", 0)
    vsp.SetParmVal(vsp.FindParm(cg_container_id, "DeflectionAngle", f"ControlSurfaceGroup_{cs_number-1}"),cs_data["Deflection"])
    vsp.Update()
    vsp.WriteVSPFile(vspfile, 0)

    errorMgr.PopErrorAndPrint(stdout)
    num_err = errorMgr.GetNumTotalErrors()
    for i in range(0,num_err):
        err = errorMgr.PopLastError()
        print("error: ", err.m_ErrorString)
    print(cs_id_lst)
    return (cs_id_lst)

def add_deflection(working_dir, cs_number, cs_data, cs_id_lst):
    vsp.VSPRenew() # API refresh
    stdout = vsp.cvar.cstdout
    errorMgr = vsp.ErrorMgrSingleton.getInstance()
    for fname in os.listdir(working_dir):
        if fname.endswith(".vsp3"):
            vspfile = os.path.join(working_dir, os.path.basename(fname))

    vsp.ReadVSPFile(vspfile)

    wing = vsp.FindGeoms()

    #vsp.AutoGroupVSPAEROControlSurfaces()
    vsp.Update

    cg_container_id = vsp.FindContainer("VSPAEROSettings", 0)
    vsp.SetParmVal(vsp.FindParm(cg_container_id, "DeflectionAngle", f"ControlSurfaceGroup_{cs_number-1}"),cs_data["Deflection"])
    vsp.Update()
    vsp.WriteVSPFile(vspfile, 0)

    errorMgr.PopErrorAndPrint(stdout)
    num_err = errorMgr.GetNumTotalErrors()
    for i in range(0,num_err):
        err = errorMgr.PopLastError()
        print("error: ", err.m_ErrorString)

def delete_cs(working_dir, cs_number, cs_id_lst):
    vsp.VSPRenew() # API refresh
    stdout = vsp.cvar.cstdout
    errorMgr = vsp.ErrorMgrSingleton.getInstance()
    for fname in os.listdir(working_dir):
        if fname.endswith(".vsp3"):
            vspfile = os.path.join(working_dir, os.path.basename(fname))

    vsp.ReadVSPFile(vspfile)
    wing = vsp.FindGeoms()
    
    vsp.DeleteSubSurf(wing[0], cs_id_lst[cs_number])
    cs_id_lst.pop()
    vsp.WriteVSPFile(vspfile)
    print(cs_id_lst)
    errorMgr.PopErrorAndPrint(stdout)
    num_err = errorMgr.GetNumTotalErrors()
    for i in range(0,num_err):
        err = errorMgr.PopLastError()
        print("error: ", err.m_ErrorString)