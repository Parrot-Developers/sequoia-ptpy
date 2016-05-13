from test_sequoia import TestSequoia


class TestOperations(TestSequoia):
    def test_temperature(self, sequoia):
        '''Verify temperature values are reasonable.'''
        with sequoia.session():
            temperatures = sequoia.get_temperature_values()
            for t in temperatures:
                assert temperatures[t] <= 200000,\
                    'A temperature over 200C means something\'s gone wrong.'
