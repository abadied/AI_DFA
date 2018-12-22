#include "LSTAR.hpp"

gi::LSTAR::LSTAR(const DFA &target_dfa)
{
    target = new DFA(target_dfa);

    // Initialize
    SymbolString empty_prefix;
    // Initialize the lambda state to RED.
    pref[empty_prefix] = OBTState::OBT_STATE_RED;

    // Set alphabet size.
    dim_alphabet = target->alphabet_count();

    // Allocate vector from the alphabet.
    alphabet = new SymbolString[dim_alphabet];

    // Initialize each member of the alphabet to BLUE.
    for (Symbol i = 0; i < dim_alphabet; ++i) {
        alphabet[i].push_back(i);
        pref[alphabet[i]] = OBTState::OBT_STATE_BLUE;
    }

    // Initialize to "lambda" exp
    experiments.push_back(empty_prefix);
    mq[empty_prefix] = target->membership_query(empty_prefix);
    for (Symbol i = 0; i < target->alphabet_count(); ++i) {
        mq[alphabet[i]] = target->membership_query(alphabet[i]);
    }
}

gi::LSTAR::~LSTAR()
{
    delete[] alphabet;
    delete target;
}

// bool obt::closed()
bool gi::LSTAR::close_obt()
{
    // If the table is not closed, it is closed
    // If the table is not changed (it was closed),
    //   it returns false, otherwise true

    // *** CLOSING ***
    // For each BLUE there must be an
    //   equal row between REDs
#ifdef DEBUG_2
    cout << "--------------------------" << endl;
    cout << "     Check the CLOSURE    " << endl;
    cout << "--------------------------" << endl;
#endif

    // The table is closed if the line relative to
    // each BLUE prefix is identical to at least
    // one line of a RED prefix.

    // Iterate only on BLUEs
    for (auto &p1 : pref) {
        if (p1.second == OBTState::OBT_STATE_BLUE) {
            bool redFound = false;
            vector<OBTState> rowB = get_row(p1.first);
#ifdef DEBUG_3
            cout << "Verify Blue: " << prefB << endl;
#endif

            // Iterate over accepting states.
            for (auto &p2 : pref) {
                if (p2.second == OBTState::OBT_STATE_RED) {
                    vector<OBTState> rowR = get_row(p2.first);
                    if (rowB == rowR) {
                        redFound = true;
                        break;
                    }
                }
            }

            // For the blue state I did not
            //   find any corresponding
            //   red state.
            if (!redFound) {
#ifdef DEBUG_2
                cout << "Table NOT closed" << endl;
                cout << "Promote RED "<< p1->first << endl;
#endif

                SymbolString prefB = p1.first;

                // Promote the BLUE in question RED.
                pref[prefB] = OBTState::OBT_STATE_RED;

                // Add to the BLUE the new RED
                //   concatenated to each symbol of
                // the alphabet.
                for (Symbol i = 0; i < dim_alphabet; ++i) {
                    SymbolString tmpB = append_vectors(&prefB, alphabet + i);

                    // tmpB.insert(tmpB.end(), alphabet[i].begin(),
                    //   alphabet[i].end());

                    // Create a new prefix.
                    pref[tmpB] = OBTState::OBT_STATE_BLUE;

                    // Fill the line of the obt for the new prefix.
                    for (auto &experiment : experiments) {
                        SymbolString tmpB_row =
                            append_vectors(&tmpB, &experiment);
                        mq[tmpB_row] = target->membership_query(tmpB_row);
                    }
                }

                // The function adds a single experiment and then exits,
                //   indicating that the table has been modified.
                // N.B .: the table is NOT necessarily closed,
                //   it has only one less problem
                return true;
            }
        }
    }

#ifdef DEBUG_2
    cout << "--------------------------" << endl;
    cout << "      End CLOSING         " << endl;
    cout << "--------------------------" << endl;
#endif

    return false;
}

