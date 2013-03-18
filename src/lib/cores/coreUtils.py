
import math, re, sys, random, os, subprocess, time
from copy import copy, deepcopy
from logic import to_cnf
from multiprocessing import Pool
import threading
import itertools






def conjunctsToCNF(conjuncts, propList):
    #takes a list of LTL formulas and a list of propositions used in them,
    #and converts them into DIMACS CNF format replacing each proposition
    #with its index in the list. 
    #returns:
    #         mapping: a mapping from LTL formulas to CNF clause numbers
    #         cnfMapping: a mapping from LTL formulas to CNFs 
    #         cnfClauses: CNFS corresponding to initial and transition formulas
    #                     (represents one-step unrolling)
    #         transClauses: CNFS corresponding to transition formulas
    #                     (useful for further unrolling later)
    #         goalClauses: CNFS corresponding to goal formulas
    #                     (useful for checking goals at each time step)
    
    propListNext = map(lambda s: 'next_'+s, propList)
    
    props = {propList[x]:x+1 for x in range(0,len(propList))}
    propsNext = {propListNext[x]:len(propList)+x+1 for x in range(0,len(propListNext))}
    
    #print props
    
    mapping = {conjuncts[x]:[] for x in range(0,len(conjuncts))}
    cnfMapping = {conjuncts[x]:[] for x in range(0,len(conjuncts))}
    
    cnfClauses = []
    transClauses = []
    goalClauses = []
    n = 0 #counts number of clauses generated for mapping LTL to line numbers
    p = len(props)+len(propsNext)  
    
    
    pool = Pool()
    print "STARTING CNF MAP"
    allCnfs = map(lineToCnf, conjuncts)#, chunksize = 1)   
    #allCnfs = map(lineToCnf, conjuncts)   
    print "ENDING CNF MAP"
    pool.terminate()
    
          
    for cnf, lineOld in zip(allCnfs,conjuncts):     
      if cnf != '': 
        allClauses = cnf.split("&");
        for clause in allClauses:    
            clause = cnfToDimacs(clause)
            #replace prop names with var numbers
            for k in propsNext.keys():
                clause = re.sub("\\b"+k+"\\b",str(propsNext[k]), clause)
            for k in props.keys():
                clause = re.sub("\\b"+k+"\\b",str(props[k]), clause)   
            #add trailing 0   
            clause = clause.strip()+" 0\n"
            if "<>" in lineOld:
                goalClauses.append(clause)
            elif "[]" in lineOld:
                transClauses.append(clause)
                cnfClauses.append(clause)                                
            else:
                cnfClauses.append(clause)     
            #associate original LTL conjuncts with CNF clauses
            cnfMapping[lineOld].append(clause)
            
        if not "<>" in lineOld:
            #for non-goal (i.e. trans and init) formulas, extend mapping with line nos.
            #the guilty goal is always put last, so we don't need the clause nos.
            mapping[lineOld].extend(range(n+1,n+1+len(allClauses)))    
            n = n + len(allClauses)
                        
    return mapping, cnfMapping, cnfClauses, transClauses, goalClauses
    
def cnfToDimacs(clause):
    clause = re.sub('[()]', '', clause)   
    clause = re.sub('[|]', '', clause)           
    clause = re.sub('~', '-', clause) 
    return clause

            
def cnfToConjuncts(cnfIndices, mapping, cnfMapping):
    #takes a list of cnf line numbers and returns the corresponding LTL
    conjuncts = [] 
    for k in mapping.keys():
        if not set(mapping[k]).isdisjoint(cnfIndices):
            #conjuncts.append((k))
            conjuncts.append((k, [cnfMapping[k][index%len(cnfMapping[k])] for (index, value) in enumerate(mapping[k]) if value in cnfIndices]))             
    #return conjuncts
    return cleanedConjuncts(conjuncts, cnfMapping)
 
def printConflictCNFs(conjuncts, proplist, depth):
    for c in conjuncts:
        for d in depth:
            print c(1).replace(proplist)

def cleanedConjuncts(conjuncts, cnfMapping):
    sorted_by_num_clauses = sorted(conjuncts, key=lambda tup: -len(tup[1]))
    result = []
    allCnfs = set([c for ltl, cnf in conjuncts for c in cnf])        
    for ltl, cnf in sorted_by_num_clauses:
            result.append(ltl)
            for x in cnf:
                if x in allCnfs:
                    allCnfs.remove(x) 
    return result
         
       
