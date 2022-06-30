r"""The CrowdStrike Developer ToolKit for FalconPy.

Welcome to the

    ______                         __ _______ __         __ __
   |      |.----.-----.--.--.--.--|  |     __|  |_.----.|__|  |--.-----.
   |   ---||   _|  _  |  |  |  |  _  |__     |   _|   _||  |    <|  -__|
   |______||__| |_____|________|_____|_______|____|__|  |__|__|__|_____|


  .,-:::::   :::.    :::::::..    :::.       .,-:::::   :::.    :::::::..    :::.
,;;;'````'   ;;`;;   ;;;;``;;;;   ;;`;;    ,;;;'````'   ;;`;;   ;;;;``;;;;   ;;`;;
[[[         ,[[ '[[,  [[[,/[[['  ,[[ '[[,  [[[         ,[[ '[[,  [[[,/[[['  ,[[ '[[,
$$$        c$$$cc$$$c $$$$$$c   c$$$cc$$$c $$$        c$$$cc$$$c $$$$$$c   c$$$cc$$$c
`88bo,__,o, 888   888,888b "88bo,888   888,`88bo,__,o, 888   888,888b "88bo,888   888,
  "YUMMMMMP"YMM   ""` MMMM   "W" YMM   ""`   "YUMMMMMP"YMM   ""` MMMM   "W" YMM   ""`

                                                    Developer Toolkit for FalconPy
"""
__all__ = ["Client", "Policy"]

from caracara.client import Client
from caracara.common import Policy
from caracara.common.meta import _pkg_version

# According to PEP 8, dunders should be before imports; however,
# this import is needed for the dunder to function
__version__ = _pkg_version

"""
MIT License

Copyright (c) CrowdStrike

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
