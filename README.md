# ItemRecommenderAndReport
Experimental analysis on a historical movie review dataset. Determine which algorithm (user-based or item- based) and parameter combination (top-K neighbours or similarity threshold, and associated values) provide the best recommendation solution for the given dataset.

# Specifications
The main goal of the assignment will be to perform experimental analysis of the prediction accuracy achieved by the recommender system algorithms we have discussed in the course. The assignment page contains a text file of historical movie review data, which follows the same format as the data used in lab #8. You will be required to submit a short report (<10 pages) outlining the design of your implementation and analyzing/discussing your experimental results within the context of this dataset. Some questions you should aim to answer in your report include but are not limited to:

To generate data for the report, you are expected to use the ‘leave one out’ cross validation approach. This will allow you to compute the mean absolute error across the entire dataset for any single algorithm/parameter combination.
Repeating the experiments for this assignment will involve quite a bit of computation. It may be worth spending some time improving the runtime complexity of your implementation before running the experiments. Look for values you can precompute and reuse/modify to avoid excessive amounts of unnecessary computation. Start your experiments early so you have time to investigate the two algorithms and different parameters.

# Instructions
(No extra libraries required):
1. Cd into project directory
2. Run python3 ./assignment2.py
3. Review produced data in logs.txt, bestResults.txt, resultsByMae.txt, and resultsByRT.txt

Files:
 - assignment2.py - The code for the assignment.
 - README.txt - this .txt file containing instructions and files list.
 - logs.txt - the output of relevant parameter information in the order that they are executed by the program.
 - resultsByMae.txt - the output of relevant parameter information sorted from best-to-worst MAE.
 - resultsByRT.txt - the output of relevant parameter information sorted from best-to-worst runtimes.
 - bestResults.txt - the output of relevant parameter information sorted by two columns from best-to-worst runtimes and MAE. Practically the same as resultsByMae.txt.
 - ./userBased - a folder containing the input and expected output .txt files from previous labs on user-based recommendation. Original files are modified from -1 to indicate unreviewed items to 0. (For testing purposes)
 - ./itemBased - a folder containing the input and expected output .txt files from previous labs on item-based recommendation. Original files are modified from -1 to indicate unreviewed items to 0. (For testing purposes)

# Report
The structuring of the code of Assignment 2 primarily follows the structure and code of Labs 6 to 8. When first converting Lab 8 (Evaluating Recommender Systems) to Assignment 2, the following overall goals were identified:

1. Create separate functions for user and item similarities.
2. Create a neighbours function that finds user-based or item-based neighbours.
    1. Sort found neighbours by top-K or threshold-based filtering.
    2. For top-K filtering, add option to use absolute similarity/negative correlations.
3. Implement timers to keep track of execution time.
4. Run experiments comparing option combinations.

As with my previous implementation of Lab 8, the beginning of the program primarily has 5 key steps; 1. read the given .txt file, 2. calculate average user ratings, 3. calculate similarities between users/items, 4. generate a list of valid neighbours, 5. calculate predictions, 6. calculate MAE.

The readMatrixFile function takes the target .txt file's location as a parameter. It then returns the values for numUsers, numItems, usernames, itemNames, and ratings to be used by other functions.

Here, it is important to differentiate between usernames and itemNames, and userIndex and itemIndex. This is highlighted by the structuring of variables within the program. The usage of global variables was specifically avoided when possible. Therefore, when values need to be shared (such as with ratings arrays, similarities arrays, etc.) they are returned as values by functions or passed as parameters. This has the added effect of not modifying input arrays, which is especially important when showcasing the original and output predictions, or when making calculations on the original ratings array. Storing average ratings and similarities as arrays also allows for hypothetically easier data manipulation in the future if new users or items are added.

Furthermore, the usernames or item names are not used in identifying specific users or items within arrays. For example, the user with username "1" does not correspond to the element at index 1 of the ratings array. Therefore, specific userIndexes and itemIndexes are created to consistently keep track and refer to specific users or items. These indexes are also used to retrieve their corresponding usernames or item names by returning the values of usernames\[userIndex\] or itemNames\[itemIndex\]. The userIndexToUsername, usernameToIndex, and itemIndexToName functions exist to retrieve names or indexes as required.