def lineToCnf(line):
        #converts a single LTL formula into CNF form 
        line = stripLTLLine(line)        
        line = re.sub('!', '~', line)
        #line = re.sub('&\s*\n', '', line)
        line = re.sub('[\s]+', ' ', line)        
        line = re.sub('\<-\>', '<=>', line)
        line = re.sub('->', '>>', line)
        line = line.strip()         
        if line!='':  
            cnf = str(to_cnf(line))   
            return cnf
        else:
            return line        
        
        
    
def stripLTLLine(line, useNext=False):
        #strip white text and LTL operators           
        line = re.sub('[\t\n]*','',line)    
        line = re.sub('\<\>','',line)  
        line = re.sub('\[\]','',line)  
        line = line.strip()
        #trailing &
        line = re.sub('&\s*$','',line)           
        if useNext:
            line = re.sub('s\.','next_s.',line)
            line = re.sub('e\.','next_e.',line)               
        line = re.sub('s\.','',line)
        line = re.sub('e\.','',line)   
        line = re.sub(r'(next\(\s*!)', r'(!next_', line)         
        line = re.sub(r'(next\()', r'(next_', line)                         
        return line
        
def subprocessReadThread(fd, out):
            for line in fd:                                                                              
               out.append(line) 
                
        
def findGuiltyLTLConjunctsWrapper(x):        
        return findGuiltyLTLConjuncts(*x)


        
def findGuiltyLTLConjuncts(cmd, depth, numProps, init, trans, goals, mapping,  cnfMapping, conjuncts, ignoreDepth): 
        #returns the ltl conjuncts returned as an unsat core when unrolling trans depth times from init and 
        #checking goal at final time step
        #note that init contains one-step unrolling of trans already
        
        mapping = deepcopy(mapping)
        #precompute p and n
        p = (depth+2)*(numProps) + 1000
        #the +2 is because init contains one trans already 
        #(so effectively there are depth+1 time steps and one final "next" time step)        
        
        n = (depth)*(len(trans)) + len(init) + len(goals)
        if ignoreDepth == 0:
            ignoreBound = 0
        else:
            ignoreBound = len(init) + ignoreDepth*len(trans)
        
        output = []
        
        #find minimal unsatisfiable core by calling picomus
        if cmd is None:
            return (False, False, [], "")   
                
        #start a reader thread        
        subp = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, close_fds=False)                                            
        readThread =  threading.Thread(target = subprocessReadThread, args=(subp.stdout,output))
        readThread.daemon = True
        readThread.start()
        
        
        #send header
        input = "p cnf "+str(p)+" "+str(n)+"\n"
        subp.stdin.write(input)                     
        subp.stdin.writelines(init)    

        #Duplicating transition clauses for depth greater than 1         
        numOrigClauses = len(trans)  
        #the depth tells you how many time steps of trans to use
        #depth 0 just checks init with goals
        
        
        for i in range(1,depth+1):
                    for clause in trans:
                        newClause = ""
                        for c in clause.split():
                            intC = int(c)
                            newClause= newClause + str(cmp(intC,0)*(abs(intC)+numProps*i)) +" "                            
                        newClause=newClause+"\n"                                                         
                        #send this clause
                        #print newClause
                        subp.stdin.write(newClause)
                        
                    j = 0    
                    for line in conjuncts:
                        if "[]" in line and "<>" not in line:                      
                            numVarsInTrans = (len(mapping[line]))/(i+1)
                            mapping[line].extend(map(lambda x: x+numOrigClauses, mapping[line][-numVarsInTrans:]))
                            j = j + 1
                    #transClauses.extend(transClausesNew)  
                    
        #create goal clauses
        dg = map(lambda x: ' '.join(map(lambda y: str(cmp(int(y),0)*(abs(int(y))+numProps*(depth))), x.split())) + '\n', goals)  
        #send goalClauses
        subp.stdin.writelines(dg)
        #send EOF
        subp.stdin.close()
        
                                
        #update mapping with newly added clause line numbers
        nMinusG = n - len(goals)
        for line in conjuncts:
            if "<>" in line:
                mapping[line] = range(nMinusG+1,nMinusG+len(goals)+1)
                
        
        readThread.join()
        
    

        
                
                                                                                      
        sys.stdout = sys.__stdout__
        sys.stderr = sys.__stderr__

        if any(["WARNING: core extraction disabled" in s for s in output]):
            # never again
            print "************************************************"
            print "*** ERROR: picomus needs to be compiled with ***"
            print "*** trace support, or things will misbehave. ***"
            print "***                                          ***"
            print "*** Recompile with ./configure --trace       ***"
            print "************************************************"
            return []

        if any(["UNSATISFIABLE" in s for s in output]):
            print "Unsatisfiable core found at depth ", depth
        elif any(["SATISFIABLE" in s for s in output]):
            print "Satisfiable at depth ", depth
            #sat = filter(lambda y: int(y)!=0, map((lambda x: x.strip('v').strip()), filter(lambda z: re.match('^v', z), output)))
            #print " & ".join(sat)        
            return []
        else:
            print "ERROR", output
            
                    
            
            
        """#Write output to file (mainly for debugging purposes)
            satFileName = self.proj.getFilenamePrefix()+".sat"
            outputFile = open(satFileName,'w')
            outputFile.write(output)
            outputFile.close()
            """
            
    
        
        """cnfIndices = []
        for line in output.split('\n'):
                if re.match('^v', line):
                    index = int(line.strip('v').strip())
                    if index!=0:
                        cnfIndices.append(index)
            """
        ignoreBound = 0
        #pythonified the above
        #get indices of contributing clauses
        cnfIndices = filter(lambda y: y!=0, map((lambda x: int(x.strip('v').strip())), filter(lambda z: re.match('^v', z), output)))
        
       
        #get contributing conjuncts from CNF indices           
        guilty = cnfToConjuncts([idx for idx in cnfIndices if idx > ignoreBound], mapping, cnfMapping)
        
        return guilty
    
 
