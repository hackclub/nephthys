from typing import List
from typing import Type

from nephthys.transcripts.transcript import Transcript
from nephthys.transcripts.transcripts.construct import Construct
from nephthys.transcripts.transcripts.flavortown import Flavortown
from nephthys.transcripts.transcripts.identity import Identity
from nephthys.transcripts.transcripts.midnight import Midnight
from nephthys.transcripts.transcripts.summer_of_making import SummerOfMaking
from nephthys.transcripts.transcripts.jumpstart import Jumpstart


transcripts: List[Type[Transcript]] = [
    Identity,
    SummerOfMaking,
    Flavortown,
    Midnight,
    Construct,
    Jumpstart,
]
