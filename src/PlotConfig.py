from configparser import ConfigParser
from pathlib import Path


class PlotConfig:
    def __init__(self, filename: str):
        self.__config_parser = ConfigParser()
        self.__config_parser.read(filename)

    def get_population_size(self) -> int:
        return self.__config_parser.getint('BASE', 'population_size')
    
    def is_pulse_count(self) -> bool:
        return self.__config_parser.getboolean('BASE', 'is_pulse_count')
    
    def is_tone_discriminator(self) -> bool:
        return self.__config_parser.getboolean('BASE', 'is_tone_discriminator')

    def get_desired_frequency(self) -> int:
        return self.__config_parser.getint('BASE', 'desired_frequency')
    
    def using_transfer_interval(self) -> bool:
        return self.get_transfer_interval() > 0
    
    def get_transfer_interval(self) -> int:
        return self.__config_parser.getint('BASE', 'transfer_interval')
    
    def get_diversity_measure(self) -> str:
        return self.__config_parser.get('BASE', 'diversity_measure')
    
    def get_save_plots(self) -> bool:
        return self.__config_parser.getboolean('BASE', 'save_plots')
    
    def get_plots_directory(self) -> Path:
        return Path(self.__config_parser.get('BASE', 'plots_dir'))
    
    def uses_init_existing_population(self) -> bool:
        return self.__config_parser.getboolean('BASE', 'existing_population')
    
def save_plot_config(file_path: Path, *, pop_sz: int, is_pulse_count: bool, is_td: bool, desired_freq: int, 
                transfer_interval: int, diversity_measure: str, save_plots: bool,
                plots_dir: str, uses_init_existing_population: bool) -> None:
    with open(file_path, 'w') as f:
        f.write('[BASE]\n')
        f.write(f'population_size={pop_sz}\n')
        f.write(f'is_pulse_count={is_pulse_count}\n')
        f.write(f'is_tone_discriminator={is_td}\n')
        f.write(f'desired_frequency={desired_freq}\n')
        f.write(f'transfer_interval={transfer_interval}\n')
        f.write(f'diversity_measure={diversity_measure}\n')
        f.write(f'save_plots={save_plots}\n')
        f.write(f'plots_dir={plots_dir}\n')
        f.write(f'existing_population={uses_init_existing_population}\n')
