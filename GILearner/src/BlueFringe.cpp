#include "BlueFringe.hpp"

using namespace std;

// TODO: change debug flag to a define.
// bool db = false; // Enable DEBUG


/**
 * Initiate blue fringe instance.
 * @param path The path to the samples.
 */
gi::BlueFringe::BlueFringe()
{
    dim_alphabet = 0;
    num_actual_merge = 0;
    num_heuristic_merge_valued = 0;
    // Size of blue fringe.
    fringe_size[0].reserve(1000);
    // Size of red fringe.
    fringe_size[1].reserve(1000);
    while_count = -1;
    debug = false;
    verbose = false;
    dim_alphabet = 0;
}

/**
 * Release resources.
 */
gi::BlueFringe::~BlueFringe()
{
    inverse_mapped_alphabet.clear();
    mapped_alphabet.clear();
}

void gi::BlueFringe::set_debug(bool val) { debug = val; }
void gi::BlueFringe::set_verbose(bool val) { verbose = val; }

/**
 * Read samples from file.
 * @param positive The result positive vector.
 * @param dim_positive The dimension of the positive vector.
 * @param negative The result negative vector.
 * @param dim_negative The dimension of the negative vector.
 * @param wp The weights for the positive vector values.
 * @param wn The weights for the negative vector values.
 */
void gi::BlueFringe::read_samples(const string &path_samples)
{
    // Open the sample file.
    ifstream infile(path_samples);
    if (!infile) {
        cerr << "An error occurred in opening file"
             << endl;
        exit(EXIT_FAILURE);
    }

    // Number of positive language strings.
    unsigned int cp = 0;
    // Number of negative language strings.
    unsigned int cn = 0;
    char ch;
    // Count before the number of positive and negative
    //   strings in the input file.
    while (infile >> noskipws >> ch) {
        switch (ch) {
            case '\n':
                continue;
            case '+':
                ++cp;
                break;
            case '-':
                ++cn;
                break;
            default:
                break;
        }
    }

    positive.clear();
    negative.clear();
    wp.clear();
    wn.clear();
    positive.resize(cp);
    negative.resize(cn);
    wp.resize(cp);
    wn.resize(cn);
    for (unsigned int i = 0; i < cp; ++i) {
        wp[i] = 0;
    }
    for (unsigned int i = 0; i < cn; ++i) {
        wn[i] = 0;
    }
    cout << cp << " positive" << endl;
    cout << cn << " negative" << endl;
    unsigned int flag_cp = 0;
    unsigned int flag_cn = 0;
    bool is_positive = false;
    bool is_negative = false;
    bool pre_pos = true;
    bool pre_neg = true;
    bool first = true;
    bool second = false;
    SymbolType null_symbol = 0;
    string line;
    // Rewind the file to the beginning.
    infile.clear();
    infile.seekg(0);
    while (getline(infile, line)) {
        istringstream iss(line);
        Symbol a;
        string n;
        // Read first line for dim alphabet.
        if (first) {
            if (!(iss >> a)) {
                break;
            } // error
            dim_alphabet = a;
            //cout << "alphabet dimention: "
            //     << a << endl;
            second = true;
            first = false;
            continue;
        }

        // Read second line for alphabet symbol
        if (second) {
            int counter = -1;
            while (iss >> n) {
                if (counter == -1) {
                    null_symbol = static_cast<SymbolType>(n[0]);
                    ++counter;
                    continue;
                }
                auto s = static_cast<Symbol>(counter);
                if (s >= dim_alphabet) {
                    break;
                }
                mapped_alphabet[n[0]] = s;
                inverse_mapped_alphabet[s] = n[0];
                ++counter;
            }

            // Alphabet
            if (static_cast<Symbol>(counter) != dim_alphabet) {
                cerr << "Error in reading example: "
                    "number of red alphabet"
                     << " symbols mismatches with "
                         "the declared one!"
                     << endl;
                cerr << "Expected symbols: "
                     << dim_alphabet << endl;
                cerr << "Red symbols: "
                     << counter << endl;
                exit(EXIT_FAILURE);
            }
            // alphabet ok ;)
            second = false;
        }
        bool weight = true;

        // Read remaining lines
        while (iss >> n) {
            if (n == "+") {
                weight = true;
                is_positive = true;
                is_negative = false;
                // avoid the increase for the first case.
                if (pre_pos) {
                    pre_pos = false;
                    continue;
                }
                ++flag_cp;
                continue;

            }
            else if (n == "-") {
                weight = true;
                is_negative = true;
                is_positive = false;
                // avoid the increase for the first case.
                if (pre_neg) {
                    pre_neg = false;
                    continue;
                }
                ++flag_cn;
                continue;
            }

            // If the string is empty, there is
            //   no need to add anything.
            if (n[0] == null_symbol) {
                continue;
            }

            if (weight) {
                weight = false;
                if (is_positive) {
                    wp[flag_cp] = str_to_int(n);
                }
                else if (is_negative) {
                    wn[flag_cn] = str_to_int(n);
                }
            }
            else {
                Symbol tmp = mapped_alphabet[n[0]];
                if (is_positive) {
                    positive[flag_cp].push_back(tmp);
                }
                else if (is_negative) {
                    negative[flag_cn].push_back(tmp);
                }
            }
        }
    }
}

