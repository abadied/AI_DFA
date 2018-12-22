#include "EDSM.hpp"

using namespace std;

/* Convensions:
 *	 column[dim_alphabet]   -> type;
 *	 type:   0-> neutral, 1-> accept, 2-> reject, 3-> removed
 */

gi::EDSM::EDSM(): BlueFringe() {};


//TODO: Verify that the destructor of
//        the "BlueFringe" class is invoked.
gi::EDSM::~EDSM() = default;

int
gi::EDSM::merge_heuristic_score(
    BlueRedDFA *cur_dfa,
    const vector < vector <Symbol> > &positive,
    const vector < vector <Symbol> > &negative,
    const vector<int> *wp,
    const vector<int> *wn)
{
    State *tp, *tn = nullptr;
    // Initialize a counter for each state
    tp = new State[cur_dfa->state_count()];
    tn = new State[cur_dfa->state_count()];

    for (State i = 0; i < cur_dfa->state_count(); ++i) {
        tp[i] = 0;
        tn[i] = 0;
    }

    // TODO implement COUNTER with OpenMP
    // Check how many POSITIVE strings are recognized
    for (State i = 0; i < positive.size(); ++i) {
        State final_state = cur_dfa->get_arrive_state(positive[i]);
        if (final_state != ND) {
            if (wp == nullptr) {
                ++tp[final_state];
            } else {
                tp[final_state] += (*wp)[i];
            }
        }
    }

    // cout << endl;
    if (debug) {
        for (State i = 0; i < cur_dfa->state_count(); ++i) {
            cout << "tp[" << i << "]: " << tp[i] << " ";
        }
    }

    // TODO Implement COUNTER with OpenMP
    // Check how many NEGATIVE strings are recognized
    for (State i = 0; i < negative.size(); ++i) {
        State final_state = cur_dfa->get_arrive_state(negative[i]);
        if (final_state != ND) {
            if (wn == nullptr) {
                ++tn[final_state];
            }
            else {
                tn[final_state] += (*wn)[i];
            }
        }
    }

    // cout << endl;
    if (debug) {
        for (State i = 0; i < cur_dfa->state_count(); ++i) {
            cout << "tn[" << i << "]: " << tn[i] << " ";
        }
    }

    // Calculate the SCORE
    int sc = 0;
    for (State i = 0; i < cur_dfa->state_count(); ++i) {
        if (sc != MINF) {
            if (tn[i] > 0) {
                if (tp[i] > 0) {
                    if (debug) {
                        cout << endl
                             << "State that accepts Positive & Negative:"
                             << i << endl;
                    }
                    sc = MINF;
                    // It is useless to continue
                    //   iterating if I put sc = ND
                    break;
                }
                else {
                    // In the pseudo De La Higuera puts -1
                    //   (in complex situations leads to
                    //   different end automata)
                    sc += tn[i] - 1;
                }
            }
            else {
                if (tp[i] > 0) {
                    sc += tp[i] - 1;
                }
            }
        }
    }

    delete[] tp;
    delete[] tn;
    return sc;
}