calculateAverageRatings is given a ratings array, numUsers, and numItems. It then returns the calculated average user ratings, where the element at averageUserRatings\[userIndex\] refers to the average user rating for the specific user of userIndex.

All similarities are calculated through the calculateAllSimilarities function which among other parameters, takes an isUserBased boolean, a ratings array, and an averageUserRatings array. Depending on if isUserBased is True, it loops through either the items or users to calculate each individual similarity by calling calculateUserSimilarity or calculateItemSimilarity. After calculating, the function returns an array of calculated similarities with similarities\[i\]\[j\] referring to the similarity between item/user i and item/user j.

The getNeighbours function generates a list of either user or item neighbours. It also takes the optional parameters numNeighbours, referring to top-K neighbour selection, and thresh for threshold-based neighbour section. Its last optional parameter is negCorrelations which is a boolean indicating if negative correlations should be included.

The getNeighbours function first creates a 2D array called neighbours where neighbours\[i\] refers to the neighbours of user/item i. The array stored within neighbours\[i\] then contains tuples which store the similarities between user i and the neighbour (the absolute similarities if negCorrelation is True), as well as the neighbour's index for future purposes. The array of tuples is then sorted by similarities using Python's built-in sort function.

If the numNeighbours parameter is set, then it slices the array at neighbours\[i\] so that the array of tuples is of numNeighbours length. If the thresh parameter is set, then it only adds neighbours which have a similarity higher than thresh. If neither numNeighbours nor thresh are set, then it adds all found neighbours. Once all neighbours are found for all items or users, then it returns the array of neighbours.

calculatePredictions takes all of the previously calculated/returned arrays and uses it to generate predictions where the rating is 0. First it copies the contents of the ratings array into a separate output array. This keeps the original ratings array intact and prevents modifications to it. It then loops through the entire ratings array and calls calculatePrediction to calculate a single prediction for a given userIndex and itemIndex. calculatePrediction returns a float rounded to 2 decimal points, this result is then saved to the output array.

calculatePrediction works by looping through the given neighbours array for a specific user or item. It uses either the item-based prediction formula or user-based prediction formula depending on if the isUserBased parameter is True or False. If no valid neighbours are found or if the calculated denominator is 0 (which is invalid), it then returns the user's average user rating.

The Mean Average Error (MAE) is calculated through "leave-one-out" cross-validation. This takes the original ratings array before predictions are calculated. Firstly, it loops through each element of the ratings array that is non-zero. It then creates a temporary variable to store the original rating and then temporarily sets the rating in the ratings array to 0. This effectively simulates not having a rating so that when a rating is calculated through the program, it can be compared with to the original ground-truth rating. The MAE is calculated as the sum of the absolute of the original ratings minus the predicted ratings, divided by the number of predictions made.

There is also a debug function used for testing code which only prints if the DEBUG global constant is True.

**Optimizations**

Care was taken to ensure optimal modularity of functions and the reuse of code.

For example, all calculated similarities are stored in a 2D array, similarities\[a\]\[b\]. similarities\[a\]\[b\] represents the similarity between user/item A, and user/item B. As similarities\[a\]\[b\] should have the same value as similarities\[b\]\[a\], it only needs to be calculated once. Therefore, the calculateAllSimilarities function loops through all items once, with a nested loop that only loops through user/item B's that have not already been accessed for a similarity calculation. Then once similarities\[a\]\[b\] is calculated, it is copied to similarities\[b\]\[a\] without having to loop to it or having to do a second calculation.

A similar idea of not doing any redundant calculations is included in the calculateAverageRatings function. Here, for the denominator, instead of looping through the ratings and only adding ratings that are non-zero, the denominator is set to the number of items. This way, only one for loop is needed (instead of looping to find unreviewed elements and then looping again to add them to the denominator) to subtract it from the denominator if it is non-zero, or to add it to the numerator if it is not.

