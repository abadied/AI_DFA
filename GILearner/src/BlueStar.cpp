#include "BlueStar.hpp"

#define STAT_PROMOTION false

gi::BlueStar::BlueStar(double alpha_value, double delta_value)
    : BlueFringe()
{
    alpha = alpha_value;
    delta = delta_value;
};

//TODO: Verify that the destructor of
//        the "BlueFringe" class is invoked
gi::BlueStar::~BlueStar() = default;


double gi::BlueStar::error_rate(BlueRedDFA *dfa1,
    const vector < SymbolString > &positive,
    const vector < SymbolString > &negative,
    const vector<int> &wp, const vector<int> &wn,
    int tot_wp_w, int tot_wn_w)
{
    int wrong_recognized = 0;
    double e_rate = 0;

    // POSITIVE strings check
    for (State i = 0; i < positive.size(); ++i)
        if (!dfa1->membership_query(positive[i])) {
            wrong_recognized += wp[i];
            cerr << "ERROR: Positive string rejected" << endl;
        }

    // NEGATIVE strings check
    for (State i = 0; i < negative.size(); ++i) {
        if (dfa1->membership_query(negative[i])) {
            wrong_recognized += wn[i];
            //cout << "Negative string accepted" << endl;
        }
    }

    // Total error rate
    e_rate = (double) wrong_recognized /
        (tot_wp_w + tot_wn_w);

#ifdef DEBUG1
    cout << "string error: " << wrong_recognized << " su "<<
            static_cast<double>(tot_wp_w+tot_wn_w) << endl;
#endif
    return e_rate;
}

double
gi::BlueStar::merge_heuristic_score(
    double error_rate_before, double error_rate_after,
    int dim_strings, double alpha, int earn_states)
{
    double z_alpha;
    double T = error_rate_after - error_rate_before;
    double dev_std_h0 = DMAX;
    double ratio_error_to_n_states = 0;

    // It's "zeta_beta" because is the zeta involved to calculate beta.
    //   For our purpose is not necessary to calculate beta.
    double zeta_beta = 0;

    // Compute Z_alpha under the H0 hypothesis
    z_alpha = u2z_alpha_test(error_rate_before,
                             error_rate_after,
                             dim_strings,
                             alpha,
                             &dev_std_h0);

    // z_alpha is MINF when the error is too low for
    //   normal distribution approximation
    if (z_alpha == DMINF) {
        // +1 is for case with earn_states=0;
        //   it's needed only the relative value
        return DMINF * ((1 + earn_states) * 0.001);
    }


    // Statistic test
    if (T > z_alpha) {
#ifdef DEBUG1
        cout << "MERGE RIJECT" << endl;
#endif
        // Rejected merge
        return DMAX;
    }
    else {
        zeta_beta = z_alpha - (delta / dev_std_h0);

        if (earn_states != 0) {
            //(log10(earn_states)/log10(2000));
            ratio_error_to_n_states = (-1) * zeta_beta / earn_states;
        }
        else {
            ratio_error_to_n_states = (-1) * zeta_beta;
        }


#ifdef DEBUG1
        cout << "T: " << T << ", z_alpha: " << z_alpha <<
            ", delta: " << delta << "dev_std: " <<
            dev_std_h0 << endl
            << "zeta-beta: "<< zeta_beta << endl
            << "Stat earned: " << earn_states << endl;
#endif
        return ratio_error_to_n_states;
    }

}