void gi::BlueFringe::add(const char* line, unsigned int len,
                         int weight, int sign)
{
    SymbolString line_vec;
    for (unsigned int i = 0; i < len; ++i) {
        if (line[i] == 10) {
            continue;
        }
        auto find_it = mapped_alphabet.find(line[i]);
        Symbol s;
        if (find_it != mapped_alphabet.end()) {
            s = find_it->second;
        } else {
            s = static_cast<Symbol>(dim_alphabet++);
            mapped_alphabet.emplace(line[i], s);
            inverse_mapped_alphabet.emplace(s, line[i]);
        }
        line_vec.push_back(s);
    }
    if (sign == 1) {
        positive.push_back(line_vec);
        wp.push_back(weight);
    } else {
        negative.push_back(line_vec);
        wn.push_back(weight);
    }
}

/**
 * build apta from sample set
 * @param positive Positive samples.
 * @param negative Negative samples.
 * @return The created automata.
 */
gi::BlueRedDFA *gi::BlueFringe::build_apta(
    const vector < SymbolString > &positive,
    const vector < SymbolString > &negative)
{
    // Preparations:
    // Calculate the prefixes and save them
    //   together with an indicator of the state.
    map<SymbolString, State, vector_int_size_less> prefixes;
    // Add empty string.
    SymbolString empty_vec;
    prefixes[empty_vec] = 0;

    for (const auto &i : positive) {
        auto w = i.begin();
        for (auto j = i.begin(); j != i.end(); ++j) {
            // A sub-vector of positive
            //   from i to j + 1.
            SymbolString sub(w, j + 1);
            if (prefixes[sub] == 0) {
                // after 0 no possible separation.
                prefixes[sub] = ND;
            }
        }
    }

    for (const auto &i : negative) {
        auto w = i.begin();
        for (auto j = i.begin(); j != i.end(); ++j) {
            SymbolString sub(w, j + 1);
            if (prefixes[sub] == 0) {
                prefixes[sub] = 0;
            }
        }
    }

    // Assign the correct status indexes
    //   for the related prefixes.
    State state_index = 0;
    for (auto p1 : prefixes) {
        prefixes[p1.first] = state_index;
        ++state_index;
    }

    // *** PTA ***
    auto apta_dfa = new BlueRedDFA(
        prefixes.size(), inverse_mapped_alphabet, 0);
    Matrix &pta = apta_dfa->get_ttable();

    bool init_state = true;
    for (auto p : prefixes) {
        SymbolString state = p.first;
        // cout << "Considered States:"<< state << endl;
        // Only for the First State - manage apart from being
        //   red and in the meantime not accepting -
        // Verify each element of the alphabet, where a
        //   transition from the initial state is defined.
        if (init_state) {
            // Set the value of Transitions
            for (Symbol i = 0;
                 i < dim_alphabet; ++i) {
                SymbolString symbol;
                symbol.push_back(i);
                // Verify a state is defined
                //   when an element of
                //   the alphabet arrives
                //   after lambda.
                if (prefixes.find(symbol) != prefixes.end()) {
                    pta[p.second][i] = prefixes[symbol];
                }
            }

            // Init state: non accept.
            pta[p.second][dim_alphabet] = 0;
            // Add the red state also to the
            //   management through VECTOR.
            apta_dfa->add_red(p.second);
            init_state = false;
            continue;
        }


        // Accept states
        // Put the appropriate states to acceptors:
        //   those whose string is also among the positive strings.
        for (State i = 0; i < mapped_alphabet.size(); ++i) {
            if (state == positive[i]) {
                // With dim_alfabat arrival to the first
                //   column over the letters of the alphabet.
                pta[p.second][dim_alphabet] = 1;
                break;
            }
            else {
                pta[p.second][dim_alphabet] = 0;
            }
        }

        // Transitions
        // Verify for each letter of the alphabet that the
        //   transition exists; if there is a memorization.
        for (Symbol i = 0; i < dim_alphabet; ++i) {
            SymbolString temp_vect(state);
            temp_vect.push_back(i);
            // In the row of the considered state ((* p) .second)
            //   the relative transition.
            if (prefixes.find(temp_vect) != prefixes.end()) {
                pta[p.second][i] = prefixes[temp_vect];
            }
        }
    }
    // Those blue states (the first level
    //   after lambda in ESDM):
    for (Symbol i = 0; i < dim_alphabet; ++i) {
        State state_blue = pta[0][i];
        // Also add it to the Vector of Blue States.
        if (pta[0][i] != ND) {
            apta_dfa->add_blue(state_blue);
        }
    }

    // Print APTA
    /*
    apta_dfa->print("*** APTA DENTRO ***");
    apta_dfa->save_dot("apta",PATH_DOT_APTA);
    */
    // cout << "PTA constructed" << endl;
    return apta_dfa;
}