Furthermore, functions such as calculateAllSimilarities and getNeighbours were specifically modified for generality and to easily use them for item-based or user-based recommendations when the isUserBased parameter is passed as true. calculateAllSimilarities makes calls to either calculateItemSimilarity or calculateUserSimilarity, which feature different mathematical formulas for similarities. getNeighbours is able to use the same code within the same line to populate the list for either user-based or item-based neighbours. It does this by using list comprehensions and by using general firstIndex and secondIndex up to the range of numUsers or numItems in the for loop.

Instead of hard-coding test cases into the program, a function was created to programmatically loop through and test all valid combinations of options and parameters (more information is provided within the Experimental Methodology section). Regarding test cases, invalid cases such as numNeighbours and thresh are both set are skipped. This drops the total number of test cases from 80 possible combinations to 32 (for the experiment's specific option parameters). This greatly reduced the runtime of tests by reducing redundant operations.

Finally, the program makes heavy usage of "Pythonisms" or language features unique to Python to either increase performance or to make the code more readable. For example, list comprehensions are used multiple times to propagate lists in a single line instead of using a comparable for loop. Also, instead of manually sorting through neighbours, lists are sorted with the built-in sort method which runs at O(n log n) time complexity.

**Experimental Methodology**

For the purposes of this experiment, "top-K" is labelled as "numNeighbours" where its value is equal to the top-K best neighbours. The two terms are synonymous.

In cases where numNeighbours and thresh are both 'None', then all neighbours are added.

Testing is programmed into assignment2.py. The startTests function takes the following parameters (as well as their currently set values for this experiment):

- txtlocation - a string indicating the location of the target input .txt file from the current directory. I.e. "assignment2-data.txt"
- isUserBasedOptions - an array of possible values for isUserBased. I.e. \[True, False\]
- neighbourNumOptions - an array of possible values for neighbourNum. I.e. \[None, 2, 10, 50, 100\]
- threshOptions - an array of possible values for thresh. I.e. \[None, 0, 0.5, 0.8\]
- negCorrelationOptions - an array of possible values for negCorrelations. I.e. \[True, False\]

With these arrays of possible option values, the possible combinations of options are looped through by calling the printPredictions function. The printPredictions function has been repurposed to track the CPU-runtime (as opposed to the wall time) between the reading of the matrix file, calculation of average ratings and similarities, the picking of neighbours, the calculating of predictions, and the calculating and printing of the MAE.

Wall time measures the actual time elapsed between timer start and timer end (and is affected by other factors such as I/O, etc.), while CPU-runtime only measures the time elapsed to execute the code. By measuring the execution time for all the previous processes (including to calculatePredictions), a wider view of the "bigger picture" is granted on how these parameters affect all aspects of the program.

At the end of every test iteration for each option combination, the results including MAE, runtime, and options are added to a results array and saved in the order of execution in the "logs.txt" file. After all test iterations are done, these results are saved to "resultsByMae.txt" (which orders results from best-to-worst MAE) and "resultsByRT.txt" (which orders results from best-to-worst runtime). A third sorted list, "bestResults.txt" is also created which sorts based on the combination of the two columns of MAE and RT, although the results are almost identical to "resultsByMae.txt".

Testing was ran multiple times to ensure overall consistency between results.

**Experimental Results**

Below are the results of the automated testing separated into two tables sorted by Mean Absolute Error (MAE) and by runtime measured in seconds. The top 5 and lowest 5 results are displayed for comparison.

**By MAE** (Lower is better)

| **Position** | **MAE** | **Runtime** | **isUserBased** | **numNeighbours** | **thresh** | **negCorrelations** |
| --- | --- | --- | --- | --- | --- | --- |
| 1   | 0.328 | 32.257 | False | None | 0.5 | False |
| 2   | 0.332 | 29.561 | False | None | 0.8 | False |
| 3   | 0.362 | 38.455 | False | None | 0   | False |
| 4   | 0.362 | 37.940 | False | None | None | False |
| 5   | 0.383 | 27.582 | False | 100 | None | False |
| 6   | 0.444 | 25.982 | False | 50  | None | False |
| 7   | 0.566 | 24.587 | False | 10  | None | False |
| 8   | 0.618 | 23.779 | False | 2   | None | False |
| 9   | 0.633 | 24.366 | False | 2   | None | True |
| 10  | 0.658 | 24.254 | False | 10  | None | True |
| 11  | 0.659 | 2.287 | True | None | 0   | False |
| 12  | 0.659 | 2.230 | True | None | None | False |
| 13  | 0.659 | 2.390 | True | 100 | None | False |
| 14  | 0.666 | 3.020 | True | None | 0   | True |
| 15  | 0.666 | 4.696 | True | None | None | True |
| 16  | 0.671 | 3.832 | True | 100 | None | True |
| 17  | 0.686 | 2.197 | True | 50  | None | False |
| 18  | 0.690 | 1.883 | True | None | 0.5 | False |
| 19  | 0.698 | 2.418 | True | None | 0.5 | True |
| 20  | 0.718 | 54.238 | False | None | 0   | True |
| 21  | 0.718 | 48.124 | False | None | None | True |
| 22  | 0.723 | 39.299 | False | None | 0.5 | True |
| 23  | 0.733 | 0.623 | True | 2   | None | False |
| 24  | 0.735 | 1.588 | True | None | 0.8 | False |
| 25  | 0.738 | 0.620 | True | 2   | None | True |
| 26  | 0.738 | 25.893 | False | 50  | None | True |
| 27  | 0.742 | 2.391 | True | 50  | None | True |
| 28  | 0.744 | 2.171 | True | None | 0.8 | True |
| 29  | 0.748 | 33.048 | False | None | 0.8 | True |
| 30  | 0.760 | 1.022 | True | 10  | None | False |
| 31  | 0.762 | 26.806 | False | 100 | None | True |
| 32  | 0.764 | 0.997 | True | 10  | None | True |

**By Runtime** (Lower is better)

| **Position** | **MAE** | **Runtime** | **isUserBased** | **numNeighbours** | **thresh** | **negCorrelations** |
| --- | --- | --- | --- | --- | --- | --- |
| 1   | 0.738 | 0.620 | True | 2   | None | True |
| 2   | 0.733 | 0.623 | True | 2   | None | False |
| 3   | 0.764 | 0.997 | True | 10  | None | True |
| 4   | 0.760 | 1.022 | True | 10  | None | False |
| 5   | 0.735 | 1.588 | True | None | 0.8 | False |
| 6   | 0.690 | 1.883 | True | None | 0.5 | False |
| 7   | 0.744 | 2.171 | True | None | 0.8 | True |
| 8   | 0.686 | 2.197 | True | 50  | None | False |
| 9   | 0.659 | 2.230 | True | None | None | False |
| 10  | 0.659 | 2.287 | True | None | 0   | False |
| 11  | 0.659 | 2.390 | True | 100 | None | False |
| 12  | 0.742 | 2.391 | True | 50  | None | True |
| 13  | 0.698 | 2.418 | True | None | 0.5 | True |
| 14  | 0.666 | 3.020 | True | None | 0   | True |
| 15  | 0.671 | 3.832 | True | 100 | None | True |
| 16  | 0.666 | 4.696 | True | None | None | True |
| 17  | 0.618 | 23.779 | False | 2   | None | False |
| 18  | 0.658 | 24.254 | False | 10  | None | True |
| 19  | 0.633 | 24.366 | False | 2   | None | True |
| 20  | 0.566 | 24.587 | False | 10  | None | False |
| 21  | 0.738 | 25.893 | False | 50  | None | True |
| 22  | 0.444 | 25.982 | False | 50  | None | False |
| 23  | 0.762 | 26.806 | False | 100 | None | True |
| 24  | 0.383 | 27.582 | False | 100 | None | False |
| 25  | 0.332 | 29.561 | False | None | 0.8 | False |
| 26  | 0.328 | 32.257 | False | None | 0.5 | False |
| 27  | 0.748 | 33.048 | False | None | 0.8 | True |
| 28  | 0.362 | 37.940 | False | None | None | False |
| 29  | 0.362 | 38.455 | False | None | 0   | False |
| 30  | 0.723 | 39.299 | False | None | 0.5 | True |
| 31  | 0.718 | 48.124 | False | None | None | True |
| 32  | 0.718 | 54.238 | False | None | 0   | True |

**Experiment Conclusions**

For this specific dataset, there are 150 users and 1067 items. Because of this, from a purely runtime perspective, the user-based recommendations would be quicker than the item-based approach. This is simply because the actual work of calculating user similarities and finding neighbours is less because there are less users than items.

As for comparing actual accuracy between the two approaches, the item-based recommendations were consistently higher (although consistently slower). This could be due to the higher number of items simply providing greater opportunities to find similar item neighbours, large differences between users that make user-based recommendations inaccurate, or a large number of consistent item data.

The threshold-based neighbour selection approach is also consistently more accurate than the top-K approach. This is because the top-K approach simply returns a specific number of neighbours, regardless of actual similarity. The threshold-based approach sets a baseline similarity needed to ensure that neighbours are relevant. The second-most accurate approach is when all found neighbours are added (when numNeighbours and thresh are both set to None), although realistically this may be too computationally heavy to perform at scale. When top-K is used, a larger number of neighbours is generally better, with accuracy decreasing as the number of neighbours decreases. This is predictable as the prediction system takes into account less and less data.

Theoretically, the inclusion of negative correlations (top-K based on absolute value of correlation) could improve results if it is important to take into account how dissimilar a user or item is. However, on this specific dataset it does not seem to consistently improve the results. This could be due to how negative correlation was accounted for within this implementation of the assignment. Greater research may be needed to factor dislikes into recommendation systems.

In conclusion, the best combination of approaches and parameters for this specific dataset (and when MAE is prioritized) is an item-based, threshold approach without negative correlations.

**Applying Findings to Movie Recommendation System**

With a movie recommendation system, an item-based approach may be best. From a runtime perspective, it should be consistently faster, assuming that the number of users is higher than the number of movies. Within a large movie recommendation database where the number of users could be tens of millions higher than the number of actual movies, performance would be an incredibly important consideration.

Furthermore, from a movie recommendation perspective, the similarity and comparisons between movies would be more important than the similarities between users. Ideally the recommender system should recommend movies that are similar to movies that a specific user had already liked. This contrasts with the user-based recommendation approach, which finds similar users. Just because a user has liked similar movies in the past, it does not take into account outlying situations such as a neighbour user having a diverse movie taste, irregular movie reviewing patterns, or changing movie tastes.

As seen from the data, threshold-based neighbour selection returns consistently better results. This is especially important as a top-K approach simply requires returning a certain number of sorted neighbours, which does not consider the actual similarity of an item, but its relative similarity in comparison to other possible neighbours. A threshold-based approach ensures that only movies that surpass a given relevance threshold are considered.

Judging from the results of the data, negative correlations should not be considered. Its effect on accuracy is inconclusive or minimal at best. This could be an issue of implementation, but the idea of considering movies that are dissimilar could help improve accuracy if the system takes into account what a user dislikes when it provides a recommendations. It could then calculate similarities and then offer recommendations that have a negative correlation with movies that the user already dislikes.

In a real-world prediction system, various values can be precomputed and modified as the data changes or as otherwise needed. For example, in this assignment's current implementation of users, items, and ratings, it would be easy to precompute all average user ratings. New average ratings should only be calculated as users review new ratings. The addition of new users should not affect the average ratings of other users and can therefore be appended to the average user rating array.

**Impact of More/Less Reviews**

There are a few impacts that users with more or less reviews would have on an item-based, threshold recommendation approach (as defined in experiment conclusions).

Firstly, a user with more reviews would generally have a net positive impact on the accuracy of the recommendation system. More user reviews allow the calculation of more accurate user review averages that better reflect a user's preferences and rating history. In a user-based recommendation system, providing more review data would also allow for better finding of related neighbours. While in an item-based approach, more reviews would provide more data for the item similarities calculation and the finding of neighbours (at the cost of some performance). More reviews also prevent huge swings in calculations such as average user ratings and similarities.

Users with few or fewer reviews would generally have a net negative impact on the accuracy of the recommendation system. Firstly, the lack of data relates to the sparsity problem which makes it harder to find accurate and relevant neighbours for a given user or item. Less reviews also would make the average user ratings more prone to fluctuation and therefore more inaccurate. Finally, this also relates to the cold start problem as the initial lack of reviews makes it generally harder to determine user preferences, which in turn makes it more difficult to provide relevant recommendations.
