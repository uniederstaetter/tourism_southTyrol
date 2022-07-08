import pandas as pd
from itertools import product
import helper as h
import specialFunc as special
import ast
import streamlit as st

trajectories_oneDay = pd.read_csv('data/trajectories_types_one_day.csv')
trajectories_fullVist = pd.read_csv('data/trajectories_types_full_visit.csv')
pois = pd.read_csv('data/accessPoints_lat_lon.csv')


#######################################################
#                      FILTERING                      #
#######################################################

def filterOnSelection(selection, trajectories, attr):
    """
    :return: the filtered trajectories according to the passed selection criterion
    """
    boolean_series = trajectories.accessId.isin(selection) if attr == 'accessId' else trajectories.cardType.isin(
        selection) if attr == 'cardType' else trajectories.distributionType.isin(
        selection) if attr == 'distributionType' else trajectories.season.isin(selection)
    return trajectories[boolean_series]


def checkPoiTag(listToAdd, tagSelection, row):
    name = row['name']
    idPoi = row['id']
    tags = row['tags']
    tags = ast.literal_eval(tags)
    lat = row['lat']
    lon = row['long']
    typePoi = row['type']
    rank = row['rank']
    mostSimilar = row['mostSimilar']
    check = any(elem in tagSelection for elem in tags)
    if check:
        listToAdd.append([name, idPoi, tags, lat, lon, typePoi, rank, mostSimilar])


def filterPOIsOnTags(tagsSelection, poiData, listToAdd):
    """
    :return: new pois-dataframe with cols: ['name', 'id', 'tags', 'lat', 'lon','type', 'rank', 'mostSimilar'] containing only POIs that satisfy
    the tag selection of the user.
    """
    #tagListNumbered = special.translateTagList(tagsSelection)
    f = poiData.apply(lambda row: checkPoiTag(listToAdd, tagsSelection, row), axis=1)
    return pd.DataFrame(listToAdd, columns=['name', 'id', 'tags', 'lat', 'long', 'type', 'rank', 'mostSimilar'])


#######################################################
#                     FREQUENCIES                     #
#######################################################

def checkTransitionFrequency(current_row, prev_attraction, prev_step, combinationAttr):
    current_step = current_row['step']
    currentAccessId = current_row['accessId']
    current_attraction = pois.loc[pois['id'] == currentAccessId, 'name'].item()
    if prev_step == current_step - 1:  # current step is direct successor step
        counter = combinationAttr.loc[(combinationAttr['source_attraction'] == prev_attraction) & (
                combinationAttr['dest_attraction'] == current_attraction), 'counter']
        newCounter = counter + 1
        combinationAttr.loc[(combinationAttr['source_attraction'] == prev_attraction) & (
                combinationAttr['dest_attraction'] == current_attraction), 'counter'] = newCounter


def transitionFrequencyTrajectory(group, combinationAttr):
    """
    :return: void. Increments the counter of transitions of the combination dataframe using the trajectory passed as group.
    """
    prev_accessId = group['accessId'].iloc[0]
    prev_attraction = pois.loc[pois['id'] == prev_accessId, 'name'].item()
    prev_step = group['step'].iloc[0]
    i = 0
    for index, row in group.iterrows():
        checkTransitionFrequency(row, prev_attraction, prev_step, combinationAttr)
        try:
            prev_accessId = group['accessId'].iloc[i]
            prev_attraction = pois.loc[pois['id'] == prev_accessId, 'name'].item()
            prev_step = group['step'].iloc[i]
            i += 1
        except IndexError:
            break


def checkOutFrequency(current_row, next_step, attractionFrequencies):
    current_step = current_row['step']
    currentAccessId = current_row['accessId']
    current_attraction = pois.loc[pois['id'] == currentAccessId, 'name'].item()
    if next_step == current_step + 1:
        counter = attractionFrequencies.loc[
            (attractionFrequencies['name'] == current_attraction), 'outTransFrequency']
        newCounter = counter + 1
        attractionFrequencies.loc[
            (attractionFrequencies['name'] == current_attraction), 'outTransFrequency'] = newCounter


def outFrequencyTrajectory(group, attractionFrequencies):
    """
    :return: void. increments for each trajectory (group) the counter counting the outTransitionFrequency stored in attractionFrequencies
    """
    i = 1
    for ix, row in group.iterrows():
        try:
            next_step = group['step'].iloc[i]  # try if next row exists
            checkOutFrequency(row, next_step, attractionFrequencies)
            i += 1
        except IndexError:
            break


# ******************************************************
# *                        MAIN                        *
# ******************************************************
def filterData(age, accommodation, tags, seasons):
    trajectories = trajectories_oneDay if st.session_state.duration == 'one-day' else trajectories_fullVist
    ########################################################################
    #                       FILTERING ON TAGS                              #
    ########################################################################
    listToFilter = []
    filteredPOIs = filterPOIsOnTags(tags, pois, listToFilter)
    idList = filteredPOIs['id'].tolist()
    filteredTraj_onPOIs = filterOnSelection(idList, trajectories, 'accessId')

    ########################################################################
    #                           FILTERING ON AGE                           #
    ########################################################################
    filteredTraj_onAge = filterOnSelection(age, filteredTraj_onPOIs, 'cardType')

    ########################################################################
    #                     FILTERING ON ACCOMMODATION                       #
    ########################################################################
    if not filteredTraj_onAge.empty:
        filteredTraj_onAccom = filterOnSelection(accommodation, filteredTraj_onAge, 'distributionType')
    else:
        return None, None
    ########################################################################
    #                          FILTERING ON SEASONS                        #
    ########################################################################
    if not filteredTraj_onAccom.empty:
        trajectories_withSeasons = special.applySeasons(filteredTraj_onAccom)
        filteredTraj_onSeasons = filterOnSelection(seasons, trajectories_withSeasons, 'season')
    else:
        return None, None
    if filteredTraj_onSeasons.empty:
        return None, None

    filteredTrajectories = filteredTraj_onSeasons
    grouped = filteredTrajectories.groupby(["user_id", "traj_n"])
    combinations = (list(tup) for tup in product(pois['name'], pois['name']))
    comb_attr = h.makeCombinationDf(combinations)
    g = grouped.apply(lambda group: transitionFrequencyTrajectory(group, comb_attr))
    not_zero_transitions = comb_attr[comb_attr['counter'] > 0]
    if not_zero_transitions.empty:
        return None, None

    coordsTransitionList = []
    n = not_zero_transitions.apply(lambda row: h.findLatLonCoords(row, coordsTransitionList, pois), axis=1)
    nonZeroFilteredTransition = pd.DataFrame(coordsTransitionList,
                                             columns=['source_attraction', 'src_lat', 'src_lon', 'dest_attraction',
                                                      'dest_lat', 'dest_lon', 'counter'])

    attractionFrequencies = pois
    attractionFrequencies['outTransFrequency'] = 0
    g = grouped.apply(lambda group: outFrequencyTrajectory(group, attractionFrequencies))
    attractionFrequencies = attractionFrequencies[
        ['name', 'id', 'type', 'lat', 'long',  'tags', 'rank', 'mostSimilar', 'outTransFrequency']]
    filteredAttractionFrequencies = attractionFrequencies[attractionFrequencies['outTransFrequency'] > 0]

    return nonZeroFilteredTransition, filteredAttractionFrequencies
