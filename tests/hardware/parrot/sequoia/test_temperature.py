from test_sequoia import TestSequoia


class TestOperationValues(TestSequoia):
    '''Check values for different operations.'''
    def test_temperature(self, sequoia):
        '''Verify temperature values are reasonable.'''
        with sequoia.session():
            temperatures = sequoia.get_temperature_values()
            for t in temperatures:
                print('Checking {} temperature.'.format(t))
                assert temperatures[t] <= 200000,\
                    'A temperature over 200C means something\'s gone wrong.'
