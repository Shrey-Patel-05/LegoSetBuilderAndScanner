import pandas as pd

# Implementation of linked list
class ListNode:
    
    def __init__(self,key,value):
        self.key= key
        self.value= value
        self.next= None

# Implementation of hash table
class Hash_Table:
    
    def __init__(self, capacity):
        self.capacity= capacity
        self.size=0
        self.table= [None]* capacity
   
    def GetTable(self):
        return self.table
    
    def GetNode(self, key):
        
        # Will return an index
        HashedValue= self.Hash(key)
        # Will return the first element in list- if it exists
        Node= self.table[HashedValue]
        return Node
        
    
    def Hash(self,key):
        # hashes the key and finds the index through a mod operation with the table's capacity
        return hash(key) % self.capacity
    
    
    def Insert(self,key,value):
        Node= self.GetNode(key)
    
        # If there is no list at that index of the table...
        if Node == None:
            
            # Create a linked list with the current key/value combination as the head
            self.table[self.Hash(key)]= ListNode(key,value)
            self.size+=1
            return
        
        else:
            
            # Will iterate to the end of the existing linked list
            while Node.next != None:
                Node= Node.next           
                
            # Create a new element of the linked list
            Node.next= ListNode(key,value)
            self.size+=1
        

      
        
    def Copy(self,copy_table):
        # initialize a new table with the same capacity 
        
        for Node in self.table:  
            #if a node exists..
            while Node != None:
                
                # Insert key-value pairs into the new table
                copy_table.Insert(Node.key, Node.value)
                
                # Move onto the next node
                Node = Node.next
                
        # Once all data has been copied, return the table
        return copy_table
    
    def GetListOfAllNodes(self):
        ListOfAllNodes=[]
        for Node in self.table:
            #if a node exists..
            while Node != None:
                ListOfAllNodes.append([Node.key,Node.value])
                # Move onto the next node
                Node = Node.next

        # Once all data has been copied, return the table
        return ListOfAllNodes
    
    def Remove(self,key):
        
        location = self.Hash(key) 

        previousNode = None
        currentNode = self.table[location] 

        # Iterate thorugh the linked list (if it exists)
        while currentNode != None: 
            
            if currentNode.key == key: 
                # If there is a previous node, update its 'next' pointer
                if previousNode != None: 
                    previousNode.next = currentNode.next
                else: 
                    # Otherwise update the node at table[location] directly
                    self.table[location] = currentNode.next
                self.size -= 1
                return
            
                # Move to the next node
            previousNode = currentNode 
            currentNode = currentNode.next
        
        # Return if not in table
        return 

class Inventory(Hash_Table):
    
    def __init__(self, capacity):
        Hash_Table.__init__(self,capacity)
    
    def Copy(self):
        copy_table= Inventory(self.capacity)
        # Use the rest of the parent class Copy method
        return super().Copy(copy_table)
    
        
    def SearchForPartsInInventory(self, key):
        
    
        Node= self.GetNode(key)
        
        # Will iterate to the end of the list. 
        # If key not found, return '0'
        while Node != None:
            
            
            # If not item, go to next node
            if Node.key != key:
                Node= Node.next

            # If found, return value
            elif Node.key== key:
                return Node
                
        return None
    
    
    def QuantityCheck(self, key, PartsRequired): 
        # Find the node
        Node= self.SearchForPartsInInventory(key)
        if Node != None:
            # Subtract parts required from how much the user has 
            quantity= str(int(Node.value)-int(PartsRequired))
            return quantity
        else:
            return 'NO_PART'
            
        
    def ChangeQuantity(self, key, amount):
        
        Node= self.GetNode(key)
        
        # Will iterate to the end of the list. 
        # If key not found, return '0'
        while Node != None:
            
            
            # If not item, go to next node
            if Node.key != key:
                Node= Node.next

            # If found, return value
            elif Node.key== key:
                Node.value = str(int(Node.value)+amount)
                return self, Node.value
        return self,Node.value       