def unsatCoreCasesWrapper(x): 
    return unsatCoreCases(*x) 
    
def unsatCoreCases(cmd, propList, topo, badInit, conjuncts, maxDepth, numRegions, extra=[]):
     #returns the minimal unsatisfiable core (LTL formulas) given
     #        cmd: picosat command
     #        propList: list of proposition names used
     #        topo: LTL formula describing topology
     #        badInit: formula describing bad initial states
     #        conjuncts: remaining LTL formulas highlighted by preliminary analysis
     #        maxDepth: determines how many time steps we unroll 
     #        numRegions: used to determine minimum depth to prevent false alarms (every depth between numRegions+1 and maxDepth is checked)
       
        numProps = len(propList)
        #initial depth is set to the number of regions. This ensures that we unroll at least as 
        #far as needed to physically get to the goal
        depth = numRegions
        
        #if len(extra) > 0:
        #    maxDepth = len(extra)   
        
        extra = [x for e in extra for x in e]            
        
        #first try without topo and init, see if it is satisfiable
        ignoreDepth = 0    
        mapping, cnfMapping, init, trans, goals = conjunctsToCNF([badInit]+conjuncts, propList)
        init.extend(extra)
           
        pool = Pool()
                      
            #print "STARTING PICO MAP"
            
        guiltyList = map(findGuiltyLTLConjunctsWrapper, itertools.izip(itertools.repeat(cmd),range(0,maxDepth + 1), itertools.repeat(numProps), itertools.repeat(init), itertools.repeat(trans), itertools.repeat(goals), itertools.repeat(mapping), itertools.repeat(cnfMapping), itertools.repeat([badInit]+conjuncts),itertools.repeat(ignoreDepth)))
            #allGuilty = map((lambda (depth, cnfs): self.guiltyParallel(depth+1, cnfs, mapping)), list(enumerate(allCnfs)))
            #print "ENDING PICO MAP"
            
        pool.terminate()
            
        allGuilty = set([item for sublist in guiltyList for item in sublist])
    
        if all((map(lambda x: x !=[], guiltyList))):
            print "unsat core found without topo and init"
            return trans, allGuilty
        else:
            ignoreDepth = len([g for g in allGuilty if g])
            depth += ignoreDepth
            
        #then try just topo and init and see if it is unsatisfiable. If so, return core.
        mapping,  cnfMapping, init, trans, goals = conjunctsToCNF([topo, badInit], propList)
        init.extend(extra)
                    
        guilty = findGuiltyLTLConjuncts(cmd,maxDepth,numProps,init,trans,goals,mapping,cnfMapping,[topo, badInit],0)
        
                #allGuilty = map((lambda (depth, cnfs): self.guiltyParallel(depth+1, cnfs, mapping)), list(enumerate(allCnfs)))
            #print "ENDING PICO MAP"
        
        if guilty:
            print "unsat core found with just topo and init"
            return trans, guilty
        
        #if the problem is in conjunction with the topo but not just topo, keep increasing the depth until something more than just topo is returned
        mapping,  cnfMapping, init, trans, goals = conjunctsToCNF([topo,badInit] + conjuncts, propList)
        init.extend(extra)
        
        pool = Pool()
                      
            #print "STARTING PICO MAP"
            
            
        guiltyList = map(findGuiltyLTLConjunctsWrapper, itertools.izip(itertools.repeat(cmd),range(maxDepth,maxDepth + 1), itertools.repeat(numProps), itertools.repeat(init), itertools.repeat(trans), itertools.repeat(goals), itertools.repeat(mapping),  itertools.repeat(cnfMapping), itertools.repeat([topo, badInit]+conjuncts), itertools.repeat(ignoreDepth)))
            #allGuilty = map((lambda (depth, cnfs): self.guiltyParallel(depth+1, cnfs, mapping)), list(enumerate(allCnfs)))
            #print "ENDING PICO MAP"
            
        pool.terminate()
        
        guilty = [item for sublist in guiltyList for item in sublist]    
        
        guiltyMinusGoal = [g for g in guilty if '<>' not in g]
        
