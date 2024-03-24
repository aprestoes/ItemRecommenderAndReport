import math
import time

DEBUG = False

def debug(message):
    if DEBUG:
        print(message)

def userIndexToUsername(userIndex, usernames):
    return usernames[userIndex]

def usernameToUserIndex(username, usernames):
    return usernames.index(username)

def itemIndexToName(itemIndex, itemNames):
    return itemNames[itemIndex]

""" PREPARING LABS FOR ASSIGNMENT
Changes:
    1. Separate user similarities, item similarities
    2. Create neighbours function
        - Separate user-based and item-based
        - After neighbours are found (regardless of if they are user based or item based), sort by top-K or threshold-based.
            -> For the top-K section, add option to use absolute similarity
    3. Implement timers in important functions to keep track of execution time
    
"""

def readMatrixFile(txtLocation):
    # Read first file
    f = open(txtLocation, "r")

    debug("Reading .txt file")

    # Read and populate the sizes from the first line
    numUsers, numItems = [int(i) for i in f.readline().split()]

    # Read and populate the usernames from the second line
    usernames = []
    for username in f.readline().split():
        usernames.append(username)

    # Read and populate the item names from the third line
    itemNames = []
    for item in f.readline().split():
        itemNames.append(item)

    # Read and populate the 2D array for the current reviews
    # ratings = [2][2]
    ratings = []
    # Element contains the index of line that has an unread item. 
    #   That way you can access the line by just looping through objects                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   
    for i in range(numUsers):
        lineRatings = f.readline().split()
        line = []
        for rating in lineRatings:
            line.append(float(rating))
        ratings.append(line)
        #unreviewed.append(unreviewedOfLine)
    debug("Finished reading file")
    return ratings, numUsers, numItems, usernames

def calculateAverageRatings(ratings, numUsers, numItems):
    # Calculate the average for each user
    averageUserRatings = []
    for i in range(numUsers):
        numerator = 0
        denominator = numItems
        for j in range(numItems):
            if ratings[i][j] == 0:
                denominator -= 1
            else:
                numerator += ratings[i][j] 
        
        averageUserRatings.append(float(numerator / denominator))
    debug(f"Average user ratings: {averageUserRatings}")
    return averageUserRatings

""" ###
    #   SIMILARITIES
    ###
""" 
def calculateItemSimilarity(itemAIndex, itemBIndex, ratings, averageUserRatings, numUsers):
    numerator = 0
    denomA = 0
    denomB = 0

    for userIndex in range(numUsers):
        ratingA = ratings[userIndex][itemAIndex]
        ratingB = ratings[userIndex][itemBIndex]
        if (ratingA != 0 and ratingB != 0):
            ratingA -= averageUserRatings[userIndex]
            ratingB -= averageUserRatings[userIndex]
            numerator += ratingA * ratingB
            denomA += math.pow(ratingA, 2)
            denomB += math.pow(ratingB, 2)
        if (denomA == 0 or denomB == 0):
            #return averageUserRatings[userIndex]
            debug("Invalid item similarities")
            #return 0
    denomA = math.sqrt(denomA)
    denomB = math.sqrt(denomB)

    if (denomA == 0 or denomB == 0):
        return 0
    else:
        return numerator / (denomA * denomB)

def calculateUserSimilarity(userAIndex, userBIndex, ratings, averageUserRatings, numItems):
    numerator = 0
    denomA = 0
    denomB = 0

    for itemIndex in range(numItems):
        if (ratings[userAIndex][itemIndex] != 0) and (ratings[userBIndex][itemIndex] != 0):
            numerator += ((ratings[userAIndex][itemIndex] - averageUserRatings[userAIndex]) 
                                * (ratings[userBIndex][itemIndex] - averageUserRatings[userBIndex]))
            denomA += math.pow((ratings[userAIndex][itemIndex] - averageUserRatings[userAIndex]), 2)
            denomB += math.pow((ratings[userBIndex][itemIndex] - averageUserRatings[userBIndex]), 2)

    if (denomA == 0 or denomB == 0):
        return 0
    else:
        finalAnswer = numerator / (math.sqrt(denomA) * math.sqrt(denomB))
        debug(f"Similarity between {userAIndex} and {userBIndex}: {finalAnswer}")
        return finalAnswer

