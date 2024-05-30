import PySimpleGUI as sg
import functions as func
import cs_manage

def window_vsp_data(working_dir):
 # Aero
    aero_text_elements = [
        [sg.Text("Alpha")],
        [sg.Text("Beta")],
        [sg.Text("Mach")],
    ]

    aero_input_elements = [
        [sg.In(default_text="0", size=(25, 1), enable_events=True, key="-alpha-")],
        [sg.In(default_text="0", size=(25, 1), enable_events=True, key="-beta-")],
        [sg.In(default_text="0.5", size=(25, 1), enable_events=True, key="-mach-")],
    ]

    # Control Surface
    cs_text_elements = [
        [sg.Text("Start")],
        [sg.Text("End")],
        [sg.Text("Length/C")],
        [sg.Text("Deflection")],
        [sg.Text("CS number")]
    ]

    cs_input_elements = [
        [sg.In(default_text="0.1", size=(25, 1), enable_events=True, key="-cs_start-")],
        [sg.In(default_text="0.9", size=(25, 1), enable_events=True, key="-cs_end-")],
        [sg.In(default_text="0.25", size=(25, 1), enable_events=True, key="-cs_length-")],
        [sg.In(default_text="0", size=(25, 1), enable_events=True, key="-cs_deflection-")],
        [sg.Text(size=(15,1), key='-cs_number-')]
    ]

    # Mesh
    mesh_text_elements = [
        [sg.Text("Max element")],
        [sg.Text("Min element")],
        [sg.Text("Max gap")],
        [sg.Text("Growth Ratio")]
    ]

    mesh_input_elements = [
        [sg.In(default_text="100", size=(25, 1), enable_events=True, key="-max_element-")],
        [sg.In(default_text="20", size=(25, 1), enable_events=True, key="-min_element-")],
        [sg.In(default_text="1", size=(25, 1), enable_events=True, key="-max_gap-")],
        [sg.In(default_text="1", size=(25, 1), enable_events=True, key="-growth_ratio-")],
    ]

    button_elements= [
        [
            sg.Button("Save", key="save")
        ]
    ]
    advanced_text_elements = [
        [sg.Text("Camber")],
        [sg.Text("T/C")],
        [sg.Text("Symmetry")],
        [sg.Text("Iter")],
    ]

    advanced_input_elements = [
        [sg.In(default_text="0.014", size=(25, 1), enable_events=True, key="-Camber-")],
        [sg.In(default_text="0.22", size=(25, 1), enable_events=True, key="-TC-")],
        [sg.In(default_text="0", size=(25, 1), enable_events=True, key="-Symmetry-")],
        [sg.In(default_text="5", size=(25, 1), enable_events=True, key="-Iter-")],
    ]


    # Add blank rows to start each layout at the same height
    layout_aero = [
        [sg.Column(aero_text_elements), sg.Column(aero_input_elements)]
    ]

    layout_cs = [
        [sg.Column(cs_text_elements), sg.Column(cs_input_elements)],
        [sg.Button("Add Control Surface" , key = "add_cs"),sg.Button("Delete Control Surface", key = "delete_cs")]
    ]

    layout_mesh = [
        [sg.Column(mesh_text_elements), sg.Column(mesh_input_elements)],
        #[sg.Button("Generate Mesh")]
    ]

    layout_adv = [
        [sg.Column(advanced_text_elements), sg.Column(advanced_input_elements)],
    ]

    layout = [
        [sg.TabGroup([
            [sg.Tab('Aero', layout_aero)],
            [sg.Tab('Control Surface', layout_cs)],
            [sg.Tab('Mesh', layout_mesh)],
            [sg.Tab('Advanced',layout_adv)]

        ])],
        button_elements
    ]

    window_settings = sg.Window("Settings", layout)

# Run the Event Loop
    cs_number = 0
    cs_id_lst = []
    while True:
        event, values = window_settings.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break

        if event == "add_cs":
            cs_number += 1
            cs_data = {
                'Start': float(values["-cs_start-"]),
                'End': float(values["-cs_end-"]),
                'Length': float(values["-cs_length-"]),
                'Deflection': float(values["-cs_deflection-"]),
            }
            window_settings['-cs_number-'].update(cs_number)
            cs_id_lst = cs_manage.add_cs(working_dir, cs_number, cs_data, cs_id_lst)

        if event == "delete_cs":
            cs_number -= 1
            if cs_number < 0:
                cs_number = 0
            window_settings['-cs_number-'].update(cs_number)
            if cs_number != 0:
                cs_manage.delete_cs(working_dir, cs_number, cs_id_lst)

        if event == "save":
            aero_data = {
                'Alpha': [float(values["-alpha-"])],
                'Beta': [float(values["-beta-"])],
                'Mach': [float(values["-mach-"])],
            }

            mesh_data = {
                'Max_element': [float(values["-max_element-"])],
                'Min_element': [float(values["-min_element-"])],
                'Max_gap': [float(values["-max_gap-"])],
                'Growth_ratio': [float(values["-growth_ratio-"])],

            }
            advanced_data = {
                'Camber': [float(values["-Camber-"])],
                'TC': [float(values["-TC-"])],
                'Symmetry': [int(values["-Symmetry-"])],
                'Iter': [int(values["-Iter-"])],
            }
            window_settings.close()

    
    return(aero_data, mesh_data, advanced_data)
