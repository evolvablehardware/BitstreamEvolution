from BitstreamEvolutionProtocols import Circuit, DataRequest, FPGA_Compilation_Data, Individual, Population
from GenerateMeasurements.GenerateMeasurements import SimpleGenerateMeasurements
from result import Result, Ok # type: ignore

class MockIndividual:
    def __init__(self, id: int):
        self.id = id

class MockCircuit:
    def __init__(self, id: int):
        self.id = id

    def compile(self, fpga: FPGA_Compilation_Data) -> Result[None,Exception]:
        Ok(None)

class MockCircuitFactory:
    def generate(self, populations: list[Population]) -> dict[Circuit,list[tuple[Population,Individual]]]:
        result = {}
        for pop in populations:
            for (ind, _) in pop:
                ckt = MockCircuit(ind.id) # type: ignore
                result[ckt] = [(pop, ind)]
        return result

def test_simple_generate_measurements():
    gen_meas = SimpleGenerateMeasurements('fake-fpga', DataRequest.WAVEFORM, 0)
    factory = MockCircuitFactory()
    pop = Population([MockIndividual(1)], None)
    measurements = gen_meas.generate(factory.generate, [pop])
    values = list(measurements.items())

    assert len(values) == 1
    m = values[0]

    measurement = m[0]
    assert measurement.data_request == DataRequest.WAVEFORM
    assert measurement.FPGA_request == 'fake-fpga'

    pairing = m[1]
    assert len(pairing) == 1
    assert pairing[0][0] == pop
    assert pairing[0][1].id == 1 # type: ignore