def calculateAllSimilarities(isUserBased, ratings, averageUserRatings, numUsers, numItems):
    #similarities = [[0 for item in range(numItems)] for user in range(numUsers)]
    # similiarites[a, b] is the similarity between a and b, etc.
    debug(f"Calculating all similarities isUserBased: {isUserBased}")
    if (isUserBased):
        similarities = [[0 for user in range(numUsers)] for user in range(numUsers)]
        for i in range(numUsers):
            for j in range(i + 1, numUsers):
                similarities[i][j] = calculateUserSimilarity(i, j, ratings, averageUserRatings, numUsers)
                similarities[j][i] = similarities[i][j]
    else:
        similarities = [[0 for item in range(numItems)] for item in range(numItems)]
        for i in range(numItems):
            for j in range(i + 1, numItems):
                similarities[i][j] = calculateItemSimilarity(i, j, ratings, averageUserRatings, numUsers)
                similarities[j][i] = similarities[i][j]
    debug(f"Finished calculating all similarities: {similarities}")
    return similarities

""" ###
    #   NEIGHBOURS
    ###
"""
def getNeighbours(isUserBased, similarities, numItems, numUsers, numNeighbours=None, thresh=None, negCorrelations=False):
    neighbours = []

    debug(f"Getting neighbours, isUserBased: {isUserBased}")
    # Changed to make it more general
    for firstIndex in range(numUsers if isUserBased else numItems):
        currentNeighbours = [(abs(similarities[firstIndex][secondIndex]) if negCorrelations else similarities[firstIndex][secondIndex], secondIndex) 
                                for secondIndex in range(numUsers if isUserBased else numItems) 
                                if (secondIndex != firstIndex) and (negCorrelations or similarities[firstIndex][secondIndex] > 0)]
        currentNeighbours.sort(key=lambda var: var[0], reverse=True)

        if (numNeighbours is not None):
            #debug(f"Using numNeighbours")
            slicedNeighbours =  currentNeighbours[:numNeighbours]
            neighbours.append(slicedNeighbours)
        elif (thresh is not None): # If similarity is higher than the threshold value
            #debug("Using threshold")
            neighbours.append([neighbour for neighbour in currentNeighbours if neighbour[0] > thresh])
        else:
            #debug("Getting default number of neighbours")
            neighbours.append(currentNeighbours)
    
    debug(f"Returning neighbours {neighbours}")
    return neighbours

# A single prediction
def calculatePrediction(isUserBased, userIndex, itemIndex, ratings, averageUserRatings, neighbours, numUsers, numItems):
    numerator = 0
    denominator = 0
    validNeighbours = 0

    #debug(f"UserBased: {isUserBased} Predicting for user/item: {userIndex if isUserBased else itemIndex}")
    #debug(f"Neighbours: {neighbours[userIndex if isUserBased else itemIndex]}")

    for (neighbourSim, neighbourIndex) in neighbours[userIndex if isUserBased else itemIndex]:
        if (isUserBased):
            if (ratings[neighbourIndex][itemIndex] != 0):
                numerator += (neighbourSim * (ratings[neighbourIndex][itemIndex] - averageUserRatings[neighbourIndex]))
                denominator += neighbourSim
                #debug(f"Numerator: {numerator} Denominator: {denominator}")
                validNeighbours += 1
        else:
            if (ratings[userIndex][neighbourIndex] != 0):
                numerator += neighbourSim * ratings[userIndex][neighbourIndex]
                denominator += neighbourSim
                validNeighbours += 1

    if (validNeighbours == 0):
        debug(f"No valid neighbours for {userIndex}, {itemIndex}")
        return round(averageUserRatings[userIndex], 2)

    if (denominator == 0):
        return round(averageUserRatings[userIndex], 2)
        #return averageUserRatings[userIndex]
    else:
        if (isUserBased):
            prediction = averageUserRatings[userIndex] + (numerator / denominator)
            debug(f"Prediction: {prediction} = {averageUserRatings[userIndex]} + ({numerator} / {denominator})")
            return round(prediction, 2)
        else:
            return round(numerator / denominator, 2)
        #return numerator / denominator

