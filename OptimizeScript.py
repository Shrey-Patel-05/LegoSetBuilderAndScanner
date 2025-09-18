def Substitute1x1(Brick, inventory,DimensionPartIDTable):
    
    # We remove from the copy instead or original table in case we cannot substitute
    # (so we can use the A x B x 1/3 's later) 
    CopyInventory= inventory.Copy()
    
    CanBeSubstituted= [0,0,0]

    # Try to find three 1 x 1 x 1/3's
    for i in range(0,3):
        CanBeSubstituted[i] =int(SearchAndRemove([1,1,1.3],CopyInventory,DimensionPartIDTable)[0])
            
    #If we can substitute, actually remove these elements from the collection pool   
    if CanBeSubstituted== [1,1,1]:
        return [True,CopyInventory]
    else:
        return [False,inventory]

           
            
def RearrangeDimensions(dim_part_1,dim_part_2):
    if dim_part_1 > dim_part_2:
        return [dim_part_2,dim_part_1]
    else:
        return [dim_part_1,dim_part_2]
     
    
def ReduceSize(H,B,D,E):
    H-=1
    D=H
    E=B-D
    return [H,B,D,E]
    
def Split2xB(Brick, depth, inventory, DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates):

    # To mantain data consistency (preventing permenant changes too early)
    CanBeSubstituted= False
        
    # If there is a thrid dimension...
    if len(Brick)==3 and UseOfPlates== True: 
        # Treat as block 1 x B x 1/3 == A-1 x B x 1/3
        SplitLego= [Brick[0]-1,Brick[1],1.3]
    
    else:
        # Treat as block 1 x B == A-1 x B 
        SplitLego= [Brick[0]-1,Brick[1]]
    

    # Try to find SplitLego
    CanBeSubstituted, inventory= TryTwo1xB(SplitLego, inventory, Brick,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
    
    if CanBeSubstituted== False:
        return TrySubstituting1xB(SplitLego, inventory, Brick, DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
    else:
        return CanBeSubstituted, inventory
        
        
def TryTwo1xB(SplitLego, inventory, Brick,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates):
    
    # Use ItemsNotUsed from this point onwards to avoid substituting with brick the user doesn't have
    ItemsNotUsed=inventory.Copy()
    
    # if we are successful in finding one 1 x B ...
    result, ItemsNotUsed=SearchAndRemove(SplitLego,ItemsNotUsed,DimensionPartIDTable)
    if result == True:


        # Try to find SplitLego again as we were successful the first time
        result, ItemsNotUsed=SearchAndRemove(SplitLego,ItemsNotUsed,DimensionPartIDTable)
        if result == True:
            # We were successful in finding two 1 x B's
            return True,ItemsNotUsed

        # Otherwise try to find the possible substitutions for SplitLego
        else:
            return TrySecond1xBSubstitution(SplitLego, inventory, ItemsNotUsed, Brick,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
    
    # Not possible to replace 2 x B with at least one 1 x B
    else:
        return False,inventory
    
    
    
def TrySubstituting1xB(SplitLego, inventory,  Brick,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates): 

    # Use ItemsNotUsed from this point onwards to avoid substituting with brick the user doesn't have
    ItemsNotUsed=inventory.Copy()

    #Try to find the possible substitutions for SplitLego
    CanBeSubstituted, ItemsNotUsed= SubstitutionsFor2xB(SplitLego, ItemsNotUsed,  Brick,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)

    # Try to find another substitution for 1 x B  as we were successful the first time
    if CanBeSubstituted== True:
        return TrySecond1xBSubstitution(SplitLego, inventory, ItemsNotUsed,  Brick,DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)

    else:
        return False, inventory
        
    
    
        
def CanBeSubstituted2xB(CanBeSubstituted, ItemsNotUsed, inventory):
    if CanBeSubstituted== True:
        return [True,ItemsNotUsed]
    
    else:
        return False, inventory
    
    
    
def SubstitutionsFor2xB(SplitLego, ItemsNotUsed, Brick, DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates):
    if len(Brick)==3 and UseOfPlates== True:
        CanBeSubstituted, ItemsNotUsed= PlateSubstitutions(SplitLego, -1,ItemsNotUsed, DimensionPartIDTable,ReturnToRoot,1)
    else:
        CanBeSubstituted, ItemsNotUsed= Optimize(SplitLego, -1, ItemsNotUsed,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
    
    return CanBeSubstituted, ItemsNotUsed
    

def TrySecond1xBSubstitution(SplitLego, inventory, ItemsNotUsed, Brick, DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates):
    CanBeSubstituted, ItemsNotUsed= SubstitutionsFor2xB(SplitLego, ItemsNotUsed, Brick, DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
    return CanBeSubstituted2xB(CanBeSubstituted, ItemsNotUsed, inventory)

def Optimize(brick, depth, inventory,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates):

    # Pre-order graph tranversal    

    # the root node (contains the original brick dimensions)
    if depth == -1:
        
        #First try and see if the brick is already in inventory
        result, inventory=SearchAndRemove(brick,inventory,DimensionPartIDTable)
        if result == True:
            return True, inventory
        # Then check to see if we can replace the plate with plates lengthwise (split)
        elif result== False and UseOfPlates ==True and CurrentlySubbingPlates== True:
            depth +=1
            # Try to split the brick in half lengthwise to find subsitutions
            if brick[0]==2:
                result,inventory=Split2xB([brick[0], brick[1],1.3], depth, inventory, DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
                if result == True:
                    return True,inventory     
        # After failing with teh methods above, try to split the brick in half lengthwise to find subsitutions  
        if result== False and CurrentlySubbingPlates== False:
                depth +=1
                if brick[0]==2:
                    result,inventory=Split2xB(brick, depth, inventory, DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)
                    if result == True:
                        return True,inventory

    # When a certain path reaches a point where no further substitutions can be made,
    # we return to the root of the tree
    if depth != 0 and ReturnToRoot == True:
        return
    elif depth == 0 and ReturnToRoot == True: 
        ReturnToRoot = False

        
    # Check (outside of depth -1)
    if CurrentlySubbingPlates == False:
        #First try and see if the brick is already in inventory
        result, inventory=SearchAndRemove(brick,inventory,DimensionPartIDTable)
        if result == True:
            return True, inventory
    
    
    elif CurrentlySubbingPlates == True:
        #First try and see if the plate is already in inventory
        result, inventory=SearchAndRemove([brick[0],brick[1],1.3],inventory,DimensionPartIDTable)
        if result == True:
            return True, inventory
    
        
    #variable initialization
    A,B= brick[0], brick[1]
    depth+=1
    C= D= E= F= 0
    C=F=G=A
    H= B
     
        
    # In case we remove elements in lower depth, but then realize the substitution path is not feasible
    # (Original elements are only removed once we know the path is feasible -> a substituiton is found)
    while H > B/2:
        
        # We remove from the copy instead or original table in case we cannot substitute
        # (so we can use the A x B x 1/3 's later) 
        CopyInventory= inventory.Copy()
        
        # Finds the next permutation
        H,B,D,E= ReduceSize(H,B,D,E) 


        # To prevent repeat substitutes (ie. '1x2 and 1x3', is the same combination as, '1x3 and 1x2') 
        if H <B/2 :
            depth-=1
            return [False,inventory]

        #Get bricks dimensions in the standard matrix format 
        Brick_1= RearrangeDimensions(C,D)
        Brick_2= RearrangeDimensions(E,F)

        
        # Providing that we don't already know whether a brick can be substituted 
        FoundSubstituions,CopyInventory= FindSubtituteParts(depth, Brick_1,Brick_2, CopyInventory ,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)

        
        # We can find substitutions for the brick using Brick_1 and Brick_2 
        if FoundSubstituions== True:
            return [True,CopyInventory]

        # Otherwise move on to the next permutation
        else:
            pass
    
    # Not possible to find substituions for this brick
    return [False,inventory]


def WholeBrickSubstitutions(Brick_1,Brick_2,depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates):

    # Find brick substitutions for the parent brick
    Found_1,inventory= NextTwoSubtitutions(Brick_1, depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
    Found_2,inventory= NextTwoSubtitutions(Brick_2, depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)

    
     # If we find both constituent brick substitutions
    if Found_1==Found_2 and Found_2 == True:
        return True,inventory
    else:
        return False,inventory   
    
    
def NextTwoSubtitutions(Brick, depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates):

    # Search to see if the  brick or plate already exists, and remove it
    if CurrentlySubbingPlates == True:
        Plate= [Brick[0],Brick[1],1.3]
        Found,inventory= SearchAndRemove(Plate,inventory,DimensionPartIDTable)
    else:
        Found,inventory= SearchAndRemove(Brick,inventory,DimensionPartIDTable)
              
    
    # Optimize the next two bricks unless they are  '1 x 1'
    if  Brick != [1,1] and Found==False:  

        # For bricks ... check if we can replace a 2 x B with two 1 x B's 
        if CurrentlySubbingPlates == False and Brick[0]==2:
                Found,inventory  = Split2xB(Brick, depth, inventory, DimensionPartIDTable,UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)

        # For plates ...  check if we can replace a 2 x B x 1/3 with two 1 x B x 1/3's   
        elif CurrentlySubbingPlates == True and Brick[0]==2:
                Found,inventory  = Split2xB([Brick[0],Brick[1],1.3], depth, inventory,DimensionPartIDTable, UseOfPlates,  ReturnToRoot, CurrentlySubbingPlates)

        # If we cannot split in two, optimize normally
        if Found == False: 
                Found,inventory= Optimize(Brick,depth,inventory, DimensionPartIDTable,UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)

                 
        # Finaly, only if the part is a whole size brick should we discard its feasibility and return to the root node
        if Found== False and CurrentlySubbingPlates== False:
            ReturnToRoot= True 
            
    # Special case for 1 x 1's - they can only be substiuted by three 1 x 1 x 1/3's     
    if Brick== [1,1] and Found==False and UseOfPlates ==True and CurrentlySubbingPlates == False:
        Found,inventory= Substitute1x1(Brick, inventory,DimensionPartIDTable)
        
    # Impossible to substitute a 1 x 1 x 1/3
    if Brick== [1,1] and Found==False and CurrentlySubbingPlates == True:
        Found= False
        

    return [Found,inventory]



def FindSubtituteParts(depth, Brick_1,Brick_2, inventory , DimensionPartIDTable,UseOfPlates, ReturnToRoot,CurrentlySubbingPlates):

    if UseOfPlates== False and CurrentlySubbingPlates==False: 

        # Normal whole brick substitution
        return WholeBrickSubstitutions(Brick_1,Brick_2,depth,inventory, DimensionPartIDTable,UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
    
    else:
        
        # We have to first see if our brick can be replaced by layers of plates before splitting it up
        if CurrentlySubbingPlates== False:
            
            CurrentlySubbingPlates= True
            
            # First check to see if our current bricks can be substituted by 3 layers of plates
            Found_1,inventory= FindTheLayers(Brick_1, depth,inventory,DimensionPartIDTable, ReturnToRoot )
            Found_2,inventory= FindTheLayers(Brick_2, depth,inventory,DimensionPartIDTable, ReturnToRoot )

            
            # if both can be subbed with plates
            if Found_1==Found_2 and Found_2 == True:
                return True,inventory
            
            CurrentlySubbingPlates= False
            # Now try to optimize the brick that cannot be subbed by plates using whole bricks
            if Found_1== False and Found_2 == True:
                Found_1,inventory= NextTwoSubtitutions(Brick_1, depth,inventory, DimensionPartIDTable,UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
            elif Found_1== True and Found_2 == False:
                Found_2,inventory= NextTwoSubtitutions(Brick_2, depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
            elif Found_1==Found_2 and Found_2 == False:
                # If we cannot substitute either with plates,  try whole brick substitutions for both
                return WholeBrickSubstitutions(Brick_1,Brick_2,depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
            
            # If we have substituted both bricks sucessfuly 
            if Found_1==Found_2 and Found_2 == True:
                return True, inventory
            else:
                return False, inventory
   
        else:
            
            #If we are subbing plates, we need to essentialy act like we are substituting a full-size brick 'n' numbers of times
            # Hence we reuse the algorithim, only adding a third dimensions conceptually
            Found_1,inventory= NextTwoSubtitutions(Brick_1, depth,inventory, DimensionPartIDTable,UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
            Found_2,inventory= NextTwoSubtitutions(Brick_2, depth,inventory,DimensionPartIDTable, UseOfPlates, ReturnToRoot,CurrentlySubbingPlates)
            
            # If we have substituted both plates sucessfuly 
            if Found_1==Found_2 and Found_2 == True:
                return True,inventory
            else:
                return False,inventory
            

def PlateSubstitutions(Brick, depth,inventory, DimensionPartIDTable,ReturnToRoot,ExtraLayersNeeded):
    #First try and see if the brick is already in inventory
    result, inventory=SearchAndRemove([Brick[0],Brick[1],1.3],inventory,DimensionPartIDTable)
    if result == True:
        return True, inventory
    
    count=0

    # We remove from the copy instead or original array in case we cannot substitute 
    # (so we can use the plates later)
    CopyInventory= inventory.Copy()
        
    # This will keep track of whether one brick can be replaced by three layers of plates
    PlateSubPossible= True

    # Loop until we cannot create the nth layer of plates
    while count < ExtraLayersNeeded and PlateSubPossible == True: 
        
        PlateSubPossible,CopyInventory= Optimize(Brick,depth,CopyInventory, DimensionPartIDTable,True, ReturnToRoot, True)
        count +=1

    # If we are able to substitute with 'n' layers of plates    
    if  count== ExtraLayersNeeded and PlateSubPossible== True:
        return [True,CopyInventory]
    else: 
        return [False,inventory]


def FindTheLayers(Brick, depth,inventory,DimensionPartIDTable, ReturnToRoot):
    #First try and see if the brick is already in inventory
    result, inventory=SearchAndRemove(Brick,inventory,DimensionPartIDTable)
    if result == True:
        return True, inventory
    
    # We remove from the copy instead or original table in case we cannot substitute
    # (so we can use the A x B x 1/3 's later) 
    CopyInventory= inventory.Copy()
    # Start by assuming all three layers of plates are needed
    LayersNeeded=3
    CanBeSubstituted= False
    
    # Will see how many layers of plates are actually needed
    for i in range(0,3):
        
         # Search and remove a plate of A x B x 1/3 ...
        Result, CopyInventory=SearchAndRemove([Brick[0],Brick[1],1.3],CopyInventory,DimensionPartIDTable)
        if Result == True:
            LayersNeeded -=1
        
        # ... or search and remove two plates of 1 x B x 1/3 
        else:
            if Brick[0]==2:
                # Will individualy substitute both plates of 1 x B x 1/3
                Result, CopyInventory1= Split2xB([Brick[0],Brick[1],1.3], depth, CopyInventory,DimensionPartIDTable, True,  ReturnToRoot, True)
                if Result== True:
                    CopyInventory= CopyInventory1.Copy()
                    LayersNeeded -=1          
    

    if LayersNeeded==0:
        inventory= CopyInventory.Copy()
        return [True,inventory]
    
    #Now try to substitute the extra layers
   # if Brick != [1,1]:
    CanBeSubstituted,CopyInventory= PlateSubstitutions(Brick, depth,CopyInventory, DimensionPartIDTable, ReturnToRoot,LayersNeeded)
    #else:
      #  CanBeSubstituted,CopyInventory= Substitute1x1(Brick, CopyInventory,DimensionPartIDTable)

    if CanBeSubstituted== True:
        
        #If we can substitute, actually remove these elements from the parent hash table
        inventory= CopyInventory.Copy()
        return [True,inventory]
    
    else:
        return [False,inventory]    


def SearchInventory(brick, inventory,DimensionPartIDTable):
    # Convert matrix to readable dimensions
    brick= DimensionPartIDTable.MatrixToDimensions(brick)
    
    # Find a part ID with the same dimensions
    BrickNode= DimensionPartIDTable.Search(brick)
    
    
    # While we have one or more parts in our inventory with the desired dimensions
    while BrickNode != None:
        
        InvNode= inventory.SearchForPartsInInventory(BrickNode.value)
       
        # check if we have at least one of this part
        if InvNode != None:
            if int(InvNode.value) > 0:
                return True,InvNode
        
        # otherwise move onto the next part with same dimensions  
        BrickNode= BrickNode.next
        
    return False, None



def SearchAndRemove(brick,inventory,DimensionPartIDTable):
    

    # First see if the part is actually in inventory
    BrickPossesed, Node= SearchInventory(brick, inventory,DimensionPartIDTable)
    
    # Then reduce the stored quantity of the brick by 1
    if BrickPossesed== True:
        inventory,___ = inventory.ChangeQuantity(Node.key,-1)
        return True, inventory
    
    # Unless the user does not possess the brick
    else:
        return False, inventory



    

    

    
    

        



      
    
    