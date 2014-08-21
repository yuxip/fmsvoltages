import os.path

import fms.cell

## @param north detector.SmallDetector for north
#  @param south detector.SmallDetector for south
#  @param path  Output directory for the file.
def generate(north, south, path = '.'):
    
    # We want to sort by (device, chip, channel), so loop over
    # all cells first and store
    # (device, chip, channel, address) with (address, voltage)
    
    cells = {}
    for i in north.cells + south.cells:
        cells[ (i.device, i.chip, i.chan, i.address) ] = i.voltage
    
    last = (-1, -1, -1)
    
    name = os.path.join(path, 'setVoltages.txt')
    with open(name, 'w') as file:
        for i in sorted(cells):
            j = cells[i]
            # Print change of device
            if last[0] != i[0]:
                file.write('!SETdevice ' + str(i[0]) + '\n')
            # Print change of chip and/or channel
            if last[1] != i[1] or last[2] != i[2]:
                file.write('!setctrl ' + str(i[1]) + ' ' + str(i[2]) + '\n')
                file.write('!sleep 100\n')

            # Convert address, voltage to hex strings
            address = fms.cell.Small.voltage_int_to_str(i[3])
            voltage = '0x' + fms.cell.Small.voltage_int_to_str(j)
        
            file.write('!rdac ' + address + ' ' + voltage + '\n')
            file.write('!sleep 100\n')

            last = i
            