gi::DFA *gi::BlueStar::run()
{
    // Samples from text file.
    // Number of positive examples.
    State dim_positive = 0;
    // Number of negative examples.
    State dim_negative = 0;
    int tot_wp_w = 0;
    int tot_wn_w = 0;
    double min_count;
    double *curr_count = nullptr;
    double *curr_zalpha = nullptr;
    State n_red = 0;
    State n_blue = 0;
    State actual_blue_state = 0;
    double error_rate_before = 0;
    // Example strings.
    bool promoted;
    bool at_least_one_promotion = false;
    BlueRedDFA *dfa1 = nullptr;
    BlueRedDFA **merged = nullptr; // DFA...
    // One dfa_best for every Blue state.
    vector<BlueRedDFA *> dfa_best;
    vector<double> dfa_score;
    // Blue states candidates to promotion
    vector<State> blue_state_index;
    vector<double> blue_promotion_score;

    // Build APTA
    dfa1 = build_apta(positive, negative);

    // Print it!
    if (dfa1->state_count() < 1000) {
        dfa1->save_dot("APTA", "./APTA.dot");
        dfa1->print_alpha_map("APTAALF", "./APTA_ALF.dot");
    }
    else {
        clog << "APTA too big! skip print" << endl;
    }

    n_blue = dfa1->blue_count();
    n_red = dfa1->red_count();
    set_fringe_size(n_red, n_blue);

    for (State i = 0; i < dim_positive; ++i) {
        tot_wp_w += wp[i];
    }
    for (State i = 0; i < dim_negative; ++i) {
        tot_wn_w += wn[i];
    }


    cout << "Total tot_wp_w: " << tot_wp_w
         << " tot_wn_w " << tot_wn_w << endl;
    cout << " START BlueStar inference process..." << endl;

    while_count = -1;
    // Blue-Star
    while (n_blue > 0) {
        ++while_count;
        promoted = false;

        // BLUE iteration
        for (State i = 0; i < n_blue &&
            (!promoted || STAT_PROMOTION); ++i) {
            /* cout << "I: "<< i << ", n_blue: "<< n_blue << endl;
            cout << "Num blue states: "
                 << dfa1->blue_count() << endl
                 << "N actual: "
                 << dfa1->get_blue()->size() << endl;
                 << "Old Actual blue state: "
                 << actual_blue_state << endl;
            */
            actual_blue_state = dfa1->get_blue().at(i);

            // Reset variable for the new run

            // Array for the heuristic values of the
            //   red group, used for select best merge.
            delete[] curr_count;
            curr_count = new double[n_red];

            // array for the z_alpha values of the red group,
            //   used for select best promotion
            if (STAT_PROMOTION) {
                delete[] curr_zalpha;
                curr_zalpha = new double[n_red];
            }

            // DFA coming from possible merges
            delete[] merged;
            merged = new BlueRedDFA *[n_red];

            // initialize values
            for (State j = 0; j < n_red; ++j) {
                curr_count[j] = DMAX;
                if (STAT_PROMOTION) {
                    curr_zalpha[j] = DMAX;
                }
                merged[j] = nullptr;
            }

            // error rate for current DFA
            error_rate_before = error_rate(
                dfa1, positive, negative,
                wp, wn, tot_wp_w, tot_wn_w);

#ifdef DEBUG1
            cout << "BLUE N:" << n_blue << endl;
                 << "Error-rate automa PRE-merging: "
                 << error_rate_before << endl;
#endif
            // Used for detection of error
            //   (OpenMP doesn't allow to handle
            //    exception inside a parallel region)
            short int error = 0;

            // RED iteration
#pragma omp parallel default(shared)
            {
#pragma omp for
                for (int j = 0; j < static_cast<int>(n_red); ++j) {
                    merged[j] = new BlueRedDFA(*dfa1);
                    merge(merged[j], dfa1->get_red().at(j),
                          actual_blue_state);

                    // TODO: This line can probably be deleted,
                    //   by doing extensive debugging.
                    merged[j]->remove_blue(actual_blue_state);

                    double error_rate_after = error_rate(
                        merged[j], positive, negative,
                        wp, wn, tot_wp_w, tot_wn_w);
                    try {
                        if (STAT_PROMOTION) {
                            curr_zalpha[j] = u2z_alpha_test(
                                error_rate_before, error_rate_after,
                                tot_wp_w + tot_wn_w, alpha);
                        }
                        curr_count[j] = merge_heuristic_score(
                            error_rate_before, error_rate_after,
                            tot_wp_w + tot_wn_w, alpha,
                            dfa1->reachables().size() -
                                merged[j]->reachables().size());
                    }
                    catch (const char *msg) {
                        cout << msg << endl;
                        ++error;
                    }

#ifdef DEBUG1
                    cout << "- Blue with red -" << endl;
                         << "Error rate after merge: " <<
                         error_rate_after <<endl;
                         << "Number of actual states before: " <<
                         dfa1->get_actual_num_states() << ", after: " <<
                         merged[j]->get_actual_num_states() << endl;
                         << "Score: " << curr_count[j] << endl;
#endif
                }
            }
            // End for RED.
            if (error != 0) {
                throw runtime_error("This inference process is stopped with no DFA");
            }

            // For Statistical purpose
            num_heuristic_merge_valued += n_red;


            // check if there some merge, else start process for promote
            promoted = true;
            min_count = DMAX;
            State j_min = ND;
            for (State j = 0; j < n_red; ++j) {
                if (curr_count[j] < min_count) {
                    min_count = curr_count[j];
                    j_min = j;
                    promoted = false;
                }
            }

            // cout << "Max_count:" << max_count << endl;


            // EXECUTE Promotion OR Merge
            if (promoted) {
                // Immediatly promotion - not adoperated in Blue*
                if (!STAT_PROMOTION) {
                    promote(dfa1, actual_blue_state);

                }
                else {
                    // Choose the minimum value among the curr_zalpha
                    //   and take it as a representative
                    //   for this promotion.
                    // When all the checks finishes, choose the major
                    //   zalpha and promote its status.
                    at_least_one_promotion = true;

                    double min_zalpha = DMAX;
                    for (State j = 0; j < n_red; ++j)
                        if (curr_zalpha[j] < min_zalpha)
                            min_zalpha = curr_zalpha[j];

                    blue_state_index.push_back(actual_blue_state);
                    blue_promotion_score.push_back(min_zalpha);

#ifdef DEBUG1
                    cout << "Potential promotion, current dimension: "
                         << blue_promotion_score.size() << endl;
                    for(Score t = 0; t < blue_promotion_score.size(); ++t) {
                        cout << "VALORE dentro: " << blue_promotion_score.at(t) << endl;
                    }
#endif
                }

                //Free memory
                typedef vector<BlueRedDFA *>::const_iterator It;
                for (It p1 = dfa_best.begin(); p1 != dfa_best.end(); ++p1) {
                    if (dfa1 == (*p1))
                        continue;
                    delete (*p1);
                }
                dfa_best.clear();
                dfa_score.clear();
            }
            else if (!at_least_one_promotion) {
                // - Merge accepted as a candidate for
                //     the final merge. and add it to
                //     the list of the best.
                dfa_best.push_back(merged[j_min]);
                dfa_score.push_back(min_count);
            }


            // Free the array with DFA merged for calculate score,
            //   leave only the DFA selected as best
            for (State j = 0; j < n_red; ++j) {
                // Leave the best. If there is at least
                //   one promotion can delete all
                if (j == j_min &&
                    (!at_least_one_promotion)) {
                    continue;
                }
                if (merged[j]) {
                    delete merged[j];
                }
            }
            delete[] merged;
            merged = nullptr;
        } // end for BLUE

        // MERGE
        // Take the best merge as next DFA, no promotion done.
        //   Select best merge between all candidates in "dfa_best"
        if (!at_least_one_promotion && !promoted) {

            // Select the best merge between all the
            //   blue states (Looking for the lower value)
            double best_score = DMAX;
            State index_best_dfa = ND;
            for (State t = 0; t < dfa_score.size(); ++t) {
                if (dfa_score.at(t) < best_score) {
                    best_score = dfa_score.at(t);
                    index_best_dfa = t;
                }
            }


            // Take the blue states before delete the old DFA
            for (State t = 0;
                 t < dfa1->blue_count(); ++t) {
                dfa_best.at(index_best_dfa)->add_blue(
                    dfa1->get_blue().at(t));
            }

            // Delete old DFA
            delete dfa1;

            // set dfa1 to the new merged DFA
            dfa1 = dfa_best.at(index_best_dfa);
            new_blue(dfa1);
            delete_states(dfa1);
            ++num_actual_merge;

            // Free memory
            for (auto &p1 : dfa_best) {
                if (dfa1 == p1) {
                    continue;
                }
                delete p1;
            }

            dfa_best.clear();
            dfa_score.clear();

            // Print information
#ifdef DEBUG1
            cout << endl << "MERGE:" << min_count << endl;
            cout << "Indice: " << index_best_dfa << endl;
#endif
            // dfa1->print("DFA");
            // cout << " ----------------------------------- "
            //      << endl;
#ifdef ALL_DFA_EDSM
            string name = "Merged" + intTostring(while_count);
            dfa1->print_dfa_dot(name, (base_path+name + ".dot").c_str());
#endif
            // Make best promotion, if Statistical
            //   Promotion is active
        }
        else if (STAT_PROMOTION) {
            at_least_one_promotion = false;
            // Select the best promotion between all the
            //   blue states (Looking for the upper value
            //   of zalpha, minimize the alpha area
            //   that is I type erro)
            double best_score = MINF;
            State index_best_blue_state = ND;
            for (State t = 0; t < blue_promotion_score.size(); ++t) {
                if (blue_promotion_score.at(t) > best_score) {
                    best_score = blue_promotion_score.at(t);
                    index_best_blue_state = blue_state_index.at(t);
                }
            }
            promote(dfa1, index_best_blue_state);

#ifdef DEBUG1
            cout << "Promote - Indice: " << index_best_blue_state
                 << ", score: " << best_score << endl;
            for(Score t=0; t<blue_promotion_score.size(); ++t) {
                cout << "VALORE: " << blue_promotion_score.at(t) << endl;
            }
#endif
            blue_promotion_score.clear();
            blue_state_index.clear();
            //Free memory
            typedef vector<BlueRedDFA *>::const_iterator It;
            for (It p1 = dfa_best.begin();
                 p1 != dfa_best.end(); ++p1) {
                if (dfa1 == (*p1)) {
                    continue;
                }
                delete (*p1);
            }
            dfa_best.clear();
            dfa_score.clear();
        }

        // update values for the DFA
        n_blue = dfa1->blue_count();
        n_red = dfa1->red_count();
        set_fringe_size(n_red, n_blue);
    }

    delete[] curr_count;

    // Sect Rejecting States.
    for (State i = 0; i < dim_negative; ++i) {
        State reject_state = dfa1->get_arrive_state(negative[i]);
        //if(reject_state != ND)
        //	dfa1->set_reject(reject_state);
    }

    // Sect Accpeting States.
    for (State i = 0; i < dim_positive; ++i) {
        State accept_state = dfa1->get_arrive_state(positive[i]);
        // if( accept_state != ND)
        // dfa1->set_accept(accept_state);
    }

    // Delete all states.
    delete_states(dfa1);
    // dfa1->print("FINAL AUTOMATA");


    ///////////////////////////////////////////////////////////////
    // Delete the unreachable states and insert, in needed, the "pos state"
    BlueRedDFA *final_dfa = dfa1->to_canonical();


    // Final error rate
    error_rate_final_dfa = error_rate(
        final_dfa, positive, negative,
        wp, wn, tot_wp_w, tot_wn_w);

    // final_dfa->print(
    // "EDSM PRE-MINIMIZATION FINAL AUTOMATA");

    //////////////////////////////////////////////////////////////
    // Return a new minimize DFA, then delete the older
    DFA *final_dfa_min = final_dfa->minimize_TF();

    delete final_dfa;
    positive.clear();
    negative.clear();
    return final_dfa_min;
}

double gi::BlueStar::get_error_rate_final_dfa()
{
    return error_rate_final_dfa;
}