void gi::BlueFringe::merge(BlueRedDFA *cur_dfa,
                           State red_state,
                           State blue_state)
{
    State predecessor = 0;
    Symbol letter_count = 0;
    State predecessor_num = 0;
    // Look for the predecessor of the state blue.
    for (State i = 0; i < cur_dfa->state_count(); ++i) {
        for (Symbol j = 0; j < cur_dfa->alphabet_count(); ++j) {
            if (cur_dfa->get_ttable()[i][j] == blue_state) {
                predecessor = i;
                letter_count = j;
                ++predecessor_num;
            }
        }
    }

    if (predecessor_num != 1) {
        cerr << "Num predec:" << predecessor_num
             << " PROBLEM: " << predecessor_num
             << "for the state " << blue_state
             << ", check algorithm!" << endl;
    }
    // The transition of the precedent
    //   (of bluestate) to red_state,
    // now q2 is IRREPTABLE in the original tree.
    cur_dfa->get_ttable()[predecessor][letter_count] = red_state;
    fold(cur_dfa, red_state, blue_state);
}

void gi::BlueFringe::fold(
    BlueRedDFA *original,
    State red_state,
    State blue_state)
{
    int column_type = original->alphabet_count();
    Matrix &current_ttable = original->get_ttable();

    // If q2 accepts, sept at the same q1.
    if (current_ttable[blue_state][column_type] ==
        DFA_STATE_ACCEPT)
        current_ttable[red_state][column_type] =
            DFA_STATE_ACCEPT;
    // For each letter, I check if the original tree is defined
    // a transition also present in the subtree:
    // If present step to the successive states,
    //   otherwise carry out the merge
    //   inserting the transition.
    for (Symbol i = 0; i < original->alphabet_count(); ++i) {
        State from_blue = current_ttable[blue_state][i];
        State from_red = current_ttable[red_state][i];

        // Now the blue state can be deleted, by
        //   setting its transition to ND for the current letter
        current_ttable[blue_state][i] = ND;

        // TODO: Could the state here already be deleted from the blue?
        //   Probably, but debug before activating this code
        //current_ttable[blue_state][column_type+1] = DFA_STATE_WHITE;
        //original->remove_blue(blue_state);

        if (from_blue != ND) {
            if (from_red != ND) {
                fold(original, from_red, from_blue);
            }
            else {
                // Add the existing transition in the subtree
                //   but not in the state in which was merge
                current_ttable[red_state][i] = from_blue;
                //current_ttable[blue_state][i] = ND;
            }
        }
    }
    // There is no need to eliminate the status line,
    //   it will be unattainable by everyone,
    //   you can take it into account at the end.
}