# Will store dimensions and PartID, with either being used as the key
class Dimensions(Hash_Table):
    
    def __init__(self, capacity):
        Hash_Table.__init__(self,capacity)
          
    
    def DimensionsToMatrix(self,dimensions):

        # The dimensions of the matrix are revealed by the number of x's in the string
        dimensionLength= dimensions.count('x') +1

        # Create a array to hold matrix dimensions
        returnDimensionsArray=[None]*dimensionLength

        # Find first matrix dimension
        returnDimensionsArray[0]= int(dimensions[:dimensions.index('x')])
        dimensions= dimensions[(dimensions.index('x')+1):]

        # Find second (and possibly third) matrix dimension(s)
        if dimensionLength ==2:
            returnDimensionsArray[1]= int(dimensions)
            return returnDimensionsArray

        elif dimensionLength ==3:

            returnDimensionsArray[1]= int(dimensions[:dimensions.index('x')])
            dimensions= dimensions[(dimensions.index('x')+1):]

            # We store a plate as size 1.3 for readability
            if dimensions == ' 1/3':
                returnDimensionsArray[2]= 1.3
            elif dimensions == ' 2/3':
                returnDimensionsArray[2]= 2.3
            else:
                returnDimensionsArray[2]= int(dimensions)

            return returnDimensionsArray

        # We cannot deal with more than 3 dimensions
        else:
            return [0,0]
    
    
    def MatrixToDimensions(self,dimensions):
        if len(dimensions)== 2:
            return str(dimensions[0])+ ' x '+ str(dimensions[1])
        
        elif len(dimensions)== 3:
            if dimensions[2] == 1.3:
                dimensionThree= '1/3'
            elif dimensions[2] == 2.3:
                dimensionThree= '2/3'
            else:
                dimensionThree= str(dimensions[2])
            return str(dimensions[0])+ ' x '+ str(dimensions[1])+' x '+ dimensionThree
                

        
    def Search(self, key):
        
        Node= self.GetNode(key)
        
        # Will iterate to the end of the list. 
        # If key not found, return '0'
        while Node != None:
            
            
            # If not item, go to next node
            if Node.key != key:
                Node= Node.next

            # If found, return value
            elif Node.key== key:
                return Node#.value#self.DimensionsToMatrix(Node.value)
                
        return None
        
   
           
class Stack():
    
    def __init__(self,capacity):
        self.stack= [None]* capacity
        self.pointer= 0
        
    def Peek(self):
        # returns the last item added to the stack
        return self.stack[self.pointer]
    
    def Pop(self):
        self.stack[self.pointer]= None
        self.pointer-=1
        # Ensures we do not go out of index
        if self.pointer<0:
            self.pointer=0
            
    def Push(self, value):
        self.pointer+=1
        # Ensures we do not go out of index
        if self.pointer == len(self.stack):
            self.pointer-=1
            pass
        else:
            # Set value
            self.stack[self.pointer]= value

        

class Sets:
    
    def __init__(self, Name, SetURL):
        self.Name= Name
        self.SetURL= SetURL
        self.PartsPossessed= []
        self.PartsRequired= []
        self.Total_Needed=0
        self.PValue= 0
        self.Cost=''
    
    def SetTotal(self):
        runningTotal=0
        # Add all the quantities of parts still needed 
        for parts in self.PartsRequired:
            runningTotal+=int(parts[1])
        self.Total_Needed= runningTotal
        

    def SetCost(self):
        # Multiply total by average price-per-part ($0.19)
        cost= str(round(self.Total_Needed * 0.19,2))

        # Extend to two decimal places
        while len(cost[cost.index('.')+1:]) <2:
            cost+='0'

        self.Cost= "$"+cost

    def SetSearchingInventory(self, Quantity, PartID, inventory):

        # Will store either 'NO_PART' or the quantity of parts left over 
        ResultOfSearch= inventory.QuantityCheck(PartID, Quantity)
        
        # The user needs full quantity of the part (they have none) 
        if ResultOfSearch == 'NO_PART':
            
            self.PartsRequired.append([PartID,Quantity])
            

        # If the user does not have enough parts
        elif int(ResultOfSearch)< 0 :
            
            # As ResultOfSearch would be negative in this case,
            # The absolute value represents the extra parts required
            self.PartsRequired.append([PartID,str(abs(int(ResultOfSearch)))])
            
            # User already has some of this part - but not enough. str(int(Quantity)+int(ResultOfSearch))
            self.PartsPossessed.append([PartID,str(int(Quantity)+int(ResultOfSearch))])


        elif int(ResultOfSearch)>= 0 :
            # The user has both the type of brick and enough of it    
            self.PartsPossessed.append([PartID,str(Quantity)])
    
   