# All predictions
def calculatePredictions(isUserBased, neighbours, ratings, averageUserRatings, similarities, numUsers, numItems):
    #output = np.copy(ratings)
    output = [row[:] for row in ratings]

    #neighbours = []
    debug("Calculating predictions")
    for userIndex in range(numUsers):
        for itemIndex in range(numItems):
            if (ratings[userIndex][itemIndex] == 0):
                debug("Calculating prediction for (user, item): %s %s" %(userIndex, itemIndex))

                prediction = calculatePrediction(isUserBased, userIndex, itemIndex, ratings, averageUserRatings, neighbours, numUsers, numItems)
                output[userIndex][itemIndex] = prediction

    debug("Finished calculating predictions")
    return output

# Leave one out cross validation
def calculateMAE(isUserBased, neighbours, ratings, averageUserRatings, numUsers, numItems):
    numerator = 0
    denominator = 0

    debug("Initializing MAE calculation")
    for userIndex in range(numUsers):
        for itemIndex in range(numItems):
            if (ratings[userIndex][itemIndex] != 0):
                origRating = ratings[userIndex][itemIndex]
                ratings[userIndex][itemIndex] = 0

                predictedRating = calculatePrediction(isUserBased, userIndex, itemIndex, ratings, averageUserRatings, neighbours, numUsers, numItems)

                ratings[userIndex][itemIndex] = origRating
                
                if predictedRating is not None:
                    numerator += abs(origRating - predictedRating)
                    denominator += 1

    debug("Finished MAE calculation")
    if (denominator == 0):
        return 0
    else:
        return numerator / denominator

def printPredictions(txtlocation, isUserBased, numNeighbours = None, thresh = None, negCorrelations = False):
    startTime = time.process_time()

    ratings, numUsers, numItems, usernames = readMatrixFile(txtlocation)
    averageUserRatings = calculateAverageRatings(ratings, numUsers, numItems)
    similarities = calculateAllSimilarities(isUserBased, ratings, averageUserRatings, numUsers, numItems)
    neighbours = getNeighbours(isUserBased, similarities, numItems, numUsers, numNeighbours=numNeighbours, thresh=thresh, negCorrelations=negCorrelations)
    output = calculatePredictions(isUserBased, neighbours, ratings, averageUserRatings, similarities, numUsers, numItems)
    mae = calculateMAE(isUserBased, neighbours, ratings, averageUserRatings, numUsers, numItems)

    endTime = time.process_time()
    runtime = endTime - startTime

    """print("\n==={}===".format(txtlocation))
    print(f"\n==={txtlocation} Runtime: {runtime}===")
    print("Original")
    for i in range(numUsers):
        for j in range(numItems):
            print(ratings[i][j], end=" ")
        print()

    print("\nOutput")
    for i in range(numUsers):
        for j in range(numItems):
            print(output[i][j], end=" ")
        print()

    print("\n===MAE=%s===" % mae)"""
    print(f"===MAE={mae} Runtime={runtime}===\n")
    #options = {"isUserBased": isUserBased, "numNeighbours": numNeighbours, "thresh": thresh, "negCorrelations": negCorrelations}
    options = [isUserBased, numNeighbours, thresh, negCorrelations]
    return mae, runtime, options

