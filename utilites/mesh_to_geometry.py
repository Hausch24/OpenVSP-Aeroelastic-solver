import csv
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
import openvsp as vsp
import math
from mpl_toolkits.mplot3d import Axes3D

def LE_TE_find(mesh, displacement, scale = None, slice = None, fig = None):
    #mesh coordinates
    x_coords = []
    y_coords = []
    z_coords = []

    #set default value for scale and slice
    if scale is None:
        scale = 5
    if slice is None:
        slice = 30  
    if fig is None:
        fig = False

    with open(mesh, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        coordinates = [row[1:] for row in reader if len(row) == 4]
        for coord in coordinates:
            x_coords.append(float(coord[0]))
            y_coords.append(float(coord[1]))
            z_coords.append(float(coord[2]))

    #Mesh coordinates without deformation
    x = np.array(x_coords)
    y = np.array(y_coords)
    z = np.array(z_coords)
    span = max(y)

    #deformation
    x_def = []
    y_def = []
    z_def = []

    with open(displacement, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        coordinates = [row[1:] for row in reader if len(row) == 3]
        for coord in coordinates:

            if coord[0] == "1":
                x_def.append(float(coord[1]) * scale)
            if coord[0] == "2":
                y_def.append(float(coord[1]) * scale)
            if coord[0] == "3":
                z_def.append(float(coord[1]) * scale)

    x_def = np.array(x_def)
    y_def = np.array(y_def)
    z_def = np.array(z_def)

    #Mesh coordinates with deformation
    x_def_coord = np.add(x,x_def)
    y_def_coord = np.add(y,y_def)
    z_def_coord = np.add(z,z_def)

    #Reshaping the coordinate arrays to a matrix form
    def_mesh_coord = np.column_stack((x_def_coord,y_def_coord,z_def_coord))
    y_max = np.argmax(def_mesh_coord[:, 1])
    y_max_row = def_mesh_coord[y_max]

    #print(def_mesh_coord)

    LE = []
    TE = []
    
    #taking a step from 0 to the end of the wing.
    for i in np.arange(0, y_max_row[1]+y_max_row[1]/slice, y_max_row[1]/slice):
        slices = []

        #Look through the coordinates
        for n in def_mesh_coord:

            #Find elements within the threshold
            if n[1] >= (i - 0.1) and n[1] <= (i + 0.1):
        
                slices.append(n)
                print(slices)
        #Matrix form
        slices = np.stack(slices)

        #Find leading edge and trailing edge
        LE.append(slices[np.argmin(slices[:,0])])
        TE.append(slices[np.argmax(slices[:,0])])

    LE = np.stack(LE)
    TE = np.stack(TE)

    #for plot
    LE_x = [LE[n][0] for n in range(len(LE))]
    LE_y = [LE[n][1] for n in range(len(LE))]
    LE_z = [LE[n][2] for n in range(len(LE))]

    TE_x = [TE[n][0] for n in range(len(TE))]
    TE_y = [TE[n][1] for n in range(len(TE))]
    TE_z = [TE[n][2] for n in range(len(TE))]

    LE_coord = [LE_x,LE_y,LE_z]
    TE_coord = [TE_x,TE_y,TE_z] 
    if fig:
        fig1 = plt.figure(1)
        ax = fig1.add_subplot(projection='3d')
        ax.scatter(x, y, z)
        ax.scatter(x_def_coord,y_def_coord,z_def_coord)
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        ax.set_zlim(-20, 20)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.show()

        fig2 = plt.figure()
        ax = fig2.add_subplot(111, projection='3d')
        ax.plot(LE_x,LE_y,LE_z)
        ax.plot(TE_x,TE_y,TE_z)

        # Set labels and title
        ax.set_xlabel('X-axis')
        ax.set_ylabel('Y-axis')
        ax.set_zlabel('Z-axis')
        

        # Show plot
        plt.show()

    return(LE_coord, TE_coord, span)



def deformed_geoemtry(LE_coord, TE_coord, span, advanced_data, FR = None, fig = None, step = None ):

    #Setting up default values
    if step is None:
        step = 0.1

    if FR is None:
        FR = 5

    if fig is None:
        fig = False
    
    #Y-Z, dihedral
    #Curve fitting
    def polynomial_func(x, a, b, c):
        return a * x**2 + b * x + c
 
    #Leading edge
    popt, pcov = curve_fit(polynomial_func, LE_coord[1], LE_coord[2])
    
    LE_y_fit_dehidral = np.linspace(max(LE_coord[1]), 0, 100)
    LE_z_fit_dehidral = polynomial_func(LE_y_fit_dehidral, *popt)
    LE_x_fit_dehidral = np.zeros(100)

    #Trailing edge
    popt, pcov = curve_fit(polynomial_func, TE_coord[1], TE_coord[2])

    TE_y_fit_dehidral = np.linspace(max(TE_coord[1]), 0, 100)
    TE_z_fit_dehidral = polynomial_func(TE_y_fit_dehidral, *popt)
    TE_x_fit_dehidral = np.zeros(100)

    mean_y = np.mean((LE_y_fit_dehidral,TE_y_fit_dehidral), axis=0)
    mean_z = np.mean((LE_z_fit_dehidral,TE_z_fit_dehidral), axis=0)

    popt, pcov = curve_fit(polynomial_func, mean_y, mean_z)
    mean_y_fit = np.linspace(max(mean_y), 0, 100)
    mean_z_fit = polynomial_func(mean_y_fit, *popt)
    mean_x_fit = np.zeros(100)
    a, b, c = popt

    #X-Y, sweep
    popt, pcov = curve_fit(polynomial_func, LE_coord[0], LE_coord[1])

    LE_x_fit_sweep = np.linspace(min(LE_coord[0]), max(LE_coord[0]), 100)
    LE_y_fit_sweep = polynomial_func(LE_x_fit_sweep, *popt)
    LE_z_fit_sweep = np.zeros(100)
    
    #sweep angle
    theta =  []
    for n in range(99):
        theta.append(math.degrees(math.atan((LE_x_fit_sweep[n+1]-LE_x_fit_sweep[n])/(LE_y_fit_sweep[n+1]-LE_y_fit_sweep[n]))))

    theta = [theta[n] for n in range(0, len(theta), round(len(theta)/FR))]

    popt, pcov = curve_fit(polynomial_func, TE_coord[0], TE_coord[1])

    TE_x_fit_sweep = np.linspace(min(TE_coord[0]), max(TE_coord[0]), 100)
    TE_y_fit_sweep = polynomial_func(TE_x_fit_sweep, *popt)
    TE_z_fit_sweep = np.zeros(100)

    #Samplinng the curve fit
    root_c = [TE_x_fit_sweep[n]-LE_x_fit_sweep[n] for n in range(100)] 

    root_c = [root_c[n] for n in range(0, len(root_c), round(len(root_c)/FR))]
    
    #Twist   
    LE_z_fit_twist = [LE_z_fit_dehidral[n] for n in range(0, 100, round(100/FR))]
    TE_z_fit_twist = [TE_z_fit_dehidral[n] for n in range(0, 100, round(100/FR))]
    delta_z_twist = [TE_z_fit_twist[n] - LE_z_fit_twist[n] for n in range(len(LE_z_fit_twist))]

    LE_x_fit_twist = [LE_x_fit_sweep[n] for n in range(0, 100, round(100/FR))]
    TE_x_fit_twist = [TE_x_fit_sweep[n] for n in range(0, 100, round(100/FR))]  
    delta_x_twist = [LE_x_fit_twist[n]-TE_x_fit_twist[n] for n in range(len(LE_x_fit_twist))]

    phi = [math.degrees(math.atan(delta_z_twist[n]/delta_x_twist[n])) for n in range(len(delta_x_twist))]

    #Dihedral angle
    x = list(np.arange(0, span * 2 + step, step))                 #Start always 0, Stop = WingSpan + Step
    y = [a * n**2 + b * n + c for n in x]

    #Curve segmentation
    chunks_x = []
    chunks_y = []

    if len(x) % FR == 0:
        chunk_size = int(len(x) / FR)
        for n in np.arange(0, len(x), chunk_size):
            chunk = x[n:n+chunk_size]
            chunks_x.append(chunk)

        for n in np.arange(0, len(x), chunk_size):
            chunk = y[n:n+chunk_size]
            chunks_y.append(chunk)
    else:
        chunk_size = len(x) // FR
        remainder = len(x) % FR
        for i in range(FR):
            start = i * chunk_size
            end = (i + 1) * chunk_size
            chunk_x = x[start:end]
            chunk_y = y[start:end]
            chunks_x.append(chunk_x)
            chunks_y.append(chunk_y)
        
        # remainders
        chunks_x[-1] += x[-remainder:]
        chunks_y[-1] += y[-remainder:]
    #If cannot be devided equally, last chuck will have less elements
        print("Inequal")

    #List of dehidral angles
    gamma = []                  

    #Only one element in the last chunk
    if len(chunks_x[-1]) == 1:
        for n in range(len(chunks_x)-1):
            x_1 = chunks_x[n][0]
            x_2 = chunks_x[n+1][0]
            y_1 = chunks_y[n][0]
            y_2 = chunks_y[n+1][0]
            print("x: ", x_1 , x_2 , "y: ", y_1, y_2)
            gamma.append(math.degrees(math.atan((y_2-y_1)/(x_2-x_1))))

    else:
        for n in range(len(chunks_x)-1): #len chunks 5-1
            x_1 = chunks_x[n][0]
            x_2 = chunks_x[n+1][0]
            y_1 = chunks_y[n][0]
            y_2 = chunks_y[n+1][0]
            gamma.append(math.degrees(math.atan((y_2-y_1)/(x_2-x_1))))
        x_1 = chunks_x[len(chunks_x)-1][0]
        x_2 = chunks_x[len(chunks_x)-1][-1]
        y_1 = chunks_y[len(chunks_x)-1][0]
        y_2 = chunks_y[len(chunks_x)-1][-1]
        gamma.append(math.degrees(math.atan((y_2-y_1)/(x_2-x_1))))

    gamma_mod = [gamma[0]]
    for n in range(1,len(gamma)):
        gamma_mod.append(gamma[n]-gamma[n-1])

    #OPENVSP API WING GENERATION
    #API referesh
    vsp.VSPRenew() 
    stdout = vsp.cvar.cstdout
    errorMgr = vsp.ErrorMgrSingleton.getInstance()

    #Creating a default wing
    wing_ID = vsp.AddGeom("WING")

    #Adding a XSEC
    for n in range(FR-1):
        vsp.InsertXSec(wing_ID, n+1, vsp.XS_FOUR_SERIES)

    #Setting up parms for XSEC bend
    for n in range(FR):
        vsp.SetParmVal(wing_ID, "Span", f"XSec_{n+1}", span / FR)
        vsp.SetParmVal(wing_ID,"Dihedral",f"XSec_{n+1}", gamma[n])
        vsp.SetParmVal(wing_ID,"Sweep",f"XSec_{n+1}", theta[n])
        vsp.SetParmVal(wing_ID,"Twist",f"XSec_{n+1}", phi[n])
        vsp.SetParmVal(wing_ID,"Root_Chord",f"XSec_{n+1}", root_c[n])
        vsp.SetParmVal(wing_ID,"ThickChord",f"XSecCurve_{n}", advanced_data["TC"][0])
        vsp.SetParmVal(wing_ID,"Camber",f"XSecCurve_{n}", advanced_data["Camber"][0])
        vsp.Update()

    #Writing the .vsp3 file
    vsp.WriteVSPFile("def_wing.vsp3")

    if fig:

        fig, ax = plt.subplots()
        ax.plot(x, y)
        ax.grid()
        ax.set(title="Test function")

        fig2 = plt.figure(2)
        ax = fig2.add_subplot(projection='3d')
        ax.plot(LE_coord[0], LE_coord[1], LE_coord[2])
        ax.plot(TE_coord[0], TE_coord[1], TE_coord[2])
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        ax.set_zlim(-20, 20)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')

        fig3 = plt.figure(3)
        ax = fig3.add_subplot()
        ax.plot(LE_y_fit_dehidral, LE_z_fit_dehidral, label = "Fitted curve")
        ax.plot(LE_coord[1], LE_coord[2], label = "Original Data")
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        plt.title('Leading Edge curve fitting')
        plt.xlabel('Y-axis')
        plt.ylabel('Z-axis')
        plt.legend() 
        plt.grid(True)

        fig4 = plt.figure(4)
        ax = fig4.add_subplot()
        ax.plot(TE_y_fit_dehidral, TE_z_fit_dehidral, label = "Fitted curve")
        ax.plot(TE_coord[1], TE_coord[2], label = "Original Data")
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        plt.title('Trailing edge curve fitting')
        plt.xlabel('Y-axis')
        plt.ylabel('Z-axis')
        plt.legend()
        plt.grid(True)

        fig5 = plt.figure(5)
        ax = fig5.add_subplot()
        ax.plot(TE_y_fit_dehidral, TE_z_fit_dehidral, label = "Fitted TE curve")
        ax.plot(LE_y_fit_dehidral, LE_z_fit_dehidral, label = "Fitted LE curve")
        ax.plot(mean_y_fit,mean_z_fit,label = "Mean fitted curve")
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        plt.title('Mean curve')
        plt.xlabel('Y-axis')
        plt.ylabel('Z-axis')
        plt.legend()
        plt.grid(True)

        fig6 = plt.figure(6)
        ax = fig6.add_subplot()
        ax.plot(LE_y_fit_sweep, LE_x_fit_sweep, label = "Fitted curve")
        ax.plot(LE_coord[1], LE_coord[0], label = "Original Data")
        ax.plot(TE_y_fit_sweep, TE_x_fit_sweep, label = "Fitted curve")
        ax.plot(TE_coord[1], TE_coord[0], label = "Original Data")
        ax.set_xlim(-20, 20)
        ax.set_ylim(-20, 20)
        plt.title('LE and TE curve fitting')
        plt.xlabel('Y-axis')
        plt.ylabel('X-axis')
        plt.legend() 
        plt.grid(True)

        plt.show()

