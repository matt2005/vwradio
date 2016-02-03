from vwradio.faceplates import Enum

class OperationModes(Enum):
    UNKNOWN = 0
    SAFE_ENTRY = 10
    SAFE_LOCKED = 11
    RADIO_PLAYING = 20
    RADIO_SCANNING = 21
    CD_PLAYING = 30
    CD_CUEING = 31
    CD_NO_CD = 32
    CD_NO_DISC = 33
    CD_NO_CHANGER = 34
    CD_CHECK_MAGAZINE = 35
    TAPE_PLAYING = 40
    TAPE_FF = 41
    TAPE_REW = 42
    TAPE_MSS_FF = 43
    TAPE_MSS_REW = 44
    TAPE_NO_TAPE = 45
    TAPE_ERROR = 46

class DisplayModes(Enum):
    UNKNOWN = 0
    SHOWING_OPERATION = 10
    ADJUSTING_VOLUME = 20
    ADJUSTING_BALANCE = 21
    ADJUSTING_FADE = 22
    ADJUSTING_BASS = 23
    ADJUSTING_TREBLE = 24

class RadioBands(Enum):
    UNKNOWN = 0
    FM1 = 1
    FM2 = 2
    AM = 3

class Radio(object):
    def __init__(self):
        self.text = ' ' * 11
        self.operation_mode = OperationModes.UNKNOWN
        self.display_mode = DisplayModes.UNKNOWN
        self.safe_code = 1000
        self.safe_tries = 0
        self.sound_balance = 0 # left -9, center 0, right +9
        self.sound_fade = 0 # rear -9, center 0, front +9
        self.sound_bass = 0 # -9 to 9
        self.sound_treble = 0 # -9 to 9
        self.radio_band = RadioBands.UNKNOWN
        self.radio_freq = 0 # 883=88.3 MHz, 5400=540.0 KHz
        self.radio_preset = 0 # 0=none, am/fm1/fm2 preset 1-6
        self.cd_disc = 0 # 0=none, disc 1-6
        self.cd_track = 0 # 0=none, track 1-99
        self.cd_cue_pos = 0 # 0 or other integer as seen on lcd
        self.tape_side = 0 # 0=none, 1=side a, 2=side b

    def process(self, text):
        if text == ' ' * 11:
            pass # blank
        elif text[6:9] in ('MIN', 'MAX'):
            self._process_volume(text)
        elif str.isdigit(text[0]):
            self._process_safe(text)
        elif text[0:4] == '    ' and text[9:11] == '  ':
            self._process_safe(text)
        elif text[0:3] == 'BAS':
            self._process_bass(text)
        elif text[0:3] == 'TRE':
            self._process_treble(text)
        elif text[0:3] == 'BAL':
            self._process_balance(text)
        elif text[0:3] == 'FAD':
            self._process_fade(text)
        elif text[0:3] == 'TAP' or text == '    NO TAPE':
            self._process_tape(text)
        elif text[0:3] in ('CD ', 'CUE', 'CHK'):
            self._process_cd(text)
        elif text in ('NO  CHANGER', '    NO DISC'):
            self._process_cd(text)
        elif text[8:11] in ('MHZ', 'MHz'):
            self._process_fm(text)
        elif text[8:11] in ('KHZ', 'kHz'):
            self._process_am(text)
        else:
            self._process_unknown(text)
        self.text = text

    def _process_safe(self, text):
        self.display_mode = DisplayModes.SHOWING_OPERATION

        if str.isdigit(text[0]):
            self.safe_tries = int(text[0])
        else:
            self.safe_tries = 0

        safe_or_code = text[5:9]
        if safe_or_code == 'SAFE':
            self.operation_mode = OperationModes.SAFE_LOCKED
            self.safe_code = 1000
        elif str.isdigit(safe_or_code):
            self.operation_mode = OperationModes.SAFE_ENTRY
            self.safe_code = int(safe_or_code)
        else:
            self._process_unknown(text)

    def _process_fm(self, text):
        self.display_mode = DisplayModes.SHOWING_OPERATION

        freq = text[4:8]
        if freq[0] == ' ': # " 881"
            freq = '0' + freq[1:]
        if str.isdigit(freq):
            self.radio_freq = int(freq)

        if text[0:4] == 'SCAN':
            self.operation_mode = OperationModes.RADIO_SCANNING
            self.radio_preset = 0
            if self.radio_band not in (RadioBands.FM1, RadioBands.FM2):
                self.radio_band = RadioBands.FM1
        elif text[0:3] in ('FM1', 'FM2'):
            self.operation_mode = OperationModes.RADIO_PLAYING
            if text[2] == '1':
                self.radio_band = RadioBands.FM1
            elif text[2] == '2': # "2"
                self.radio_band = RadioBands.FM2

            if str.isdigit(text[3]):
                self.radio_preset = int(text[3])
            else: # " " no preset
                self.radio_preset = 0
        else:
            self._process_unknown(text)

    def _process_am(self, text):
        self.display_mode = DisplayModes.SHOWING_OPERATION

        freq = text[4:8]
        if freq[0] == ' ': # " 540"
            freq = '0' + freq[1:]
        if str.isdigit(freq):
            self.radio_freq = int(freq) * 10

        self.radio_band = RadioBands.AM

        if text[0:4] == 'SCAN':
            self.operation_mode = OperationModes.RADIO_SCANNING
            self.radio_preset = 0
        else:
            self.operation_mode = OperationModes.RADIO_PLAYING
            if str.isdigit(text[3]):
                self.radio_preset = int(text[3])
            else: # no preset
                self.radio_preset = 0

    def _process_cd(self, text):
        self.display_mode = DisplayModes.SHOWING_OPERATION
        if text == 'CHK MAGAZIN':
            self.operation_mode = OperationModes.CD_CHECK_MAGAZINE
            self.cd_disc = 0
            self.cd_track = 0
            self.cd_cue_pos = 0
        elif text == 'NO  CHANGER':
            self.operation_mode = OperationModes.CD_NO_CHANGER
            self.cd_disc = 0
            self.cd_track = 0
            self.cd_cue_pos = 0
        elif text == '    NO DISC':
            self.operation_mode = OperationModes.CD_NO_DISC
            self.cd_disc = 0
            self.cd_track = 0
            self.cd_cue_pos = 0
        elif text[0:3] == 'CD ':
            self.cd_disc = int(text[3])
            self.cd_cue_pos = 0
            if text[5:10] == 'NO CD':
                self.operation_mode = OperationModes.CD_NO_CD
                self.cd_track = 0
            else: # "TR 01"
                self.operation_mode = OperationModes.CD_PLAYING
                self.cd_track = int(text[8:10])
        elif text[0:3] == 'CUE':
            self.operation_mode = OperationModes.CD_CUEING
            self.cd_cue_pos = int(text[4:9].strip())
        else:
            self._process_unknown(text)

    def _process_tape(self, text):
        self.display_mode = DisplayModes.SHOWING_OPERATION
        if text in ('TAPE PLAY A', 'TAPE PLAY B'):
            self.operation_mode = OperationModes.TAPE_PLAYING
            if text[10] == 'A':
                self.tape_side = 1
            else: # "B"
                self.tape_side = 2
        elif text in ('TAPE  FF   ', 'TAPE  REW  '):
            if text[6:9] == 'REW':
                self.operation_mode = OperationModes.TAPE_REW
            else: # 'FF '
                self.operation_mode = OperationModes.TAPE_FF
        elif text in ('TAPEMSS FF ', 'TAPEMSS REW'):
            if text[8:11] == 'REW':
                self.operation_mode = OperationModes.TAPE_MSS_REW
            else: # 'FF '
                self.operation_mode = OperationModes.TAPE_MSS_FF
        elif text == '    NO TAPE':
            self.operation_mode = OperationModes.TAPE_NO_TAPE
            self.tape_side = 0
        elif text == 'TAPE ERROR ':
            self.operation_mode = OperationModes.TAPE_ERROR
            self.tape_side = 0
        else:
            self._process_unknown(text)

    def _process_volume(self, text):
        self.display_mode = DisplayModes.ADJUSTING_VOLUME

    def _process_balance(self, text):
        self.display_mode = DisplayModes.ADJUSTING_BALANCE
        if text[4] == 'C':
            self.sound_balance = 0  # Center
        elif text[4] == 'L' and str.isdigit(text[10]):
            self.sound_balance = int(text[10])  # Left
        elif text[4] == 'R' and str.isdigit(text[10]):
            self.sound_balance = -int(text[10])  # Right
        else:
            self._process_unknown(text)

    def _process_fade(self, text):
        self.display_mode = DisplayModes.ADJUSTING_FADE
        if text[4] == 'C':
            self.sound_fade = 0  # Center
        elif text[4] == 'F' and str.isdigit(text[10]):
            self.sound_fade = int(text[10])  # Front
        elif text[4] == 'R' and str.isdigit(text[10]):
            self.sound_fade = -int(text[10])  # Rear
        else:
            self._process_unknown(text)

    def _process_bass(self, text):
        self.display_mode = DisplayModes.ADJUSTING_BASS
        if str.isdigit(text[8]):
            if text[6] == '-':
                self.sound_bass = -int(text[8])
            else:
                self.sound_bass = int(text[8])
        else:
            self._process_unknown(text)

    def _process_treble(self, text):
        self.display_mode = DisplayModes.ADJUSTING_TREBLE
        if str.isdigit(text[8]):
            if text[6] == '-':
                self.sound_treble = -int(text[8])
            else:
                self.sound_treble = int(text[8])
        else:
            self._process_unknown(text)

    def _process_unknown(self, text):
        # TODO temporary
        import sys
        sys.stderr.write("Unrecognized: %r\n" % text)
        # raise ValueError("Unrecognized: %r" % text)