bool gi::LSTAR::make_obt_consistent()
{
    // *** CONSISTENCY ***
    // 2 equal states with the same input must reach the same status.

#ifdef DEBUG_2
    cout << "--------------------------" << endl;
    cout << "  Check the CONSISTENCY   " << endl;
    cout << "--------------------------" << endl;
#endif

    for (auto &p1 : pref) {
        // RED cycle: s1
        if (p1.second == OBTState::OBT_STATE_RED) {
            SymbolString prefR1 = p1.first;
            vector<OBTState> rowR1 = get_row(p1.first);
            // RED cycle: s2
            for (auto &p2 : pref) {
                if (p2.second == OBTState::OBT_STATE_RED) {

                    // Try to work with 2 distinct reds
                    //   (NB: "compare" here returns T if they are different)
                    if (p1.first == p2.first) {
                        continue;
                    }

                    SymbolString prefR2 = p2.first;
                    vector<OBTState> rowR2 = get_row(p2.first);

                    // If they are the same row, I verify that
                    //   there are no inconsistencies.
                    if (rowR1 == rowR2) {
                        //V cout << "They have equal lines, therefore potential"
                        //          " generators of inconsistency" << endl;
                        for (Symbol i = 0; i < dim_alphabet; ++i) {
                            SymbolString prefR1A = append_vectors(&prefR1, alphabet + i);
                            SymbolString prefR2A = append_vectors(&prefR2, alphabet + i);

                            // If it is NOT consistent, update the
                            //   EXP and the table accordingly
                            vector<OBTState> prefR1A_row = get_row(prefR1A);
                            vector<OBTState> prefR2A_row = get_row(prefR2A);
                            if (prefR1A_row != prefR2A_row) {
                                unsigned int q = 0;
                                // Determine the suffix for which the two lines differ.
                                for (auto w = experiments.begin();
                                     w != experiments.end(); ++w, ++q)
                                    if (prefR1A_row.at(q) != prefR2A_row.at(q)) {
                                        SymbolString expc = append_vectors(alphabet + i, &(*w));
                                        // Add the new suffix (experiment).
                                        experiments.push_back(expc);
                                        // Fill the column of the obt for the new suffix
                                        for (auto &p3 : pref) {
                                            SymbolString tmpP = p3.first;
                                            tmpP = append_vectors(&tmpP, &expc);
                                            mq[tmpP] = target->membership_query(tmpP);
                                        }
#ifdef DEBUG_2
                                        cout << "--------------------------" << endl;
                                        cout << "          Consistent      " << endl;
                                        cout << "--------------------------" << endl;
#endif

                                        // The function adds a single suffix and then exits,
                                        //   indicating that the table has been modified.
                                        // N.B.: The table is not necessarily consistent,
                                        //         it only has one less problem
                                        return true;
                                    }
                            }
                        }
                    }
                }
            }
        }
    }

#ifdef DEBUG_2
    cout << "--------------------------" << endl;
    cout << "     End of CONSISTENCY   " << endl;
    cout << "--------------------------" << endl;
#endif

    return false;
}

