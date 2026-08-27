# Category metadata.

# Category icon show in the menu
ICON = "icons/cta.png"

# Background color for category background in menu
# and widget icon background in workflow.
BACKGROUND = "#CE93D8"

DESCRIPTION = """Add-on for researchers in text analysis for Orange3"""

LONG_DESCRIPTION = """
CTA Orange is an add-on for Orange Canvas created for Computational Text Analysis and based on CTA Kernel. \
It adds 8 new widgets meant to propose an interface based edit of a CTA Kernel's workflow. At last, it is \
designed to make scientific claims about text analysis in a more practicable way.
"""
from .extract_string import ExtractStringsCTA
from .load import LoadTSVFile

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
