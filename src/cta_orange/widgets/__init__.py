import sysconfig

# Category metadata.

# Category icon show in the menu
ICON = "icons/cta.png"

# Background color for category background in menu
# and widget icon background in workflow.
BACKGROUND = "#CE93D8"

DESCRIPTION = """Add-on for researchers in text analysis for Orange3"""

LONG_DESCRIPTION = """
WORK IN PROGRESS
"""
from .extract_string import ExtractStringsCTA
from .load import LoadTSVFile

#from .load import LoadTSVFile
#from .load import LoadTSVFile
#from .load import LoadTSVFile
#from .load import LoadTSVFile
#from .load import LoadTSVFile
#from .load import LoadTSVFile

# Orange utilise __all__ pour découvrir les widgets
__all__ = [
    "CTAProportion",
    "CTASegmentation",
    "CTAStringsFeatures",
    "EvidenceBrowserCTA",
    "ExtractStringsCTA",
    "LoadTSVFile",
    "OrangeCTAClaim",
    "StringsFilter"
]
