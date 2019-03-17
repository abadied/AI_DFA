"""
This Cython module wraps gi_learning API from c++ to python.
"""

from gi.dfa cimport *
from gi.dfa import *

cdef extern from "EDSM.hpp" namespace "gi":
    # noinspection PyPep8Naming
    cdef cppclass EDSM:
        EDSM() except +
        void add(char*, unsigned int, int, int) except +
        DFA* run() except +
        unsigned int get_alphabet_count()
        unsigned int get_positive_count()
        unsigned int get_negative_count()
        string get_alphabet()


# noinspection PyAttributeOutsideInit,PyUnresolvedReferences
cdef class EDSMSolver:
    """
    This class wraps the EDSM learn
      automata algorithm.
    """

    """
    The internal c instance.
    """
    cdef EDSM c_edsm

    """
    The c learned DFA.
    """
    cdef DFA* c_dfa

    cdef public cnp.ndarray _dfa
    cdef public dict _alphabet
    cdef public dict _reachable
    cdef public dict _state_type
    cdef public int _pos_count
    cdef public int _neg_count


    def __cinit__(self):
        """
        Initiate the EDSM Solver (c part).
        """
        self.c_edsm = EDSM()
        self._dfa = None
        self._alphabet = None
        self._reachable = None
        self._state_type = None
        self._pos_count = 0
        self._neg_count = 0


    def add_pos(self, line, weight=0):
        """
        Add positive sample.
        :param line: A string of actions depicted as characters.
        :param weight: The weight for this trace sample.
        """
        self.c_edsm.add(line.encode('UTF-8', 'strict'),
                        len(line), weight, 1)

    def add_neg(self, line, weight=0):
        """
        Add negative sample.
        :param line: A string of actions depicted as characters.
        :param weight: The weight for this trace sample.
        """
        self.c_edsm.add(line.encode('UTF-8', 'strict'),
                        len(line), weight, 0)

    def run(self):
        """
        Learn the automata.
        """
        self.c_dfa = self.c_edsm.run()

    def __dealloc__(self):
        """
        Release allocated memory.
        """
        del self.c_dfa

    def __str__(self):
        """
        String representation of the DFA.
        :return:
        """
        return self.c_dfa.dfa().decode('UTF-8')\
               if self.c_dfa != NULL else "empty"

    def dot(self):
        """
        :return: Dot format of the DFA.
        """
        if self.c_dfa != NULL:
            return Source(self.c_dfa.dot().decode('UTF-8')
                          if self.c_dfa != NULL else '')


    def alphabet_count(self):
        """
        :return: Number of actions.
        """
        if self._dfa is not None:
            return self._dfa.shape[1] - 1
        return self.c_edsm.get_alphabet_count()

    def pos_count(self):
        """
        :return: Number of positive samples to process.
        """
        if not self._pos_count:
            self._pos_count = self.c_edsm.get_positive_count()
        return self._pos_count

    def neg_count(self):
        """
        :return: Number of negative samples to process.
        """
        if not self._neg_count:
            self._neg_count = self.c_edsm.get_negative_count()
        return self._neg_count

    def state_count(self):
        """
        :return: Number of states.
        """
        if self._dfa is not None:
            return self._dfa.shape[0]
        return self.c_dfa.state_count() if self.c_dfa != NULL else 0

    def alphabet(self):
        """
        Get the alphabet mapping from char to index.
        :return:
        """
        if self._alphabet is not None:
            return self._alphabet
        self._alphabet = {}
        for c in self.c_edsm.get_alphabet().decode('UTF-8').split('|'):
            k, v = c.split(':')
            self._alphabet[k] = v
        return self._alphabet

    def state_type(self, s):
        """
        Get the state type.
        :param s: The state to check.
        :return: Accept, Reject, Normal, Unreachable.
        """
        return StateType(self._state_type[s])

    def is_accept(self, s):
        return self.state_type(s) == StateType.ACCEPT

    def is_reject(self, s):
        return self.state_type(s) == StateType.REJECT

    def is_normal(self, s):
        return self.state_type(s) == StateType.NORMAL

    def is_unreachable(self, s):
        return self.state_type(s) == StateType.UNREACHABLE

    def dfa(self):
        """
        :return: The DFA matrix.
        """
        if self._dfa is not None:
            return self._dfa
        if self.c_dfa == NULL:
            return False
        self._dfa = np.zeros((self.state_count(),
                              self.alphabet_count()),
                             dtype=int)
        self._state_type = {}
        for s in range(self._dfa.shape[0]):
            for a in range(self._dfa.shape[1]):
                self._dfa[s, a] = self.c_dfa.ttable[s][a]
            self._state_type[s] = self.c_dfa.ttable[s][self._dfa.shape[1]]
        return self._dfa

    def reachable(self):
        """
        :return: Indicator for each state whether an
                   accept state is reachable from it.
        """
        if self._reachable is not None:
            return self._reachable

        self._reachable = {}
        m, n = self._dfa.shape[0], self._dfa.shape[1]
        for s in range(m):
            if self.state_type(s) == StateType.ACCEPT:
                self._reachable[s] = True
            else:
                self._reachable[s] = False

        changed = True
        while changed:
            changed = False
            for s in range(m):
                if self._reachable[s]:
                    continue
                for a in range(n):
                    if self._reachable[self._dfa[s, a]]:
                        self._reachable[s] = True
                        changed = True
                        break

        return self._reachable

    def __getstate__(self):
        return (self._dfa, self._alphabet, self._reachable, self._state_type,
                self.c_edsm.get_positive_count(),
                self.c_edsm.get_negative_count())

    def __setstate__(self, state):
        (self._dfa, self._alphabet, self._reachable,
         self._state_type, self._pos_count, self._neg_count) = state
