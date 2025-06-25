# Tool to read in a pulselivedata file and generate best/average/worst fitness lines from it
# Requires a bestlivedata file to get the diversity measurements, but otherwise generates 
# the other values in bestlivedata

TARGET_FREQ = 40000
PULSE_LIVE_DATA_PATH = './workspace/pulselivedata.log'
BEST_LIVE_DATA_PATH = './workspace/bestlivedata.log'

diversities = []
with open(BEST_LIVE_DATA_PATH, 'r') as file:
    lines = file.readlines()
    for line in lines:
        values = [v.strip() for v in line.split(',')]
        diversities.append(values[-1])


with open(BEST_LIVE_DATA_PATH, 'r+') as best_file:
    best_file.truncate(0)
    best_file.write('0, 0, 0, 0, 0, {}\n'.format(str(diversities[0])))
    with open(PULSE_LIVE_DATA_PATH, 'r') as pulse_file:
        pulse_lines = pulse_file.readlines()
        best_overall_fitness = 0
        for pulse_line in pulse_lines:
            split = pulse_line.split(':')
            generation = int(split[0])
            diversity = diversities[generation]
            pulses = [int(x) for x in split[1].split(',')]
            fits = []
            for pulse in pulses:
                if pulse == TARGET_FREQ:
                    fits.append(1)
                elif pulse == 0:
                    fits.append(0)
                else:
                    fits.append(1.0 / abs(TARGET_FREQ - pulse))
            avg = sum(fits) / len(fits)
            best = max(fits)
            worst = min(fits)
            if best > best_overall_fitness:
                best_overall_fitness = best
            best_file.write('{}, {}, {}, {}, {}, {}\n'.format(
                str(generation),
                str(best),
                str(worst),
                str(avg),
                str(best_overall_fitness),
                str(diversity)
            ))

print('Done')