# Options parameters are lists that will be looped through to try each combination
def startTests(txtlocation, isUserBasedOptions, neighbourNumOptions, threshOptions, negCorrelationsOptions):
    #totalNumTests = len(isUserBasedOptions) * len(neighbourNumOptions) * len(threshOptions) * len(negCorrelationsOptions) # Use product rule to get total num of permutations
    #numNeighbourThreshCases = len(isUserBasedOptions) * 1 * 1 * len(negCorrelationsOptions) # Subtract permutations where thresh and numNeighbours are both None
    #totalNumTests -= numNeighbourThreshCases

    counter = 1

    logFile = open("logs.txt", "w")
    testResults = []
    for isUserBased in isUserBasedOptions:
        for numNeighbours in neighbourNumOptions:
            for thresh in threshOptions:
                if (numNeighbours is not None and thresh is not None):
                    continue # Skip iteration, as thresh and top-K cannot both be used
                for negCorrelations in negCorrelationsOptions:
                    #print(f"===({counter}/{totalNumTests}) Testing with userBased={isUserBased}, numNeighbours={numNeighbours}, thresh={thresh}, negCorrelations={negCorrelations}===")
                    print(f"===({counter}) Testing with userBased={isUserBased}, numNeighbours={numNeighbours}, thresh={thresh}, negCorrelations={negCorrelations}===")
                    mae, runtime, options = printPredictions(txtlocation, isUserBased, numNeighbours, thresh, negCorrelations)
                    testResults.append((mae, runtime, options))
                    logFile.write(f"({counter}) MAE: {mae}, Runtime: {runtime}, isUserBased: {options[0]}, numNeighbours: {options[1]}, thresh: {options[2]}, negCorrelations: {options[3]}")
                    counter += 1
    logFile.close()
    resultsByMAE = sorted(testResults, key=lambda var: var[0], reverse=True)
    resultsByRT = sorted(testResults, key=lambda var: var[1])
    resultsByBoth = sorted(testResults, key=lambda var: (-var[0], var[1]))

    print("\n===Results by MAE===")
    resultsMAEFile = open("resultsByMae.txt", "w")
    for resultIndex in range(len(resultsByMAE)):
        result = resultsByMAE[resultIndex]
        print(result)
        resultsMAEFile.write(f"{resultIndex}. MAE: {result[0]}, Runtime: {result[1]}, isUserBased: {result[2][0]}, numNeighbours: {result[2][1]}, thresh: {result[2][2]}, negCorrelations: {result[2][3]}\n")
    resultsMAEFile.close()
    
    print("\n===Results by Runtime===")
    resultsRTFile = open("resultsByRT.txt", "w")
    for resultIndex in range(len(resultsByRT)):
        result = resultsByRT[resultIndex]
        print(result)
        resultsRTFile.write(f"{resultIndex}. MAE: {result[0]}, Runtime: {result[1]}, isUserBased: {result[2][0]}, numNeighbours: {result[2][1]}, thresh: {result[2][2]}, negCorrelations: {result[2][3]}\n")
    resultsRTFile.close()

    # Sorted by runtime and MAE
    print("\n===Best Results===")
    bestResultsFile = open("bestResults.txt", "w")
    for resultIndex in range(len(resultsByBoth)):
        result = resultsByMAE[resultIndex]
        print(result)
        bestResultsFile.write(f"{resultIndex}. MAE: {result[0]}, Runtime: {result[1]}, isUserBased: {result[2][0]}, numNeighbours: {result[2][1]}, thresh: {result[2][2]}, negCorrelations: {result[2][3]}\n")
    bestResultsFile.close()

isUserBasedOptions = [True, False]
neighbourNumOptions = [None, 2, 10, 50, 100]
threshOptions = [None, 0, 0.5, 0.8]
negCorrelationsOptions = [True, False]

startTests("assignment2-data.txt", isUserBasedOptions, neighbourNumOptions, threshOptions, negCorrelationsOptions)

#printPredictions("userBased/test.txt", True, 2, None)
#printPredictions("itemBased/test2.txt", False, 2, None)