class PdfType:
    is_scanned = True
    column = 1
    linspace = 0
    noise = 0
    tilt = 0
    table = 0

    def __init__(self):
        self.is_scanned = True
        self.column = 1
        self.linspace = 0
        self.noise = 0
        self.tilt = 0
        self.table = 0

    def __init__(
        self,
        scan: bool,
        column: int,
        linspace: int,
        noise: int,
        tilt: bool,
        table: bool,
    ):

        self.is_scanned = scan
        self.column = column
        self.linspace = linspace
        self.noise = noise
        self.tilt = tilt
        self.table = table
