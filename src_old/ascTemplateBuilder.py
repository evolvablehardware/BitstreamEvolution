import os
from mmap import mmap
from shutil import copyfile

class ascTemplateBuilder:
    def __init__(self, config, logger):
        self.__config = config
        self.__logger = logger

    def configure_seed_io(self, seed_hardware, dest):
        self.__log_event(2, "Configuring the io tiles of the seed circuit")
        verilog_file = "workspace/template/template.v"
        pcf_file = "workspace/template/template.pcf"
        inputs = self.__config.get_input_pins()
        outputs = self.__config.get_output_pins()
        self.generate_verilog(verilog_file, inputs, outputs)
        self.generate_pcf(pcf_file, inputs, outputs)

        blif_file = "workspace/template/template.blif"
        asc_file = "workspace/template/template.asc"
        self.__log_event(4, "Generating blif file for configurable io")
        os.system("yosys -p 'synth_ice40 -top template -blif " + blif_file +"' "+  verilog_file)
        self.__log_event(4, "Generated blif file for configurable io")
        self.__log_event(4, "Generating asc file for configurable io")
        os.system("arachne-pnr -d 1k -o " + asc_file + " -p " + pcf_file + " " + blif_file)
        self.__log_event(4, "Generated asc file for configurable io")

        self.overwritewrite_io(asc_file, seed_hardware, dest)
        self.__log_event(2, "Finished configuring the io tiles of the seed circuit")

    def generate_verilog(self, file, inputs, outputs):
        '''
        Generates the verilog file used to gnerate the asc file for configurable io
        '''
        # write module header
        module = "module template ("
        for pin in inputs:
            module += "input p" + str(pin) + ", "
        for pin in outputs:
            module += "output p" + str(pin) + ", "
        module = module[0:len(module)-2]
        module += ");\n"

        # wire together inputs and outputs
        # not sure if this is necessary
        # if(len(inputs) > 0):
        #     for pin in outputs:
        #         module += "\t assign p" + str(pin) + " = "
        #         for p in inputs:
        #             module += "p" + str(p) + " | "
        #         module = module[0:len(module)-3]
        #         module += ";\n"
        
        # end module
        module += "endmodule"
        f = open(file, "w")
        f.write(module)
        f.close()
        self.__log_event(4, "Generated verilog file for configurable io")

    def generate_pcf(self, file, inputs, outputs):
        '''
        Generates the pcf (pin constraints file) for configurable io
        '''
        # pcf format:
        # set_io --warn-no-port <wire_name> <physical pin name>
        pcf = ""
        for pin in inputs:
            pcf += "set_io --warn-no-port p" + str(pin) + " " + str(pin) + "\n"
        for pin in outputs:
            pcf += "set_io --warn-no-port p" + str(pin) + " " + str(pin) + "\n"
        f = open(file, "w")
        f.write(pcf)
        f.close()
        self.__log_event(4, "Generated pcf file for configurable io")


    def overwritewrite_io(self, io_src, logic_src, dest):
        '''
        Overwrite the io tiles of the destination file with the io tiles of the source files
        '''
        # use mmaps to improve perfomance
        io_src = open(io_src, "r+")
        io_src_file = mmap(io_src.fileno(), 0)
        io_src.close()

        copyfile(logic_src, dest)
        dest = open(dest, "r+")
        dest_file = mmap(dest.fileno(),0)
        dest.close()
        
        #find first io tile
        src_tile = io_src_file.find(b".io_tile")
        dest_tile = dest_file.find(b".io_tile")
        while src_tile > 0:
            src_pos = src_tile + len(".io_tile")
            dest_pos = dest_tile + len(".io_tile")

            # calculate size until the next tile
            tile_start = io_src_file.find(b"\n", src_tile) + 1
            tile_end = io_src_file.find(b".", tile_start + 1)
            tile_size = tile_end - tile_start + 1

            # overwrite the existing io tile
            data = io_src_file[src_pos:src_pos + tile_size]
            dest_file[dest_pos:dest_pos + tile_size] = data

            # find next io tile (will be -1 when we're out of tiles)
            src_tile = io_src_file.find(b".io_tile", src_tile + 1)
            dest_tile = dest_file.find(b".io_tile", dest_tile + 1)

    def __log_event(self, level, *event):
        """
		Emit an event-level log. This function is fulfilled through
		the logger.
		"""
        self.__logger.log_event(level, *event)