# new!!!!!

class MOC_Sets(Sets):
    
    def __init__(self, Name, SetURL):
        Sets.__init__(self, Name, SetURL)



class Official_Sets(Sets):
    
    def __init__(self, Name, SetURL):
        Sets.__init__(self, Name, SetURL)
        self.Name= self.ExtractSetName()
        self.SetID= self.ExtractSetID()
    
    def ExtractSetName(self):
        try: 
            # First 29 charcters are same for all URLs. Find the fourth and fifth instance of '/'
            URL= self.SetURL
            
            start_of_set_name=URL[30+URL[29:].index('/'):]
            end_of_set_name=start_of_set_name.index('/')

            # Then slice that section out of URL and replace dashes with spaces
            set_name_unclean= start_of_set_name[:end_of_set_name]
            set_name= set_name_unclean.replace('-',' ')
            
            return set_name
        except:
            return self.Name

    def ExtractSetID(self):
        
        # Locate where the setID will begin
        loc1= 6+ self.SetURL.find('/sets/')
        # The next '/' after '/sets' is where the setID ends
        loc2= loc1 + self.SetURL[loc1:].find('/')
        # The setID is between the two locations
        return self.SetURL[loc1:loc2]

                    

#### NOT PART OF ANY CLASS ########################################################

def SecondIterations(placer, sub_array, child_aray, ArrayPointer):
    
    # While elements in this child aray have not been place in parent array...
    while ArrayPointer < len(child_aray):
        
        # Place the curent element in the parent array... 
        sub_array[placer]= child_aray[ArrayPointer] 
        
        # And increment pointers
        ArrayPointer +=1
        placer+=1
        
def Iterations(LP, RP, Placer,sub_array, Left_sub_array, Right_sub_array ):
    
    while LP < len(Left_sub_array) and RP < len(Right_sub_array):

        # If the current element  of Left_sub_array is less than 
        # the current element of Right_sub_array...
        if Left_sub_array[LP].PValue < Right_sub_array[RP].PValue:

            # Place the the current element of Left_sub_array into next location in parent array
            sub_array[Placer]= Left_sub_array[LP] 
            LP +=1

        # If the current element of Righft_sub_array is less than/equal to 
        # the current element of Left_sub_array...
        else:
            sub_array[Placer]= Right_sub_array[RP] 
            RP +=1

        Placer+=1
        # The follwoing two if statements deal with the remaning elements in the two smaller arrays
        if LP < len(Left_sub_array):
            SecondIterations(Placer, sub_array, Left_sub_array, LP)

        if RP < len(Right_sub_array):
            SecondIterations(Placer, sub_array, Right_sub_array, RP)

def MergeSort(sub_array):
    
    if len(sub_array) >1:
        
        # Stores the index of the middle of the array
        MidPoint= len(sub_array)//2

        # Will recursively iterate until we have sub arrays of size of 1
        Left_sub_array= sub_array[:MidPoint]
        Right_sub_array= sub_array[MidPoint:]
        MergeSort(Left_sub_array)
        MergeSort(Right_sub_array)
        

        # Pointer for Left_sub_array
        LP=0
        # Pointer for Right_sub_array
        RP=0
        # Current element in parent array
        Placer=0


        Iterations(LP, RP, Placer, sub_array, Left_sub_array, Right_sub_array )

        return sub_array  

def CalculatePValues(Set):
    
    partsPossessed=0
    partsRequired=0
    
    # For all the possesed parts...
    for i in range(0,len(Set.PartsPossessed)):
        partsPossessed+= int(Set.PartsPossessed[i][1]) 
        
    # For all the required parts...
    for i in range(0,len(Set.PartsRequired)): 
        partsRequired+= int(Set.PartsRequired[i][1]) 
        
    total= partsPossessed + partsRequired
    
    Set.PValue= partsRequired / total
    

