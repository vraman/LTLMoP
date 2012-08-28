import net.sf.javabdd.BDD;
import net.sf.javabdd.BDDVarSet;
import net.sf.javabdd.BDD.BDDIterator;
import edu.wis.jtlv.env.Env;
import edu.wis.jtlv.env.module.SMVModule;
import edu.wis.jtlv.env.spec.Spec;
import java.io.File;
import java.io.PrintStream;
import edu.wis.jtlv.lib.FixPoint;

public class GROneMain {

	/**
	 * @param args
	 * @throws Exception
	 */
	public static void main(String[] args) throws Exception {
		// uncomment to use a C BDD package
		//System.setProperty("bdd", "buddy");

		GROneParser.just_initial = true;
		// GRParser.just_safety = true;

        // Check that we have enough arguments
        if (args.length < 2) {
            System.err.println("Usage: java GROneMain [smv_file] [ltl_file]");
            System.exit(1);
        }                

        Env.loadModule(args[0]);
        Spec[] spcs = Env.loadSpecFile(args[1]);

        // Figure out the name of our output file by stripping the spec filename extension and adding .aut
        String out_filename = args[1].replaceAll("\\.[^\\.]+$",".aut");

		// constructing the environment module.
		SMVModule env = (SMVModule) Env.getModule("main.e");
		Spec[] env_conjuncts = GROneParser.parseConjuncts(spcs[0]);
		GROneParser.addReactiveBehavior(env, env_conjuncts);
		// GRParser.addPureReactiveBehavior(env, env_conjuncts);

		// constructing the system module.
		SMVModule sys = (SMVModule) Env.getModule("main.s");
		Spec[] sys_conjuncts = GROneParser.parseConjuncts(spcs[1]);
		GROneParser.addReactiveBehavior(sys, sys_conjuncts);
		//GROneParser.addPureReactiveBehavior(sys, sys_conjuncts);

		// env.setFullPrintingMode(true);
		// System.out.println(env);
		// sys.setFullPrintingMode(true);
		// System.out.println(sys);

		// ***** playing the game

		System.out.print("==== Constructing and playing the game ======\n");
		long time = System.currentTimeMillis();
		GROneGame g = new GROneGame(env,sys);
		long t1 = (System.currentTimeMillis() - time);
		System.out.println("Games time: " + t1);
		
	 ///////////////////////////////////////////////
		 ///////////////////////////////////////////////
		 //old
		 BDD all_init = g.getSysPlayer().initial().and(g.getEnvPlayer().initial());
		 BDD counter_exmple = g.envWinningStates().and(all_init);
		 if (!counter_exmple.isZero()) {
		 System.out.println("Specification is unrealizable...");
		 System.out.println("The env player can win from states:");
		 System.out.println("\t" + counter_exmple);
		 
         return;     
		 } 

		// ///////////////////////////////////////////////
		// ///////////////////////////////////////////////
		// Let win := winm(nps,nqs);
		// Let initial := I(1) & I(2);
		// Let right := (I(2) & win) forsome vars2;
		// Let counter := I(1) & !right;
		// If (counter)
		// Print "\n Specification is unrealizable\n";
		// Print counter;
		// Let realizable := 0;
		// Return;
		// Else
		// Let realizable := 1;
		// End -- If (counter)
		// ///////////////////////////////////////////////
		// ///////////////////////////////////////////////

		// ///////////////////////////////////////////////
		// ///////////////////////////////////////////////
	/*	// new
		BDD env_ini = g.getEnvPlayer().initial();
		BDDVarSet env_vars = g.getEnvPlayer().moduleUnprimeVars();
		for (BDDIterator it = env_ini.iterator(env_vars); it.hasNext();) {
			System.out.println("IN DA LOOP");			
			BDD eini = (BDD) it.next();
			BDD sys_response = eini.and(g.getSysPlayer().initial()).and(
					g.sysWinningStates());
            System.out.println("---------------");
            sys_response.printSet();
			if (sys_response.isZero()) {
				System.out.println("Specification is unrealizable...");
				System.out.println("The env player can win from states:");
				System.out.println("\t" + eini);
				System.out.println("===== Done ==============================");
				return;
			}
		}*/
		// otherwise we can synthesis
		
		System.out.println("Specification is realizable...");
		System.out.println("==== Building an implementation =========");
		System.out.println("-----------------------------------------");
		PrintStream orig_out = System.out;
		System.setOut(new PrintStream(new File(out_filename))); // writing the output to a file
		/*
        g.printWinningStrategy(g.getEnvPlayer().initial().and(
				g.getSysPlayer().initial()).satOne(env.moduleUnprimeVars().union(
						sys.moduleUnprimeVars()), false));  // Added BDDVarSet argument so that initial condition is fully specified -Cameron
        */
		g.printWinningStrategy(g.getEnvPlayer().initial().and(
	               g.getSysPlayer().initial()));
		System.setOut(orig_out); // restore STDOUT
		System.out.print("-----------------------------------------\n");
		long t2 = (System.currentTimeMillis() - time);
		System.out.println("Strategy time: " + t2);
		System.out.println("===== Done ==============================");
		
	
	}
	
}
