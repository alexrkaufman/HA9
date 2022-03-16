import serial
import yaml
from pkg_resources import resource_filename
from serial.serialutil import SerialException


class HA9():
    '''
    A class that represents the HA9 programmable variable attenuator.
    '''

    def __init__(self, serial_port, baudrate=1200, timeout=0.5):
        """TODO describe function

        :param serial_port:
        :param baudrate:
        :param timeout:
        :returns:

        """
        self._port = serial_port
        self._baudrate = baudrate
        self._timeout = timeout
        self._device = None
        command_file = 'commands.yaml'

        # this function creates register functions
        def mkfn(*, command, fnname, description, **_):
            # _ here to absorb unused things. This way the yaml
            # can contain more info without causing errors here.
            def reg_fun(self, data=None):
                self.send_command(command, data)
                return self.get_response()

            reg_fun.__doc__ = description
            reg_fun.__name__ = fnname
            return reg_fun

        register_file = resource_filename('ha9', command_file)
        with open(register_file, 'r') as register_yaml:
            register_spec = yaml.safe_load(register_yaml)

            for register_name in register_spec:
                register_data = register_spec[register_name]
                setattr(HA9,
                        '_' + register_data['fnname'],
                        mkfn(command=register_name, **register_data))

    def __enter__(self):
        """TODO describe function

        :returns:

        """
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        """TODO describe function

        :param exc_type:
        :param exc_value:
        :param traceback:
        :returns:

        """
        self.disconnect()

    def __del__(self):
        """TODO describe function

        :returns:

        """
        if self._device is not None:
            self.disconnect()

    def connect(self):
        """Establishes a serial connection with the port provided

        """
        try:
            self._device = serial.Serial(self._port, self._baudrate,
                                         timeout=self._timeout)
        except SerialException:
            raise SerialException("Connection to "
                                  + self._port + " unsuccessful.")

    def disconnect(self):
        """TODO Explain what this does.

        :returns:

        """
        if not self._device.is_open:
            return

        try:
            self._device.close()
        except AttributeError:
            # When does this error occur?
            # There are a few ways disconnect can be called.
            # 1) It can be called purposefully.
            # 2) It can be called by ending a `with` (ie __exit__)
            # 3) It can be called by exiting a repl or a script ending (ie. __del__).
            pass

    def send_command(self, command, data=None):

        self._device.write(bytes(f'{command} {data}\r', 'UTF-8'))

    def get_response(self):
        response = self._device.readline()

        # change data type of response from bytestring to string
        response = response.decode()

        response = response.replace('\r', '')

        return response

    def set_block(self, is_blocked=True):

        # convert to boolean and back to int. all values > 0 accepted as true
        self._d(int(bool(is_blocked)))

    def is_blocked(self):
        response = self._d_query()

        return bool(response[0])

    def set_displaymode(self, displaymode):

        displaymodes = {'ATT': 0, 'PWR': 1}

        if type(displaymode) == int:
            setting = displaymode

        else:
            displaymode = displaymode.upper()

            if displaymode in displaymodes.keys():
                setting = displaymodes[displaymode]

            if displaymode in displaymode.values():
                setting = displaymode

        response = self._disp(f'{setting}')

    def get_wavelength(self, units='nm'):

        response = self._wvl_query()

        wavelength = float(response) * 1e9

        return wavelength

    def set_wavelength(self, wvl, units='nm'):
        '''
        Accepts the input in user chosen units. default is nm.
        Can accept upper or lowercase.
        '''
        units = units.upper()

        self._wvl(f'{wvl}{units}')

    def get_attenuation(self):

        response = self._att_query()
        return float(response)

    def set_attenuation(self, att):

        self._att(f'{att}dB')

    def reset(self):

        self._reset()

    def get_summary(self):

        response = self._lrn_query()

        return response
