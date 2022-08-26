import pandas as pd
from itertools import product
import helper as h
import specialFunc as special
import ast
import streamlit as st
from collections import Counter
import pickle

trajectories_oneDay = pd.read_csv('data/trajectories_types_one_day.csv')
trajectories_fullVist = pd.read_csv('data/trajectories_types_full_visit.csv')
pois = pd.read_csv('data/accessPoints_lat_lon.csv')
pois_full = pd.read_csv('data/accessPoints_lat_lon_full.csv')
pois_one = pd.read_csv('data/accessPoints_lat_lon_one.csv')
file_to_read = open("data/trajectories_dictionary.pkl", "rb")
trajectories_dictionary = pickle.load(file_to_read)
file_to_read_2 = open("data/trajectories_dictionary_full.pkl", "rb")
trajectories_dictionary_full = pickle.load(file_to_read_2)
lookUpPois_oneDay = pd.read_csv('data/pois_outTransFreqOneDay.csv')
lookUpPois_fullVisit = pd.read_csv('data/pois_outTransFreqFullVisit.csv')
lookUpTransitions_oneDay = pd.read_csv('data/lookUpTransitions_oneDay.csv')
lookUpTransitions_full = pd.read_csv('data/lookUpTransitions_fullVisit.csv')


def checkPoiTag(listToAdd, tagList, row):
    name = row['name']
    idPoi = row['id']
    tags_first = row['tags']
    tags = ast.literal_eval(tags_first)
    lat = row['lat']
    lon = row['long']
    mostSimilar = row['mostSimilar']
    type = row['type']
    top3InTransitions = row['top3InTransitions']
    top3OutTransitions = row['top3OutTransitions']
    outTransFrequency = row['outTransFrequency']
    check = any(item in tagList for item in tags)
    if check:
        listToAdd.append(
            [name, idPoi, lat, lon, type, tags_first, mostSimilar, top3InTransitions, top3OutTransitions, outTransFrequency])


def filterPOIsOnTags(tagsSelection, poiData, listToAdd):
    """
    :return: new pois-dataframe with cols: ['name', 'id', 'tags', 'lat', 'lon','type', 'rank', 'mostSimilar'] containing only POIs that satisfy
    the tag selection of the user.
    """
    #tagListNumbered = special.translateTagList(tagsSelection)
    f = poiData.apply(lambda row: checkPoiTag(listToAdd, tagsSelection, row), axis=1)
    return pd.DataFrame(listToAdd, columns=['name', 'id', 'lat', 'long', 'type', 'tags', 'mostSimilar',
                                            'top3InTransitions', 'top3OutTransitions', 'outTransFrequency'])


# ******************************************************
# *                        MAIN                        *
# ******************************************************
def filterData(age, accommodation, seasons):
    trajectories = trajectories_oneDay if st.session_state.duration == 'one-day' else trajectories_fullVist

    # filtering trajectories according to user selection
    filtering = trajectories[(trajectories['season'].isin(seasons)) &
                             (trajectories['cardType'].isin(age)) &
                             (trajectories['distributionType'].isin(accommodation))]
    if filtering.empty:
        return None, None

    # creating a list of tuples (user, traj_number) of the filtered trajectories
    filteredTraj = filtering[['user_id', 'traj_n']].drop_duplicates()
    filteredTraj_tuples = [tuple(x) for x in filteredTraj.values]

    # transforming it to a filtered trajectory-dictionary : key = (user, traj); value = POI-transition tuples
    filtered_trajectory_dict = {key: trajectories_dictionary[key] for key in
                                filteredTraj_tuples} if st.session_state.duration == 'one-day' else {
        key: trajectories_dictionary_full[key] for key in filteredTraj_tuples}

    # flatten the dictionary to contain only the POI-transition tuples and remove the self-transitions
    tuples_list = list(filtered_trajectory_dict.values())
    tuples_flat_list = [item for sublist in tuples_list for item in sublist]
    cleaned_tuples = [t for t in tuples_flat_list if t[0] != t[1]]

    # count the transitions
    cnt = Counter(cleaned_tuples)

    # count the OutTransitions
    all_aids = filtering['accessId'].unique()
    for aid in filtering['accessId'].unique():
        outTrans = {k: v for k, v in cnt.items() if k[1] in all_aids}
    OutTransitionFrequency = Counter(k[1] for k in outTrans.keys())

    filteredAttractions = lookUpPois_oneDay if st.session_state.duration == 'one-day' else lookUpPois_fullVisit
    filteredAttractions['outTransFrequency'] = filteredAttractions.apply(lambda row: OutTransitionFrequency[row['id']],
                                                                         axis=1)

    filteredTransitions = lookUpTransitions_oneDay if st.session_state.duration == 'one-day' else lookUpTransitions_full
    filteredTransitions = [row for index, row in filteredTransitions.iterrows() if
                           (row['source_id'], row['dest_id']) in cleaned_tuples]
    filteredTransitions_df = pd.DataFrame(filteredTransitions)

    return filteredTransitions_df, filteredAttractions


def filterPOIs(tags):
    listToFilter = []
    return filterPOIsOnTags(tags, pois_one,
                                    listToFilter) if st.session_state.duration == 'one-day' else filterPOIsOnTags(tags,
                                                                                                                  pois_full,
                                                                                                                  listToFilter)