#        print "guiltyMinusGoal", guiltyMinusGoal
#        print "topo, badInit", [topo, badInit]
#        print "intersect", set(guiltyMinusGoal).intersection(set([topo, badInit]))
#        print "superset", set([topo, badInit]).issuperset(guiltyMinusGoal)
      

        # don't use ignoreDepth for deadlock
        if len(goals) == 0:
           ignoreDepth = 0 
        
           
        justTopo = set([topo, badInit]).issuperset(guiltyMinusGoal)
        depth = maxDepth + 1
        
        while justTopo:
            
            guilty = findGuiltyLTLConjuncts(cmd,depth,numProps,init,trans,goals,mapping,cnfMapping,[topo, badInit]+conjuncts, ignoreDepth)
            #allGuilty = map((lambda (depth, cnfs): self.guiltyParallel(depth+1, cnfs, mapping)), list(enumerate(allCnfs)))
            #print "ENDING PICO MAP"
            
            
            guiltyMinusGoal = [g for g in guilty if '<>' not in g]
            if not set([topo, badInit]).issuperset(set(guiltyMinusGoal)):
                justTopo = False
            else:
                depth+=1
            
        print "unsat core found with all parts" 
        
        return trans, guilty
    
def stateToLTL(state, useEnv=1, useSys=1, use_next=False):
        def decorate_prop(prop, polarity):
            if int(polarity) == 0:
                prop = "!"+prop
            if use_next:
                prop = "next({})".format(prop)
            return prop
            
       
        sys_state = " & ".join([decorate_prop("s."+p, v) for p,v in state.inputs.iteritems()])
        env_state = " & ".join([decorate_prop("e."+p, v) for p,v in state.outputs.iteritems()])
        
        if useEnv:
            if useSys and env_state!='':
                return env_state + " & " + sys_state
            else:
                return env_state
        elif useSys:
            return sys_state
        else:
            return ""
        
        

def stateCycleToCNFs(cycle, propList, depth): 
    #expanding the cycle out to the required depth
    
    depth = max(depth, len(cycle)) 
    
    propListNext = map(lambda s: 'next_'+s, propList)
    
    props = {propList[x]:x+1 for x in range(0,len(propList))}
    propsNext = {propListNext[x]:len(propList)+x+1 for x in range(0,len(propListNext))}
    
    def replaceProps(cnfs, depth):
        newCnfs = []
        allClauses = cnfs.split("&");      
        for clause in allClauses:
            #replace prop names with var numbers
            for k in propsNext.keys():
                clause = re.sub("\\b"+k+"\\b",str(propsNext[k]+depth*len(propList)), clause)
            for k in props.keys():
                clause = re.sub("\\b"+k+"\\b",str(props[k]+depth*len(propList)), clause)   
            #add trailing 0   
            clause = clause.strip()+" 0\n"
            newCnfs.append(clause)
        return newCnfs
    
    singleTime = [stripLTLLine(stateToLTL(s,1,0)) for s in cycle]
    singleTimeCnfs = [cnfToDimacs(lineToCnf(s)) for s in singleTime]
    print singleTimeCnfs
    
    unrollTime = []
    d = 0
    while d < depth:
      tempD = d
      for index, line in enumerate(singleTimeCnfs, d):
        unrollTime.append(replaceProps(line, index))
        tempD = tempD + 1
        if tempD == depth:
            break
      d = tempD
    
    #unrollTime.append(replaceProps(singleTimeCnfs[0], len(singleTimeCnfs)))
    return unrollTime
        
             
             
    
    
    
    
    
        
            
            
        
        
