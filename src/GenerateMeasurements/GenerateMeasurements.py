from BitstreamEvolutionProtocols import CircuitFactory, DataRequest, Individual, Measurement, Population

# Trivial enough that unit tests do not exist for this particular implementation
class SimpleGenerateMeasurements:
    '''
    A simple implementater of GenerateMeasurements protocol
    Stores a single FPGA and the data request that will be performed
    '''
    def __init__(self, fpga: str, data_req: DataRequest, num_samples: int):
        self.__fpga = fpga
        self.__data_req = data_req
        self.__num_samples = num_samples

    def generate(self, factory: CircuitFactory, populations: list[Population]) -> dict[Measurement, list[tuple[Population, Individual]]]:
        circuit_dict = factory(populations)
        result: dict[Measurement, list[tuple[Population, Individual]]] = {}
        for circuit in circuit_dict:
            other = circuit_dict[circuit]
            m = Measurement(self.__fpga, self.__data_req, circuit, self.__num_samples)
            result[m] = other
        return result