gi::DFA *gi::EDSM::run()
{
    int max_count;
    int *curr_count = nullptr;
    State n_red = 0;
    State n_blue = 0;
    State actual_blue_state = 0;

    // example strings
    char *symbols = nullptr;
    bool promoted;

    BlueRedDFA *cur_dfa = nullptr;
    BlueRedDFA **merged = nullptr;

    // One dfa_best_vec for every Blue state
    vector<BlueRedDFA *> dfa_best_vec;
    vector<int> dfa_score;

    // Create PTA
    // BlueRedDFA* cur_dfa = build_pta(positive, dim_positive);

    // Build APTA
    cur_dfa = build_apta(positive, negative);

    // Print the initial DFA if not too big.
    if (verbose) {
        if (cur_dfa->state_count() < 1000) {
            cur_dfa->save_dot("APTA", "./APTA.dot");
            cur_dfa->print_alpha_map("APTAALF", "./APTA_ALF.dot");
        }
        else {
            clog << "Skip print of too big initial DFA" << endl;
        }
    }

    n_blue = cur_dfa->blue_count();
    n_red = cur_dfa->red_count();
    set_fringe_size(n_red, n_blue);
    if (verbose) {
        cout << " START Edsm inference process:" << endl;
    }

    while_count = -1;
    // ESDM
    while (n_blue > 0) {
        ++while_count;
        promoted = false;

        // BLUE iteration
        for (State i = 0; i < n_blue && (!promoted); ++i) {
            actual_blue_state = cur_dfa->get_blue()[i];
            // Reset variable for the new run
            // array for the heuristic values of the red group
            delete[] curr_count;
            curr_count = new int[n_red];

            // DFA coming from possible merges
            delete[] merged;
            merged = new BlueRedDFA *[n_red];

            // initialize values
            for (State j = 0; j < n_red; ++j) {
                curr_count[j] = ND;
                merged[j] = nullptr;
            }


            // RED iteration
#pragma omp parallel default(shared)
            {
#pragma omp for
                for (int j = 0; j < static_cast<int>(n_red); ++j) {
                    merged[j] = new BlueRedDFA(*cur_dfa);
                    merge(merged[j],
                          cur_dfa->get_red()[(State)j],
                          actual_blue_state);

                    // TODO: This line can probably be deleted,
                    //         by doing extensive debugging
                    merged[j]->remove_blue(actual_blue_state);

                    curr_count[j] =
                        merge_heuristic_score(
                            merged[j],
                            positive,
                            negative,
                            nullptr,
                            nullptr);
                }
            }
            // end for RED

            // For Statistical purpose
            num_heuristic_merge_valued += n_red;

            // check if there some merge, else
            //   start process for promote
            promoted = true;
            max_count = MINF;
            State j_max = ND;
            for (State j = 0; j < n_red; ++j) {
                if (curr_count[j] > max_count) {
                    max_count = curr_count[j];
                    j_max = j;
                    promoted = false;
                }
            }

            //cout << "Max_count:" << max_count << endl;


            // PROMOTION
            if (promoted) {
                promote(cur_dfa, actual_blue_state);
                // cout << "Promoted" << endl;

#ifdef ALL_DFA_EDSM
                ostringstream os_dfa;
                os_dfa << "P" << while_count << blue[i];
                cur_dfa->print_dfa_dot(os_dfa.str(),
                  ("./" + os_dfa.str() + ".dot").c_str());
#endif

                // Free memory
                for (BlueRedDFA *p1 : dfa_best_vec) {
                    if (cur_dfa == p1) {
                        continue;
                    }
                    delete p1;
                }
                dfa_best_vec.clear();
                dfa_score.clear();
            }
            else {
                // - Merge accepted as a candidate for
                //     the final merge. add it to the list of the best.
                // merged[j_max]->remove_blue(actual_blue_state);

                dfa_best_vec.push_back(merged[j_max]);
                dfa_score.push_back(max_count);
            }

            // Free the array with DFA merged for calculate score,
            //   leave only the DFA selected as best
            for (State j = 0; j < n_red; ++j) {
                // Leave the best.
                if (j == j_max && (!promoted)) {
                    continue;
                }
                delete merged[j];
            }
            delete[] merged;
            merged = nullptr;
        } // end for BLUE


        // MERGE
        // Do definitive merge, no promotion done.
        //   Select best merge between all candidates in "dfa_best_vec"
        if (!promoted) {
            // Select the best merge between all the blue states
            int best_score = -1;
            unsigned int index_best_dfa = 0;
            for (unsigned int t = 0; t < dfa_score.size(); ++t) {
                if (dfa_score[t] > best_score) {
                    best_score = dfa_score[t];
                    index_best_dfa = t;
                }
            }

            // Take the blue states before delete the old DFA
            // int column_type = cur_dfa->alphabet_count();
            BlueRedDFA *dfa_best = dfa_best_vec[index_best_dfa];
            for (auto b : cur_dfa->get_blue()){
                dfa_best->add_blue(b);
            }
            // Delete old DFA.
            delete cur_dfa;

            // set cur_dfa to the new merged DFA
            cur_dfa = dfa_best;
            new_blue(cur_dfa);
            delete_states(cur_dfa);

            // Print information
            //cout << "MERGE:"<<max_count<<endl;
            //cout <<" ----------------------------------- "<<endl;
#ifdef ALL_DFA_EDSM
            string name = "M" + DFA::intTostring(while_count);
            cur_dfa->print_dfa_dot(name, ("./" + name + ".dot").c_str());
#endif
            ++num_actual_merge;
            // Free memory
            for (auto &p1 : dfa_best_vec) {
                if (cur_dfa == p1) {
                    continue;
                }
                delete p1;
            }
            dfa_best_vec.clear();
            dfa_score.clear();
        }

        // update values for the DFA
        n_blue = cur_dfa->blue_count();
        n_red = cur_dfa->red_count();
        set_fringe_size(n_red, n_blue);
    }
    delete[] curr_count;

    // Sept. Accepting States.
//    for (State i = 0; i < dim_positive; ++i) {
//        State accept_state =
//            cur_dfa->get_arrive_state(positive[i]);
//			if(accept_state != ND)
//				cur_dfa->get_ttable()[accept_state][column_type] =
//                DFA_STATE_ACCEPT;
//    }

    // Sept. Rejecting States.
    for (const auto &i : negative) {
        State reject_state = cur_dfa->get_arrive_state(i);
        if (reject_state != ND) {
            // cout << "State of arrival: " << reject_state << endl;
            cur_dfa->set_reject(reject_state);
        }
    }

    // Delete all states.
    delete_states(cur_dfa);
    // cur_dfa->print("FINAL AUTOMATA");

    // Delete the unreachable states and insert,
    //   if needed, the sink state
    BlueRedDFA *final_dfa = cur_dfa->to_canonical();
    // Minimize returns a new DFA, then delete the older
    DFA *final_min_dfa = final_dfa->minimize_TF();
    delete final_dfa;
    positive.clear();
    negative.clear();
    delete[] symbols;
    return final_min_dfa;

}
