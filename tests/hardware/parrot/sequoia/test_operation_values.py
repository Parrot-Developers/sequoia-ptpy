from .test_sequoia import TestSequoia


class TestOperationValues(TestSequoia):
    '''Check values for different operations.'''
    def test_hotness(self, sequoia):
        '''Verify temperature values are reasonable.'''
        with sequoia.session():
            temperatures = sequoia.get_temperature_values()
            for t in temperatures:
                print('Checking {} temperature.'.format(t))
                assert temperatures[t] <= 200000,\
                    'A temperature over 200C means something\'s gone wrong.'

    def test_absolute_zero(self, sequoia):
        '''Verify temperature values are reasonable.'''
        with sequoia.session():
            temperatures = sequoia.get_temperature_values()
            for t in temperatures:
                print('Checking {} temperature.'.format(t))
                # -999 degrees C means invalid value.
                if temperatures[t] != -999000:
                    assert temperatures[t] > -273150,\
                        'Reported temperature is under absolute zero...'
