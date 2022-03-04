import serial
import yaml
from pkg_resources import resource_filename
from serial.serialutil import SerialException


class HA9():
    '''
    A class that represents the HA9 programmable variable attenuator.
    '''

    def __init__(self, serial_port, baudrate, timeout=0.5):
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
        command_file = 'commands.yml'

        # this function creates register functions
        def mkfn(*, fnname, description, **_):
            # _ here to absorb unused things. This way the yaml
            # can contain more info without causing errors here.
            def reg_fun(self):
                self.send_command()
                return self.get_response()

            reg_fun.__doc__ = description
            reg_fun.__name__ = fnname
            return reg_fun

        register_file = resource_filename('ha9', command_file)
        with open(register_file, 'r') as register_yaml:
            register_spec = yaml.safe_load(register_yaml)

            for register_name in register_spec:
                print(register_name)
                register_data = register_spec[register_name]
                setattr(HA9,
                        '_' + register_data['fnname'],
                        mkfn(**register_data))

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

        **For some reason on Linux opening the serial port causes some
        power output from the laser before it has been activated. This behavior
        does not occur on Windows.**

        """
        try:
            self._device = serial.Serial(self._port, self._baudrate,
                                         timeout=self._timeout)
        except SerialException:
            raise SerialException("Connection to "
                                  + self._port + " unsuccessful.")

    def disconnect(self, leave_on=False):
        """Ends the serial connection to the laser

        :param leave_on:
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

    def send_command(self, register, data=None, signed=False):
        pass

    def get_response(self, register):
        pass