gi::DFA *gi::LSTAR::obt_to_dfa()
{
    // OBSERVATION TABLE -> DFA

    // Create a list of the final automaton
    //   states with the "states" map
    // LIST OF STATES: State Label and 2 integers:
    // The first by numerical index of the state,
    //   according to acceptor or not
    map<SymbolString, State[2], vector_int_size_less> states;
    unsigned int count_state = 0;

    // Here I check the transitions looking
    //   at the rows of the oss table.
    // RED cycle: s1
    unsigned int w = 0;
    for (auto &i : pref) {
        cout << "Pref " << (w++) << ": " << i.first << endl;
    }

    for (auto p1 = pref.begin(); p1 != pref.end(); ++p1) {
        bool final_states_inDFA = true;

        if (p1->second == OBTState::OBT_STATE_RED) {
            // string prefR1 = p1->first;

            // Assume it is a state to be added (status_inDFAfinal = T).
            // Cycling internally "equal" must always
            //   become F at the end, if T remains
            // there is an already analyzed state equal to that
            //   taken into consideration therefore
            // must not belong and status_inDFAfinal = F
            // bool states_inDFAfinale=true;
            // RED cycle: s2
            for (auto p2 = pref.begin(); p2 != p1; ++p2) {
                if (p2->second == OBTState::OBT_STATE_RED &&
                    get_row(p1->first) == get_row(p2->first)) {
                    final_states_inDFA = false;
                    break;
                }
            }

            if (final_states_inDFA) {
                // State index in the TRANSITION table and
                //   type of status (accentuating or not)
                states[p1->first][0] = count_state;
                states[p1->first][1] = mq[p1->first] ?
                                       DFA_STATE_ACCEPT :
                                       DFA_STATE_REJECT;
                ++count_state;
            }
        }
    }

    auto dfaOBT = new DFA(count_state, target->alphabet, 0);
    Matrix &dfaOBTtable = dfaOBT->get_ttable();

    // Print red states list.
#ifdef DEBUG_2
    cout << "--------------------------------------" << endl;
    cout << "LIST OF RED STATES (final automaton): " << endl;
    cout << "--------------------------------------" << endl;
    // Iterate over the final automata states.
    for(auto p1=states.begin(); p1!=states.end(); ++p1) {
        cout << p1->first <<";" << endl;
    }
    cout << "END" << endl;
#endif

    // Calculating the transitions matrix.
    // Iterate on the states of the final automaton.
    for (auto p1 = states.begin(); p1 != states.end(); ++p1) {
        // Starting label string.
        SymbolString departure_state = p1->first;
        State departure_state_idx = states[departure_state][0];
        for (Symbol i = 0; i < dim_alphabet; ++i) {
            // Arrival label string.
            SymbolString arrive_state = append_vectors(
                &departure_state, alphabet + i);

            // As the arrival state could be a row () among the blue,
            // must look for the corresponding state among the reds;
            // then set the "arrival status" label, and find the label
            // among reds that has the same row, and use
            //   it to extract the corresponding index
            //   in the final DFA matrix.
            State arrive_state_idx = 0;
            // Find the line of the arrival state and look
            //   for the first among the RED's which
            //   has the same line.
            auto p2 = states.begin();
            for (; p2 != states.end(); ++p2) {

                SymbolString p2_pref = p2->first;
                if (get_row(arrive_state) == get_row(p2_pref)) {
                    arrive_state_idx = states[p2_pref][0];
                    break;
                }
            }

            // before change assertion.
            // TO CHANGE
            if (p2 == states.end()) {
                cerr << "Error, stop the world: " <<
                    "index_state _ arrival not assigned!" << endl;
                return nullptr;
            }

            dfaOBTtable[departure_state_idx][i] =
                arrive_state_idx;
        }
        // Set the type of status: accepting or not.
        dfaOBTtable[departure_state_idx][dim_alphabet] =
            states[departure_state][1];
    }

    return dfaOBT;
}

void gi::LSTAR::update_from_counterexample(
    const SymbolString& witness)
{
    // *** add the Counter example to
    //   the observation table ***
#ifdef DEBUG_2
    cout << "Update the observation table " <<
            "through the counterexample" << endl;
#endif

    for (auto i = witness.begin() + 1; i != witness.end(); ++i) {
        SymbolString pref_witness = prefix_vector(witness, i);

        // Add all the prefixes of the contr.ex. like RED.
        pref[pref_witness] = OBTState::OBT_STATE_RED;

        // Close the holes with MQ.
        for (auto &experiment : experiments) {
            if (mq.count(pref_witness) == 0) {
                mq[pref_witness] = target->membership_query(
                    append_vectors(&pref_witness, &experiment));
            }
        }

        for (Symbol j = 0; j < dim_alphabet; ++j) {
            SymbolString pref_witness_alpha =
                append_vectors(&pref_witness, alphabet + j);

            // If prefix + alpha_letter is not present,
            //   I'll put it among the blue ones.
            if (pref.count(pref_witness_alpha) == 0) {
                // Close in prefixes / suffixes (with
                //   each letter of the alphabet).
                pref[pref_witness_alpha] = OBTState::OBT_STATE_BLUE;
                // Fill the holes with MQ.
                for (auto &experiment : experiments) {
                    SymbolString pref_witness_alpha_exp =
                        append_vectors(&pref_witness_alpha, &experiment);
                    if (mq.count(pref_witness_alpha_exp) == 0)
                        mq[pref_witness_alpha_exp] =
                            target->membership_query(pref_witness_alpha_exp);
                }
            }
        }
    }
}