void gi::BlueFringe::promote(BlueRedDFA *cur_dfa, State q)
{
    if (!cur_dfa->in_blue(q)) {
        cerr << "WARNING! You are not BLUE!" << endl;
    }

    // Promote state q to RED.
    cur_dfa->add_red(q);
    cur_dfa->remove_blue(q);

    // Promote to blue all the states
    //   that can be reached directly from q.
    for (Symbol i = 0; i < cur_dfa->alphabet_count(); ++i) {
        State transition = cur_dfa->get_ttable()[q][i];
        if (transition != ND) {
            cur_dfa->add_blue(transition);
        }
    }
}

// Promote to BLUE all the states reachable
//   in a direct way by a RED.
void gi::BlueFringe::new_blue(BlueRedDFA *cur_dfa)
{
    State numred = cur_dfa->red_count();
    // Promote to BLUE all the states
    //   reachable by a RED in a direct way
    for (Symbol i = 0; i < cur_dfa->alphabet_count(); ++i) {
        for (State j = 0; j < numred; ++j) {
            State red = cur_dfa->get_red()[j];
            State transition = cur_dfa->get_ttable()[red][i];
            if (transition != ND) {
                // It's blue as long as it's not red
                if (!cur_dfa->in_red(transition)) {
                    cur_dfa->add_blue(transition);
                }
            }
        }
    }
}

void gi::BlueFringe::delete_states(BlueRedDFA *cur_dfa)
{
    Symbol column_type = cur_dfa->alphabet_count();

    // Delete all states.
    // Check if the status K is visited by someone.
    for (State k = 1; k < cur_dfa->state_count(); ++k) {
        bool is_visit = false;
        for (State i = 0; i < cur_dfa->state_count(); ++i) {
            for (Symbol j = 0; j < cur_dfa->alphabet_count(); ++j)
                if (cur_dfa->get_ttable()[i][j] == k &&
                    !cur_dfa->is_unreachable(i))
                    is_visit = true;
        }

        if (!is_visit) {
            // If the state of the state is
            //   not_visit from any other state
            cur_dfa->set_unreachable(k);
            // Delete them from the Vector of
            //   Red or Blue, if any.
            cur_dfa->remove_red(k);
            cur_dfa->remove_blue(k);
        }
    }
}

int gi::BlueFringe::get_actual_merge()
{
    return num_actual_merge;
}

int gi::BlueFringe::get_heuristic_merge()
{
    return num_heuristic_merge_valued;
}

void gi::BlueFringe::set_fringe_size(State r, State b)
{
    // 0 for Blue, 1 for Red
    fringe_size[0].push_back(b);
    fringe_size[1].push_back(r);

}

void gi::BlueFringe::print_fringe_size()
{
    // 0 for Blue, 1 for Red
    for (auto i = fringe_size[1].begin(),
              l = fringe_size[0].begin();
         i != fringe_size[1].end() &&
         l != fringe_size[0].end();
         ++i, ++l) {
        cout << "R:" << (*i) << ",";
        cout << "B:" << (*l) << endl;
    }
}

int gi::BlueFringe::get_while_count()
{
    return while_count;
}

unsigned int gi::BlueFringe::get_alphabet_count()
{
    return dim_alphabet;
}

unsigned int gi::BlueFringe::get_positive_count()
{
    return positive.size();
}

unsigned int gi::BlueFringe::get_negative_count()
{
    return negative.size();
}

string gi::BlueFringe::get_alphabet()
{
    ostringstream os;
    bool first = true;
    for (auto& it : mapped_alphabet) {
        if (!first) {
            os << "|";
        }
        first = false;
        os << it.first << ":" << it.second;
    }
    return os.str();
}