import os

def generate_verilog(file, inputs, outputs):
    module = "module template ("
    for pin in inputs:
        module += "input p" + str(pin) + ", "
    for pin in outputs:
        module += "output p" + str(pin) + ", "
    module = module[0:len(module)-2]
    module += ");\n"

    for pin in outputs:
        module += "\t assign p" + str(pin) + " = "
        for p in inputs:
            module += "p" + str(p) + " | "
        module = module[0:len(module)-3]
        module += ";\n"
    
    module += "endmodule"
    f = open(file, "w")
    f.write(module)
    f.close()

def generate_pcf(file, inputs, outputs):
    # set_io --warn-no-port <wire_name> <physical pin name>
    pcf = ""
    for pin in inputs:
        pcf += "set_io --warn-no-port p" + str(pin) + " " + str(pin) + "\n"
    for pin in outputs:
        pcf += "set_io --warn-no-port p" + str(pin) + " " + str(pin) + "\n"
    f = open(file, "w")
    f.write(pcf)
    f.close()


def overwritewrite_io(src, dest):
    pass

verilog_file = "workspace/template/template.v"
pcf_file = "workspace/template/template.pcf"
inputs = [112, 113, 114]
outputs = [119]
generate_verilog(verilog_file, inputs, outputs)
generate_pcf(pcf_file, inputs, outputs)

blif_file = "workspace/template/template.blif"
asc_file = "workspace/template/template.asc"
os.system("yosys -p 'synth_ice40 -top template -blif " + blif_file +"' "+  verilog_file)
os.system("arachne-pnr -d 1k -o " + asc_file + " -p " + pcf_file + " " + blif_file)