void gi::LSTAR::print_obt()
{
    cout << "---------------------------------------------" << endl
         << "   OBSERVATION TABLE - List of total lines   " << endl
         << "---------------------------------------------" << endl;

    cout << "Exp: ";
    for (auto &experiment : experiments)
        cout << experiment << ", ";
    cout << endl;
    // Iterate on the states of the final automaton.
    for (auto &p1 : pref) {
        if ((int) p1.second == 1) {
            cout << "R ";
            SymbolString tmpVect = p1.first;
            cout << tmpVect << " | ";
            for (auto &experiment : experiments) {
                cout << mq[append_vectors(&tmpVect, &experiment)]
                     << " ";
            }
            cout << endl;
        }
    }
    cout << endl;

    // Iterate on the states of the final automaton.
    for (auto &p1 : pref) {
        if ((int) p1.second == 0) {
            cout << "B ";
            SymbolString tmpVect = p1.first;
            cout << tmpVect << " | ";
            for (auto &experiment : experiments) {
                cout << mq[append_vectors(
                    &tmpVect, &experiment)] << " ";
            }
            cout << endl;
        }
    }
    cout << endl << "---------------------------------------------" << endl;
}

vector<OBTState> gi::LSTAR::get_row(const SymbolString& prefix)
{
    vector<OBTState> row;

    // vector<SymbolString>::const_iterator last_index;
    for (auto &experiment : experiments) {
        SymbolString tmpVect = prefix;
        tmpVect.insert(tmpVect.end(),
                       experiment.begin(),
                       experiment.end());
        row.push_back((mq[tmpVect]) ?
                      OBTState::OBT_STATE_RED :
                      OBTState::OBT_STATE_BLUE);
    }

    return row;
}

gi::DFA *gi::LSTAR::run(bool approximate,
                        const string *samples_test_path)
{
    DFA *dfahp = nullptr;
    int count_generation = 0;

    // Minimize tgdfa
    DFA *t1 = target->minimize_TF();

    delete target;

    target = t1;

    // Observation table
    auto obtable = new LSTAR(*target);

    DFA *dfatmp = nullptr;

    while (true) {
#ifdef DEBUG_1
        cout << endl << endl
             << "********************************" << endl
             << count_generation << " GENERATION "  << endl
             << "********************************" << endl;
#endif

        // Long version of the code of the next lines:
        // For the first time check that
        //   the table is closed and consistent;
        // All the other times I render the table closed
        //   and consist only if it has been previously
        // changed from the obtable-> close_obt ()
        //   and obtable-> make_obt_consistent () functions.

        // cycle until the table is closed and consistent
        //while( obtable->close_obt() || obtable->make_obt_consistent());
        bool modified, modified2 = true, firstTime = true;

        while (modified2) {
            // make the table closed and memorize
            //   if I changed it at least once
            modified = false;
            while (obtable->close_obt()) {
                modified = true;
            }

            // I render the consensus table and memorize
            //   if I have changed it at least once
            // I do it only if the table has changed since
            //   the last cycle, or if it has been closed,
            //   or if it is the first cycle
            modified2 = false;
            while ((modified || firstTime) &&
                obtable->make_obt_consistent()) {
                modified2 = true;
            }

            firstTime = false;
        }
        // Print transition table
#ifdef DEBUG_2
        obtable->print_obt();
#endif

        // DFA from transition table
        delete dfatmp;

        dfatmp = obtable->obt_to_dfa();

#ifdef DEBUG_2
        dfatmp->print_dfa_ttable("DFA_HP from the OBSERVATION TABLE");
#endif
        ++count_generation;
        // Generate witness if necessary
        SymbolString witness;
        // if(!approximate)
        witness = target->equivalence_query(dfatmp);
        // else
        //	witness = target->equivalence_query_approximate(dfatmp, samples_test_path);

        // Find automaton when witness is 'e',
        //   else update the obb. table
        //TODO: problem with "and": how do you replace it?
        // In practice, as I understand in the examples
        //   there will never be empty strings, so the problem
        //   of the approximation does not arise.
        // It does not seem correct to me, however,
        //   that we can not have null strings as
        //   positive samples
        /*if(witness.compare("e")){
            obtable->update_from_counterexample(witness);
        }*/
        if (!witness.empty()) {
            obtable->update_from_counterexample(witness);
        } else {
            cout << "LSTAR: Automa Constructed." << endl;
            dfahp = dfatmp->minimize_TF();
            break;
        }
    }

    delete dfatmp;
    // dfahp->set_n_memb_query(tgdfaL->get_n_memb_query());
    delete obtable;
    // delete tgdfaL;
    // DFA dfahp2(*dfahp);
    return dfahp;
}

std::ostream &operator<<(std::ostream &os, OBTState s)
{
    return os << static_cast<char>(s) + '0';
}
