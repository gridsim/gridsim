"""
.. moduleauthor:: Yann Maret <yann.maret@hevs.ch>

.. codeauthor:: Yann Maret <yann.maret@hevs.ch>

"""

from enum import Enum

class ParamType(Enum):
    """
    ParamType list using in this program to identify the value
    """

    #unit 1
    un1_U1 = 0 #readable value
    un1_U2 = 1
    un1_U3 = 2
    un1_UN = 3
    un1_I1 = 4
    un1_I2 = 5
    un1_I3 = 6
    un1_IN = 7
    un1_UL12 = 8
    un1_UL23 = 9
    un1_UL31 = 10
    un1_USUM = 11
    un1_ISUM = 12
    un1_PL1 = 13
    un1_PL2 = 14
    un1_PL3 = 15
    un1_PA = 16
    un1_QL1 = 17
    un1_QL2 = 18
    un1_QL3 = 19
    un1_QA = 20
    un1_SL1 = 21
    un1_SL2 = 22
    un1_SL3 = 23
    un1_SA = 24
    un1_P = 25 #writable value
    un1_Q = 26 #

    #unit 2
    un2_U1 = 27
    un2_U2 = 28
    un2_U3 = 29
    un2_UN = 30
    un2_I1 = 31
    un2_I2 = 32
    un2_I3 = 33
    un2_IN = 34
    un2_UL12 = 35
    un2_UL23 = 36
    un2_UL31 = 37
    un2_USUM = 38
    un2_ISUM = 39
    un2_PL1 = 40
    un2_PL2 = 41
    un2_PL3 = 42
    un2_PA = 43
    un2_QL1 = 44
    un2_QL2 = 45
    un2_QL3 = 46
    un2_QA = 47
    un2_SL1 = 48
    un2_SL2 = 49
    un2_SL3 = 50
    un2_SA = 51
    un2_P = 52
    un2_Q = 53

    #unit3
    un3_U1 = 54
    un3_U2 = 55
    un3_U3 = 56
    un3_UN = 57
    un3_I1 = 58
    un3_I2 = 59
    un3_I3 = 60
    un3_IN = 61
    un3_UL12 = 62
    un3_UL23 = 63
    un3_UL31 = 64
    un3_USUM = 65
    un3_ISUM = 66
    un3_PL1 = 67
    un3_PL2 = 68
    un3_PL3 = 69
    un3_PA = 70
    un3_QL1 = 71
    un3_QL2 = 72
    un3_QL3 = 73
    un3_QA = 74
    un3_SL1 = 75
    un3_SL2 = 76
    un3_SL3 = 77
    un3_SA = 78
    un3_P = 79
    un3_Q = 80

    un4_U1 = 81
    un4_U2 = 82
    un4_U3 = 83
    un4_UN = 84
    un4_I1 = 85
    un4_I2 = 86
    un4_I3 = 87
    un4_IN = 88
    un4_UL12 = 89
    un4_UL23 = 90
    un4_UL31 = 91
    un4_USUM = 92
    un4_ISUM = 93
    un4_PL1 = 94
    un4_PL2 = 95
    un4_PL3 = 96
    un4_PA = 97
    un4_QL1 = 98
    un4_QL2 = 99
    un4_QL3 = 100
    un4_QA = 101
    un4_SL1 = 102
    un4_SL2 = 103
    un4_SL3 = 104
    un4_SA = 105
    un44_P = 106 # no writable value
    un44_Q = 107 #

    un5_U1 = 108
    un5_U2 = 109
    un5_U3 = 110
    un5_UN = 111
    un5_I1 = 112
    un5_I2 = 113
    un5_I3 = 114
    un5_IN = 115
    un5_UL12 = 116
    un5_UL23 = 117
    un5_UL31 = 118
    un5_USUM = 119
    un5_ISUM = 120
    un5_PL1 = 121
    un5_PL2 = 122
    un5_PL3 = 123
    un5_PA = 124
    un5_QL1 = 125
    un5_QL2 = 126
    un5_QL3 = 127
    un5_QA = 128
    un5_SL1 = 129
    un5_SL2 = 130
    un5_SL3 = 131
    un5_SA = 132

    @staticmethod
    def getQuantity():
        """

        getQuantity()

        return the number of ReadParam per district

        :return: number of ReadParam per district
        """
        return 25