def GoThroughParts(quantity, part, SetList,MOC_or_OFFICIAL, index, hashtable):
    
    # Only the set URLs would have a length greater than 5
    if len(part)>5:
        # Increment the index and add a new set
        index+=1
        if MOC_or_OFFICIAL== "MOC":
            SetList.append(MOC_Sets(quantity, part))
        elif MOC_or_OFFICIAL== "OFFICIAL": 
            SetList.append(Official_Sets(quantity, part))   
        return index
    
    else:
        # The current set is at position specified by index
        Set= SetList[index]
        # Will search the hash table for the part
        Set.SetSearchingInventory(quantity, part,hashtable)
        return

def SearchForPartsInSets(df,MOC_or_OFFICIAL):
    SetList=[]
    index=-1
    # Apply the function to the dataframe to add sets and search for parts
    df.apply(lambda x: GoThroughParts(x['Quantities'],x['PartID'],SetList,MOC_or_OFFICIAL, index, UserInventory),axis=1)
    # Find priority values once all sets have been accounted for 
    for Set in SetList:
        CalculatePValues(Set)
    return SetList

def GetSubstiutionList(InventoryReturned, OriginalInventory,PartIDDimensionTable):
    returnlist= []
    # The actual hash table
    table= InventoryReturned.GetTable()
    
    for NewNode in table: 
        #if a node exists..
        while NewNode != None:
            # Get the corresponding node in the original inventory
            OriginalNode= OriginalInventory.SearchForPartsInInventory(NewNode.key)
            
            if OriginalNode != None:
                #If there is a difference in values, this means the part has been used in substitution
                if NewNode.value != OriginalNode.value: 
                    dimension_return = PartIDDimensionTable.Search(NewNode.key).value if PartIDDimensionTable.Search(NewNode.key) is not None else 'N/A'
                    if int(OriginalNode.value)-int(NewNode.value) >0: 
                        returnlist.append([NewNode.key,dimension_return,str(int(OriginalNode.value)-int(NewNode.value))])

            NewNode = NewNode.next
   
    return returnlist  

def LoadInventory():
    df = pd.read_csv("CSV's/InventoryCSV.csv")
    for i in range(0,len(df)):
        UserInventory.Insert(str(df.iloc[i]["PartID"]),str(df.iloc[i]["Quantities"]))

def SaveInventory():
    # Get the contents of the inventory
    parts= UserInventory.GetListOfAllNodes()
    data= {'Quantities': [arr[1] for arr in parts],'PartID': [arr[0] for arr in parts]}
    # Add this data to the existing dataframe
    df = pd.DataFrame(data)
    # Save the updated inventory
    df.to_csv("CSV's/InventoryCSV.csv",index=False, encoding='utf-8')


################################################################################################################################################
###################################################### DECLARE VARIABLES #######################################################################
################################################################################################################################################
0
# Flags are start,capturing, take_capture
scan_flags= [False,False,False]
output_width= 600
output_height= 400
current_image=1
Use_Plates= True 
global image_to_save_data
vid= None


# Load relevant csv files    
MOCdf= pd.read_csv("CSV's/RebrickableMOCClean.csv")
OFFICIALdf= pd.read_csv("CSV's/OfficialSetsClean.csv")
DIMENSIONSdf=pd.read_csv("CSV's/PartDataClean.csv")


# There are 3700 different lego pieces available
UserInventory= Inventory(4000)


# Creates a hash table of length 1.3 * actual number of elements
DimensionTableLength= int(float(DIMENSIONSdf.shape[0])*2)
DimensionPartIDTable= Dimensions(DimensionTableLength)
PartIDDimensionTable= Dimensions(DimensionTableLength)

# User should not be able to add 999 parts in one go
InventoryStack= Stack(999)

# Fill in dimension tables
for i in range(0,DIMENSIONSdf.shape[0]):
    DimensionPartIDTable.Insert(DIMENSIONSdf['dimensions'][i], DIMENSIONSdf['part_num'][i])
    PartIDDimensionTable.Insert(DIMENSIONSdf['part_num'][i], DIMENSIONSdf['dimensions'][i])