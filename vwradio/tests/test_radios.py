import sys
import unittest
from vwradio.radios import Radio, OperationModes, DisplayModes, RadioBands

class TestRadio(unittest.TestCase):
    def test_safe_mode(self):
        values = (
            ('     0000  ',    0, 0, OperationModes.SAFE_ENTRY),
            ('1    1234  ', 1234, 1, OperationModes.SAFE_ENTRY),
            ('2    5678  ', 5678, 2, OperationModes.SAFE_ENTRY),
            ('9    9999  ', 9999, 9, OperationModes.SAFE_ENTRY),
            ('     SAFE  ', 1000, 0, OperationModes.SAFE_LOCKED),
            ('1    SAFE  ', 1000, 1, OperationModes.SAFE_LOCKED),
            ('2    SAFE  ', 1000, 2, OperationModes.SAFE_LOCKED),
            ('9    SAFE  ', 1000, 9, OperationModes.SAFE_LOCKED),
        )
        for text, safe_code, safe_tries, mode in values:
            radio = Radio()
            radio.process(text)
            self.assertEqual(radio.safe_code, safe_code)
            self.assertEqual(radio.safe_tries, safe_tries)
            self.assertEqual(radio.operation_mode, mode)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_volume(self):
        texts = (
            'AM    MIN  ',
            'AM    MAX  ',
            'FM1   MIN  ',
            'FM1   MAX  ',
            'FM2   MIN  ',
            'FM2   MAX  ',
            'CD    MIN  ',
            'CD    MAX  ',
            'TAP   MIN  ',
            'TAP   MAX  ',
        )
        for text in texts:
            radio = Radio()
            radio.operation_mode = OperationModes.SAFE_LOCKED
            radio.process(text)
            self.assertEqual(radio.operation_mode,
                OperationModes.SAFE_LOCKED)
            self.assertEqual(radio.display_mode,
                DisplayModes.ADJUSTING_VOLUME)

    def test_balance(self):
        values = (
            ('BAL RIGHT 9', -9),
            ('BAL RIGHT 1', -1),
            ('BAL CENTER ', 0),
            ('BAL LEFT  1', 1),
            ('BAL LEFT  9', 9),
        )
        for text, balance in values:
            radio = Radio()
            original_operation_mode = radio.operation_mode
            radio.sound_balance = 99
            radio.process(text)
            self.assertEqual(radio.sound_balance, balance)
            self.assertEqual(radio.operation_mode,
                original_operation_mode)
            self.assertEqual(radio.display_mode,
                DisplayModes.ADJUSTING_BALANCE)

    def test_fade(self):
        values = (
            ('FADEREAR  9', -9),
            ('FADEREAR  1', -1),
            ('FADECENTER ', 0),
            ('FADEFRONT 1', 1),
            ('FADEFRONT 9', 9),
        )
        for text, fade in values:
            radio = Radio()
            original_operation_mode = radio.operation_mode
            radio.sound_fade = 99
            radio.process(text)
            self.assertEqual(radio.sound_fade, fade)
            self.assertEqual(radio.operation_mode,
                original_operation_mode)
            self.assertEqual(radio.display_mode,
                DisplayModes.ADJUSTING_FADE)

    def test_bass(self):
        values = (
            ('BASS  - 9  ', -9),
            ('BASS  - 1  ', -1),
            ('BASS    0  ', 0),
            ('BASS  + 1  ', 1),
            ('BASS  + 9  ', 9),
        )
        for text, bass in values:
            radio = Radio()
            original_operation_mode = radio.operation_mode
            radio.sound_bass = 99
            radio.process(text)
            self.assertEqual(radio.sound_bass, bass)
            self.assertEqual(radio.operation_mode,
                original_operation_mode)
            self.assertEqual(radio.display_mode,
                DisplayModes.ADJUSTING_BASS)

    def test_treble(self):
        values = (
            ('TREB  - 9  ', -9),
            ('TREB  - 1  ', -1),
            ('TREB    0  ', 0),
            ('TREB  + 1  ', 1),
            ('TREB  + 9  ', 9),
        )
        for text, treble in values:
            radio = Radio()
            original_operation_mode = radio.operation_mode
            radio.sound_treble = 99
            radio.process(text)
            self.assertEqual(radio.sound_treble, treble)
            self.assertEqual(radio.operation_mode,
                original_operation_mode)
            self.assertEqual(radio.display_mode,
                DisplayModes.ADJUSTING_TREBLE)

    def test_fm_scan_off(self):
        values = (
            ('FM1  887MHz',  887, RadioBands.FM1, 0),
            ('FM1  887MHZ',  887, RadioBands.FM1, 0),
            ('FM1 1023MHZ', 1023, RadioBands.FM1, 0),
            ('FM11 915MHZ',  915, RadioBands.FM1, 1),
            ('FM161079MHZ', 1079, RadioBands.FM1, 6),
            ('FM2  887MHZ',  887, RadioBands.FM2, 0),
            ('FM2 1023MHZ', 1023, RadioBands.FM2, 0),
            ('FM21 915MHZ',  915, RadioBands.FM2, 1),
            ('FM261079MHZ', 1079, RadioBands.FM2, 6),
            )
        for text, freq, band, preset in values:
            radio = Radio()
            radio.process(text)
            self.assertEqual(radio.radio_band, band)
            self.assertEqual(radio.radio_freq, freq)
            self.assertEqual(radio.radio_preset, preset)
            self.assertEqual(radio.operation_mode,
                OperationModes.RADIO_PLAYING)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_fm_scan_on(self):
        values = (
            ('SCAN 879MHz',  879, RadioBands.FM1, RadioBands.FM1),
            ('SCAN 879MHZ',  879, RadioBands.FM1, RadioBands.FM1),
            ('SCAN 879MHZ',  879, RadioBands.UNKNOWN, RadioBands.FM1),
            ('SCAN1035MHZ', 1035, RadioBands.FM2, RadioBands.FM2),
        )
        for text, freq, initial_band, expected_band in values:
            radio = Radio()
            radio.radio_band = initial_band
            radio.process(text)
            self.assertEqual(radio.radio_freq, freq)
            self.assertEqual(radio.radio_preset, 0)
            self.assertEqual(radio.radio_band, expected_band)
            self.assertEqual(radio.operation_mode,
                OperationModes.RADIO_SCANNING)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_am_scan_off(self):
        values = (
            ('AM   670kHz',  6700, 0),
            ('AM   670KHZ',  6700, 0),
            ('AM  1540KHZ', 15400, 0),
            ('AM 1 670KHZ',  6700, 1),
            ('AM 61540KHZ', 15400, 6),
            )
        for text, freq, preset in values:
            radio = Radio()
            radio.operation_mode = OperationModes.UNKNOWN
            radio.process(text)
            self.assertEqual(radio.radio_freq, freq)
            self.assertEqual(radio.radio_band, RadioBands.AM)
            self.assertEqual(radio.operation_mode, OperationModes.RADIO_PLAYING)
            self.assertEqual(radio.radio_preset, preset)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_am_scan_on(self):
        values = (
            ('SCAN 530kHz',  5300),
            ('SCAN 530KHZ',  5300),
            ('SCAN1710KHZ', 17100),
        )
        for text, freq in values:
            radio = Radio()
            radio.radio_band = RadioBands.AM
            radio.process(text)
            self.assertEqual(radio.radio_freq, freq)
            self.assertEqual(radio.radio_band, RadioBands.AM)
            self.assertEqual(radio.radio_preset, 0)
            self.assertEqual(radio.operation_mode,
                OperationModes.RADIO_SCANNING)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_cd_playing(self):
        values = (
            ('CD 1 TR 01 ', 1, 1),
            ('CD 6 TR 99 ', 6, 99),
        )
        for text, disc, track in values:
            radio = Radio()
            radio.operation_mode = OperationModes.UNKNOWN
            radio.process(text)
            self.assertEqual(radio.cd_disc, disc)
            self.assertEqual(radio.cd_track, track)
            self.assertEqual(radio.operation_mode,
                OperationModes.CD_PLAYING)
            self.assertEqual(radio.display_mode,
                DisplayModes.SHOWING_OPERATION)

    def test_cd_cueing(self):
        radio = Radio()
        radio.operation_mode = OperationModes.CD_PLAYING
        radio.cd_disc = 5
        radio.cd_track = 12
        radio.process('CUE   122  ')
        self.assertEqual(radio.cd_disc, 5)
        self.assertEqual(radio.cd_track, 12)
        self.assertEqual(radio.cd_cue_pos, 122)
        self.assertEqual(radio.operation_mode,
            OperationModes.CD_CUEING)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_cd_check_magazine(self):
        radio = Radio()
        radio.operation_mode = OperationModes.CD_PLAYING
        radio.cd_disc = 1
        radio.cd_track = 3
        radio.cd_cue_pos = 99
        radio.process('CHK MAGAZIN')
        self.assertEqual(radio.cd_disc, 0)
        self.assertEqual(radio.cd_track, 0)
        self.assertEqual(radio.cd_cue_pos, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.CD_CHECK_MAGAZINE)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_cd_no_cd(self):
        radio = Radio()
        radio.operation_mode = OperationModes.CD_PLAYING
        radio.cd_disc = 1
        radio.cd_track = 3
        radio.cd_cue_pos = 99
        radio.process('CD 2 NO CD ')
        self.assertEqual(radio.cd_disc, 2)
        self.assertEqual(radio.cd_track, 0)
        self.assertEqual(radio.cd_cue_pos, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.CD_NO_CD)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_cd_no_disc(self):
        radio = Radio()
        radio.operation_mode = OperationModes.CD_PLAYING
        radio.cd_disc = 7
        radio.cd_track = 9
        radio.cd_cue_pos = 99
        radio.process('    NO DISC')
        self.assertEqual(radio.cd_disc, 0)
        self.assertEqual(radio.cd_track, 0)
        self.assertEqual(radio.cd_cue_pos, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.CD_NO_DISC)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_cd_no_changer(self):
        radio = Radio()
        radio.operation_mode = OperationModes.CD_PLAYING
        radio.cd_disc = 7
        radio.cd_track = 9
        radio.cd_cue_pos = 99
        radio.process('NO  CHANGER')
        self.assertEqual(radio.cd_disc, 0)
        self.assertEqual(radio.cd_track, 0)
        self.assertEqual(radio.cd_cue_pos, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.CD_NO_CHANGER)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_play_a(self):
        radio = Radio()
        radio.process('TAPE PLAY A')
        self.assertEqual(radio.tape_side, 1)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_PLAYING)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_play_b(self):
        radio = Radio()
        radio.process('TAPE PLAY B')
        self.assertEqual(radio.tape_side, 2)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_PLAYING)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_ff(self):
        radio = Radio()
        radio.process('TAPE  FF   ')
        radio.tape_side = 1
        self.assertEqual(radio.tape_side, 1)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_FF)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_mss_ff(self):
        radio = Radio()
        radio.process('TAPEMSS FF ')
        radio.tape_side = 1
        self.assertEqual(radio.tape_side, 1)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_MSS_FF)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_rew(self):
        radio = Radio()
        radio.tape_side = 2
        radio.process('TAPE  REW  ')
        self.assertEqual(radio.tape_side, 2)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_REW)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_mss_rew(self):
        radio = Radio()
        radio.tape_side = 2
        radio.process('TAPEMSS REW')
        self.assertEqual(radio.tape_side, 2)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_MSS_REW)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_error(self):
        radio = Radio()
        radio.tape_side = 1
        radio.process('TAPE ERROR ')
        self.assertEqual(radio.tape_side, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_ERROR)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_tape_no_tape(self):
        radio = Radio()
        radio.tape_side = 0
        radio.process('    NO TAPE')
        self.assertEqual(radio.tape_side, 0)
        self.assertEqual(radio.operation_mode,
            OperationModes.TAPE_NO_TAPE)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

    def test_ignores_blank(self):
        radio = Radio()
        radio.operation_mode = OperationModes.RADIO_PLAYING
        radio.display_mode = DisplayModes.SHOWING_OPERATION
        radio.process(' ' * 11)
        self.assertEqual(radio.operation_mode,
            OperationModes.RADIO_PLAYING)
        self.assertEqual(radio.display_mode,
            DisplayModes.SHOWING_OPERATION)

def test_suite():
    return unittest.findTestCases(sys.modules[__name__])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')