import java.util.Iterator;
import java.util.Stack;
import java.util.Vector;

import net.sf.javabdd.BDD;
import net.sf.javabdd.BDDVarSet;
import net.sf.javabdd.BDD.BDDIterator;
import edu.wis.jtlv.env.Env;
import edu.wis.jtlv.env.module.ModuleWithWeakFairness;
import edu.wis.jtlv.env.module.Module;
import edu.wis.jtlv.lib.FixPoint;
import edu.wis.jtlv.old_lib.games.GameException;
import edu.wis.jtlv.env.module.ModuleBDDField;

/** 
 * <p>
 * To execute, create an object with two Modules, one for the system and the
 * other for the environment, and then just extract the strategy/counterstrategy 
 * via the printWinningStrategy() and printLosingStrategy() methods.
 * </p>
 * 
 * @author Yaniv Sa'ar, Vasumathi Raman, Cameron Finucane)
 * 
 */
public class GROneGame {
	private ModuleWithWeakFairness env;
	private ModuleWithWeakFairness sys;
	int sysJustNum, envJustNum;
	private BDD player1_winning;
	private BDD player2_winning;


	// p2_winning in GRGAmes are !p1_winning

	public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys, int sysJustNum, int envJustNum)
			throws GameException {
		if ((env == null) || (sys == null)) {
			throw new GameException(
					"cannot instanciate a GR[1] Game with an empty player.");
		}

		//Define system and environment modules, and how many liveness conditions are to be considered. 
		//The first sysJustNum system livenesses and the first envJustNum environment livenesses will be used
		this.env = env;
		this.sys = sys;
		this.sysJustNum = sysJustNum;
		this.envJustNum = envJustNum;

		// for now I'm giving max_y 50, at the end I'll cut it (and during, I'll
		// extend if needed. (using vectors only makes things more complicate
		// since we cannot instantiate vectors with new vectors)
		x_mem = new BDD[sysJustNum][envJustNum][50];
		y_mem = new BDD[sysJustNum][50];
		z_mem = new BDD[sysJustNum];
		x2_mem = new BDD[sysJustNum][envJustNum][50][50];
		y2_mem = new BDD[sysJustNum][50];
		z2_mem = new BDD[50];	

		//
		this.player2_winning = this.calculate_win_alternative();	//(system winning states) -- Call the alternative function (VR)
		this.player1_winning = this.player2_winning.not();   //(environment winning states)
		//this.player1_winning = this.player2_winning.not(); //commented out after counterstrategy addition - VR

	}



	public GROneGame(ModuleWithWeakFairness env, ModuleWithWeakFairness sys)
			throws GameException {
		this(env, sys, sys.justiceNum(), env.justiceNum());
	}


	public BDD[][][] x_mem;
	public BDD[][][][] x2_mem;
	public BDD[][] y_mem, y2_mem;
	public BDD[] z_mem, z2_mem;

	/**
	 * <p>
	 * Calculating Player-2 winning states.
	 * </p>
	 * 
	 * @return The Player-2 winning states for this game.
	 */
	private BDD calculate_win() {
		BDD x, y, z;
		FixPoint<BDD> iterZ, iterY, iterX;
		int cy = 0;

		z = Env.TRUE();
		for (iterZ = new FixPoint<BDD>(); iterZ.advance(z);) {
			for (int j = 0; j < sysJustNum; j++) {
				cy = 0;
				y = Env.FALSE();
				for (iterY = new FixPoint<BDD>(); iterY.advance(y);) {

					BDD start = sys.justiceAt(j).and(env.yieldStates(sys,z))
							.or(env.yieldStates(sys,y));
					y = Env.FALSE();

					for (int i = 0; i < envJustNum; i++) {
						BDD negp = env.justiceAt(i).not();
						x = z.id();
						int ig = 0;
						for (iterX = new FixPoint<BDD>(); iterX.advance(x);) {
							x = negp.and(env.yieldStates(sys,x)).or(start);
						}
						x_mem[j][i][cy] = x.id();
						//System.out.println("X ["+ j + ", " + i + ", " + cy + "] = " + x_mem[j][i][cy]);
						y = y.id().or(x);
					}
					y_mem[j][cy] = y.id();
					//System.out.println("Y ["+ j + "] = " + y_mem[j][cy]);													
					cy++;
					if (cy % 50 == 0) {
						x_mem = extend_size(x_mem, cy);
						y_mem = extend_size(y_mem, cy);
					}
				}
				z = y.id();
				z_mem[j] = z.id();
				//System.out.println("Z ["+ j + " ] = " + z_mem[j]);					
			}
		}
		x_mem = extend_size(x_mem, 0);
		y_mem = extend_size(y_mem, 0);					
		return z.id();
	}


	/**
	 * <p>
	 * Calculating Player-2 winning states.
	 * This program is built for assumptions and guarantees that are transitions rather than states.
	 * The case of states is included as a set of states is equivalent to all the transitions leaving
	 * these states.
	 * </p>
	 * 
	 * @return The Player-2 winning states for this game.
	 */
	private BDD calculate_win_alternative() {
		BDDVarSet envPrimedVars = env.modulePrimeVars();
		BDDVarSet sysPrimedVars = sys.modulePrimeVars();


		BDD x, y, z;
		FixPoint<BDD> iterZ, iterY, iterX;
		int cy = 0;

		z = Env.TRUE();
		for (iterZ = new FixPoint<BDD>(); iterZ.advance(z);) {
			for (int j = 0; j < sysJustNum; j++) {
				cy = 0;
				y = Env.FALSE();
				for (iterY = new FixPoint<BDD>(); iterY.advance(y);) {

					BDD start = sys.justiceAt(j).and(Env.prime(z))
							.or(Env.prime(y));
					y = Env.FALSE();

					for (int i = 0; i < envJustNum; i++) {
						BDD negp = env.justiceAt(i).not();
						x = z.id();
						for (iterX = new FixPoint<BDD>(); iterX.advance(x);) {
							x = this.yieldStatesNext(env,sys,envPrimedVars,sysPrimedVars, negp.and(Env.prime(x)).or(start));			    
						}
						x_mem[j][i][cy] = x.id();
						//System.out.println("X ["+ j + ", " + i + ", " + cy + "] = " + x_mem[j][i][cy]);
						y = y.id().or(x);
					}
					y_mem[j][cy] = y.id();
					//System.out.println("Y ["+ j + "] = " + y_mem[j][cy]);													
					cy++;
					if (cy % 50 == 0) {
						x_mem = extend_size(x_mem, cy);
						y_mem = extend_size(y_mem, cy);
					}
				}
				z = y.id();
				z_mem[j] = z.id();
				//System.out.println("Z ["+ j + " ] = " + z_mem[j]);					
			}
		}
		x_mem = extend_size(x_mem, 0);
		y_mem = extend_size(y_mem, 0);					
		return z.id();
	}

	// A controllable next that accepts a transition as the target
	public BDD yieldStatesNext(Module challenger, Module responder, BDDVarSet challengerPrime, BDDVarSet responderPrime, BDD to) {
		BDD exy = to.and(responder.trans()).exist(responderPrime);
		return challenger.trans().imp(exy).forAll(challengerPrime);
	}

	private BDD[][][][] extend_size(BDD[][][][] in, int extended_size) {
		BDD[][][][] res;
		if (extended_size > 0) {
			res = new BDD[in.length][in[0].length][in[0][0].length + extended_size][in[0][0][0].length
			                                                                        + extended_size];
			for (int i = 0; i < in.length; i++) {
				for (int j = 0; j < in[i].length; j++) {
					for (int k = 0; k < in[i][j].length; k++) {
						for (int m = 0; m < in[i][j][k].length; m++) {
							res[i][j][k][m] = in[i][j][k][m];
						}
					}
				}
			}
		} else {
			res = new BDD[in.length][in[0].length][in[0][0].length][];
			for (int i = 0; i < in.length; i++) {
				for (int j = 0; j < in[i].length; j++) {
					for (int k = 0; k < in[i][j].length; k++) {						
						int real_size = 0;
						for (int m = 0; m < in[i][j][k].length; m++) {
							if (in[i][j][k][m] != null)
								real_size++;
						}
						res[i][j][k] = new BDD[real_size];
						int new_add = 0;
						for (int m = 0; m < in[i][j][k].length; m++) {
							if (in[i][j][k][m] != null) {
								res[i][j][k][new_add] = in[i][j][k][m];
								new_add++;
							}
						}
					}
				}
			}
		}
		return res;
	}	
	// extended_size<=0 will tight the arrays to be the exact sizes.

	private BDD[][][] extend_size(BDD[][][] in, int extended_size) {
		BDD[][][] res;
		if (extended_size > 0) {
			res = new BDD[in.length][in[0].length][in[0][0].length
			                                       + extended_size];
			for (int i = 0; i < in.length; i++) {
				for (int j = 0; j < in[i].length; j++) {
					for (int k = 0; k < in[i][j].length; k++) {
						res[i][j][k] = in[i][j][k];
					}
				}
			}
		} else {
			res = new BDD[in.length][in[0].length][];
			for (int i = 0; i < in.length; i++) {
				for (int j = 0; j < in[i].length; j++) {
					int real_size = 0;
					for (int k = 0; k < in[i][j].length; k++) {
						if (in[i][j][k] != null)
							real_size++;
					}
					res[i][j] = new BDD[real_size];
					int new_add = 0;
					for (int k = 0; k < in[i][j].length; k++) {
						if (in[i][j][k] != null) {
							res[i][j][new_add] = in[i][j][k];
							new_add++;
						}
					}
				}
			}
		}
		return res;
	}

	private BDD[][] extend_size(BDD[][] in, int extended_size) {
		BDD[][] res;
		if (extended_size > 0) {
			res = new BDD[in.length][in[0].length + extended_size];
			for (int i = 0; i < in.length; i++) {
				for (int j = 0; j < in[i].length; j++) {
					res[i][j] = in[i][j];
				}
			}
		} else {
			res = new BDD[in.length][];
			for (int i = 0; i < in.length; i++) {
				int real_size = 0;
				for (int j = 0; j < in[i].length; j++) {
					if (in[i][j] != null)
						real_size++;
				}
				res[i] = new BDD[real_size];
				int new_add = 0;
				for (int j = 0; j < in[i].length; j++) {
					if (in[i][j] != null) {
						res[i][new_add] = in[i][j];
						new_add++;
					}
				}
			}
		}
		return res;
	}

	private BDD[] extend_size(BDD[] in, int extended_size) {
		BDD[] res;		
		if (extended_size > 0) {
			res = new BDD[in.length + extended_size];
			for (int i = 0; i < in.length; i++) {

				res[i] = in[i];

			}
		} else {
			int real_size = 0;
			for (int j = 0; j < in.length; j++) {
				if (in[j] != null)
					real_size++;
			}
			res = new BDD[real_size];
			for (int j = 0; j < real_size; j++) {

				res[j] = in[j];

			}
		}			
		return res;
	}

	/**
	 * <p>
	 * Extracting an arbitrary implementation from the set of possible
	 * strategies. 
	 * The second argument changes the priority of searching for different types of moves in the game
	 * </p>
	 */
	public void printWinningStrategy(BDD ini) {
		calculate_strategy(3, ini);
		// return calculate_strategy(3);
		// return calculate_strategy(7);
		// return calculate_strategy(11);
		// return calculate_strategy(15);
		// return calculate_strategy(19);
		// return calculate_strategy(23);
	}




	/**
	 * <p>
	 * Extracting an implementation from the set of possible strategies with the
	 * given priority to the next step, following the approach outlined in	
	 * </p>
	 * <p>
	 * Nir Piterman, Amir Pnueli, and Yaniv Sa'ar. Synthesis of Reactive(1) Designs.
	 * In VMCAI 2006, pp. 364-380.
	 * </p>
	 * <p>
	 * Possible priorities are:<br>
	 * 3 - Z Y X.<br>
	 * 7 - Z X Y.<br>
	 * 11 - Y Z X.<br>
	 * 15 - Y X Z.<br>
	 * 19 - X Z Y.<br>
	 * 23 - X Y Z.<br>
	 * </p>
	 * 
	 * @param kind
	 *            The priority kind.
	 */


	public void calculate_strategy(int kind, BDD ini) {
		int strategy_kind = kind;
		Stack<BDD> st_stack = new Stack<BDD>();
		Stack<Integer> j_stack = new Stack<Integer>();
		Stack<RawState> aut = new Stack<RawState>();

		// Create a varset of all non-location propositions
		// (used later to prevent inefficient wobbling when
		// multiple goals are satisfied in the same location)
		//
		// TODO: There is probably a cleaner way to do this
		ModuleBDDField [] allFields = sys.getAllFields();        
		BDDVarSet nonRegionProps = Env.getEmptySet();
		for (int i = 0; i < allFields.length; i++) {      
			ModuleBDDField thisField = allFields[i];
			String fieldName = thisField.support().toString();
			if (!fieldName.startsWith("<bit"))
				nonRegionProps = nonRegionProps.union(thisField.support());
		}


		BDDIterator ini_iterator = ini.iterator(env.moduleUnprimeVars().union(sys.moduleUnprimeVars()));
		while (ini_iterator.hasNext()) {
			BDD this_ini = (BDD) ini_iterator.next();

			RawState test_st = new RawState(aut.size(), this_ini, 0);

			int idx = -1;
			for (RawState cmp_st : aut) {
				if (cmp_st.equals(test_st, false)) { // search ignoring rank
					idx = aut.indexOf(cmp_st);
					break;
				}
			}

			if (idx != -1) {
				// This initial state is already in the automaton
				continue;
			}

			// Otherwise, we need to attach this initial state to the automaton

			st_stack.push(this_ini);
			j_stack.push(new Integer(0)); // TODO: is there a better default j?
			//this_ini.printSet();

			// iterating over the stacks.
			while (!st_stack.isEmpty()) {
				// making a new entry.
				BDD p_st = st_stack.pop();
				int p_j = j_stack.pop().intValue();

				/* 
				 * Create a new automaton state for our current state 
				 * (or use a matching one if it already exists) 
				 * p_st is the current state value,
				 * and p_j is the system goal currently being pursued.
				 * cf. RawState class definition below.
				 */
				RawState new_state = new RawState(aut.size(), p_st, p_j);
				int nidx = aut.indexOf(new_state);
				if (nidx == -1) {
					aut.push(new_state);
				} else {
					new_state = aut.elementAt(nidx);
				}

				/* Find Y index of current state */
				// find minimal cy and an i
				int p_cy = -1;
				for (int i = 0; i < y_mem[p_j].length; i++) {
					if (!p_st.and(y_mem[p_j][i]).isZero()) {
						p_cy = i;
						break;
					}
				}

				assert p_cy >= 0 : "Couldn't find p_cy";
				/* Find  X index of current state */
				int p_i = -1;
				for (int i = 0; i < envJustNum; i++) {
					if (!p_st.and(x_mem[p_j][i][p_cy]).isZero()) {
						p_i = i;
						break;
					}
				}
				assert p_i >= 0 : "Couldn't find p_i";

				// computing the set of env possible successors.
				Vector<BDD> succs = new Vector<BDD>();
				BDD all_succs =  env.succ(p_st);

				for (BDDIterator all_states = all_succs.iterator(env
						.moduleUnprimeVars()); all_states.hasNext();) {
					BDD sin = (BDD) all_states.next();
					succs.add(sin);
				}

				BDD candidate = Env.FALSE();
				// For each env successor, find a strategy successor
				for (Iterator<BDD> iter_succ = succs.iterator(); iter_succ
						.hasNext();) {
					BDD primed_cur_succ = Env.prime(iter_succ.next());
					BDD next_op = Env.unprime(sys.trans().and(p_st).and(primed_cur_succ)
							.exist(
									env.moduleUnprimeVars().union(
											sys.moduleUnprimeVars()))).and(this.player2_winning);
					System.out.println("Searching what to do with: " + next_op);

					candidate = Env.FALSE();
					int jcand = p_j;

					int local_kind = strategy_kind;
					while (candidate.isZero() & (local_kind >= 0)) {
						// a - first successor option in the strategy.
						// (rho_1 in Piterman; satisfy current goal and move to next goal)
						if ((local_kind == 3) | (local_kind == 7)
								| (local_kind == 10) | (local_kind == 13)
								| (local_kind == 18) | (local_kind == 21)) {
							BDD trans = p_st.and(Env.prime(next_op));			    
							BDD trans_and_just = trans.and(sys.justiceAt(p_j));
							if (!trans_and_just.isZero()) {
								int next_p_j = (p_j + 1) % sysJustNum;   
								// Cycle through goals that are trivially satisfied by staying in the exact same state.
								// (This is essentially stutter-state removal)
								while (!trans_and_just.and(sys.justiceAt(next_p_j)).isZero() && next_p_j != p_j) {
									trans_and_just = trans_and_just.and(sys.justiceAt(next_p_j));
									next_p_j = (next_p_j + 1) % sysJustNum;
								}

								BDD next_of_trans_and_just = Env.unprime(trans_and_just.exist(sys.moduleUnprimeVars()).exist(env.moduleUnprimeVars())); 
								//BDD next_of_trans = Env.unprime(trans.exist(sys.moduleUnprimeVars()).exist(env.moduleUnprimeVars())); 

								// Find the lowest-rank transitionable state in the direction of the next unsatisfied goal
								// (or just stay in the same y-set if we've looped all the way around)
								int look_r = 0;
								while ((next_of_trans_and_just.and(y_mem[next_p_j][look_r]).isZero())) {
									//while ((next_of_trans.and(y_mem[next_p_j][look_r]).isZero())) {
									look_r++;
								}

								BDD opt = next_of_trans_and_just.and(y_mem[next_p_j][look_r]);
								//BDD opt = next_of_trans.and(y_mem[next_p_j][look_r]);
								if (!opt.isZero()) {
									candidate = opt;
									System.out.println("1");
									jcand = next_p_j;
								}

								// If possible, trim down the candidates to prioritize movement-less transitions
								BDD current_region = p_st.exist(env.moduleUnprimeVars()).exist(nonRegionProps);
								if (!candidate.and(current_region).isZero()) {
									candidate = candidate.and(current_region); 
								}
							}

						}                       
						// b - second successor option in the strategy.
						// (rho_2 in Piterman; move closer to current goal)
						if ((local_kind == 2) | (local_kind == 5)
								| (local_kind == 11) | (local_kind == 15)
								| (local_kind == 17) | (local_kind == 22)) {
							if (p_cy > 0) {
								int look_r = 0;
								// look for the further most r.
								while ((next_op.and(y_mem[p_j][look_r]).isZero())
										& (look_r < p_cy)) {
									look_r++;
								}

								BDD opt = next_op.and(y_mem[p_j][look_r]);
								if ((look_r != p_cy) && (!opt.isZero())) {
									candidate = opt;  
									System.out.println("2");
								}
							}
						}

						// c - third successor option in the strategy.
						// (rho_3 in Piterman; falsify environment :()
						if ((local_kind == 1) | (local_kind == 6)
								| (local_kind == 9) | (local_kind == 14)
								| (local_kind == 19) | (local_kind == 23)) {
							BDD trans = p_st.and(Env.prime(next_op));
							BDD trans_and_not_just = trans.and(env.justiceAt(p_i).not());
							if (!trans_and_not_just.isZero()) {
								BDD next_of_trans_and_not_just = Env.unprime(trans_and_not_just.exist(sys.moduleUnprimeVars()).exist(env.moduleUnprimeVars()));
								BDD opt = next_of_trans_and_not_just.and(x_mem[p_j][p_i][p_cy]);
								if (!opt.isZero()) {
									candidate = opt;
									System.out.println("3");
								}
							}
						}

						// no successor was found yet.
						//assert ((local_kind != 0) & (local_kind != 4)
						if (!((local_kind != 0) & (local_kind != 4)
								& (local_kind != 8) & (local_kind != 12)
								& (local_kind != 16) & (local_kind != 20))) {
							System.out.println("No successor was found");
							candidate = (next_op).and(y_mem[p_j][p_cy]);	
							assert !(candidate.isZero()) : "No successor was found";

						}

						local_kind--;
					}


					//BDD one_cand = candidate.satOne();

					
					BDDIterator candIter = candidate.iterator(env.moduleUnprimeVars().union(
                            sys.moduleUnprimeVars())); 
                    BDD one_cand = (BDD) candIter.next();
                                   
                    					

					RawState gsucc = new RawState(aut.size(), one_cand, jcand);
					idx = aut.indexOf(gsucc); // the equals doesn't consider
					// the id number.
					if (idx == -1) {
						st_stack.push(one_cand);
						j_stack.push(jcand);
						aut.add(gsucc);
						idx = aut.indexOf(gsucc);
					}
					new_state.add_succ(aut.elementAt(idx));
					System.out.println("added " + this + " as succcesoor of that.");
				}
			}
		}

		/* Remove stuttering */
		// TODO: Make this more efficient (and less ugly) if possible
		/*
	  int num_removed = 0;

	  for (RawState state1 : aut) {
	  int j1 = state1.get_rank();
	  for (RawState state2 : state1.get_succ()) {
	  int j2 = state2.get_rank();
	  if ((j2 == (j1 + 1) % sys.justiceNum()) &&
	  state1.equals(state2, false)) {
	  // Find any states pointing to state1
	  for (RawState state3 : aut) {
	  if (state3.get_succ().indexOf(state1) != -1) {
	  // Redirect transitions to state2
	  state3.del_succ(state1); 
	  state3.add_succ(state2); 
	  // Mark the extra state for deletion 
	  state1.set_rank(-1);
	  }
	  }
	  }
	  }

	  if (state1.get_rank() == -1) {
	  num_removed++;
	  }

	  }


	  System.out.println("Removed " + num_removed + " stutter states.");

		 */

		/* Print output */




		String res = "";

		for (RawState state : aut) {
			if (state.get_rank() != -1) {
				res += state + "\n";
			}
		}

		System.out.print("\n\n");
		System.out.print(res);
		// return null; // res;
		System.out.print("\n\n");

	}



	@SuppressWarnings("unused")
	//Class for a state of the STRATEGY automaton. 
	//The "rank" is the system goal currently being pursued.
	private class RawState {
		private int id;
		private int rank;
		private BDD state;
		private Vector<RawState> succ;

		public RawState(int id, BDD state, int rank) {
			this.id = id;
			this.state = state;
			this.rank = rank;
			succ = new Vector<RawState>(10);
		}

		public void add_succ(RawState to_add) {
			succ.add(to_add);
		}

		public void del_succ(RawState to_del) {
			succ.remove(to_del);
		}

		public BDD get_state() {
			return this.state;
		}

		public int get_rank() {
			return this.rank;
		}

		public void set_rank(int rank) {
			this.rank = rank;
		}

		public Vector<RawState> get_succ() {
			//RawState[] res = new RawState[this.succ.size()];
			//this.succ.toArray(res);
			return this.succ;
		}

		public boolean equals(Object other) {
			return this.equals(other, true);
		}

		public boolean equals(Object other, boolean use_rank) {
			if (!(other instanceof RawState))
				return false;
			RawState other_raw = (RawState) other;
			if (other_raw == null)
				return false;

			if (use_rank) {
				return ((this.rank == other_raw.rank) & (this.state
						.equals(other_raw.state)));
			} else {
				return (this.state.equals(other_raw.state));
			}
		}

		public String toString() {
			String res = "State " + id + " with rank " + rank + " -> "
					+ state.toStringWithDomains(Env.stringer) + "\n";
			if (succ.isEmpty()) {
				res += "\tWith no successors.";
			} else {
				RawState[] all_succ = new RawState[succ.size()];
				succ.toArray(all_succ);
				res += "\tWith successors : " + all_succ[0].id;
				for (int i = 1; i < all_succ.length; i++) {
					res += ", " + all_succ[i].id;
				}
			}
			return res;
		}
	}


	//Class for a state of the COUNTERSTRATEGY automaton.  
	//"rank_i" is the environment goal currently being pursued, 
	//and "rank_j" is the system goal currently being prevented.
	private class RawCState {
		private int id;
		private int rank_i;
		private int rank_j;
		private BDD input;
		private BDD state;
		private Vector<RawCState> succ;		


		public RawCState(int id, BDD state, int rank_j, int rank_i, BDD input) {
			this.id = id;
			this.state = state;
			this.rank_i = rank_i;
			this.rank_j = rank_j;
			this.input = input;
			succ = new Vector<RawCState>(10);
		}

		public void add_succ(RawCState to_add) {
			succ.add(to_add);
		}

		public void del_succ(RawCState to_del) {
			succ.remove(to_del);
		}


		public BDD get_input() {
			return this.input;
		}

		public void set_input(BDD input) {
			this.input = input;
		}

		public BDD get_state() {
			return this.state;
		}

		public int get_rank_i() {
			return this.rank_i;
		}

		public void set_rank_i(int rank) {
			this.rank_i = rank;
		}

		public int get_rank_j() {
			return this.rank_j;
		}

		public void set_rank_j(int rank) {
			this.rank_j = rank;
		}


		public boolean equals(Object other) {
			return this.equals(other, true);
		}

		public boolean equals(Object other, boolean use_rank) {
			if (!(other instanceof RawCState))
				return false;
			RawCState other_raw = (RawCState) other;
			if (other_raw == null)
				return false;
			if (use_rank) {
				return ((this.rank_i == other_raw.rank_i) & (this.rank_j == other_raw.rank_j) &
						(this.state.equals(other_raw.state)));
			} else {
				return ((this.state.equals(other_raw.state)));
			}
		}


		public String toString() {
			String res = "State " + id + " with rank (" + rank_i + "," + rank_j + ") -> " 
					+ state.toStringWithDomains(Env.stringer) + "\n";
			if (succ.isEmpty()) {
				res += "\tWith no successors.";				
			} else {
				RawCState[] all_succ = new RawCState[succ.size()];
				succ.toArray(all_succ);
				res += "\tWith successors : " + all_succ[0].id;
				for (int i = 1; i < all_succ.length; i++) {
					res += ", " + all_succ[i].id;
				}
			}
			return res;
		}
	}

	/**
	 * <p>
	 * Getter for the environment player.
	 * </p>
	 * 
	 * @return The environment player.
	 */
	public ModuleWithWeakFairness getEnvPlayer() {
		return env;
	}

	/**
	 * <p>
	 * Getter for the system player.
	 * </p>
	 * 
	 * @return The system player.
	 */
	public ModuleWithWeakFairness getSysPlayer() {
		return sys;
	}

	/**
	 * <p>
	 * Getter for the environment's winning states.
	 * </p>
	 * 
	 * @return The environment's winning states.
	 */
	public BDD sysWinningStates() {
		return player2_winning;
	}

	/**
	 * <p>
	 * Getter for the system's winning states.
	 * </p>
	 * 
	 * @return The system's winning states.
	 */
	public BDD envWinningStates() {
		return player2_winning.not();
	}

	public BDD gameInitials() {
		return getSysPlayer().initial().and(getEnvPlayer().initial());
	}

	public BDD[] playersWinningStates() {
		return new BDD[] { envWinningStates(), sysWinningStates() };
	}

	public BDD firstPlayersWinningStates() {
		return envWinningStates();
	}

	public BDD secondPlayersWinningStates() {
		return sysWinningStates();
	}

}
